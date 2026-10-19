#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能端口冲突检测与推荐脚本 (跨平台: Linux / WSL / Windows)
支持:
1. 底层 Socket 实际绑定测试 (探测端口是否真能被监听)
2. 扫描正在运行的 Docker 容器端口映射与 Compose 项目路径溯源
3. 进程级占用信息深度溯源 (PID / 进程名 / 启动命令行 / 项目路径 / 工作目录)
4. 生成对准该占用实例的一键停机命令 (kill_command)
5. 冲突时自动向上探测并推荐可用的连续空闲端口
"""

import sys
import socket
import subprocess
import argparse
import json
import re
import os

def is_socket_free(port: int, host: str = "0.0.0.0") -> bool:
    """尝试以 0.0.0.0 实际 bind 端口，检验操作系统层是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False

def get_docker_occupied_ports() -> dict:
    """检查正在运行的 Docker 容器占用的宿主机端口，并尝试溯源其所属项目路径"""
    occupied = {}
    try:
        res = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=3
        )
        if res.returncode == 0:
            for line in res.stdout.strip().splitlines():
                if not line.strip():
                    continue
                parts = line.split("\t")
                container_name = parts[0]
                ports_str = parts[1] if len(parts) > 1 else ""
                
                # 匹配如 0.0.0.0:8080->8000/tcp 或 :::8080->8000/tcp
                found_ports = re.findall(r"(?:0\.0\.0\.0|:::|\[::\]):(\d+)->", ports_str)
                if found_ports:
                    project_info = get_docker_project_path(container_name)
                    desc = f"Docker 容器 [{container_name}]"
                    if project_info:
                        desc += f" (项目路径: {project_info})"
                    for p in found_ports:
                        occupied[int(p)] = {
                            "desc": desc,
                            "type": "docker",
                            "name": container_name,
                            "kill_command": f"docker stop {container_name} && docker rm {container_name}"
                        }
    except Exception:
        pass
    return occupied

def get_docker_project_path(container_name: str) -> str:
    """从 Docker 容器中提取 compose 项目路径或主工作目录"""
    try:
        res = subprocess.run(
            ["docker", "inspect", container_name, "--format", "{{json .Config.Labels}}"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if res.returncode == 0 and res.stdout.strip():
            labels = json.loads(res.stdout.strip())
            working_dir = labels.get("com.docker.compose.project.working_dir")
            project_name = labels.get("com.docker.compose.project")
            if working_dir:
                return working_dir
            if project_name:
                return f"Compose项目: {project_name}"
    except Exception:
        pass
    return ""

def get_process_details_linux(pid: int) -> dict:
    """在 Linux/WSL 下通过 /proc/{pid} 提取进程工作目录与命令行"""
    details = {"name": "", "path": "", "cmdline": ""}
    proc_dir = f"/proc/{pid}"
    if not os.path.exists(proc_dir):
        return details

    try:
        cwd = os.readlink(os.path.join(proc_dir, "cwd"))
        details["path"] = cwd
    except Exception:
        pass

    try:
        with open(os.path.join(proc_dir, "cmdline"), "rb") as f:
            cmdline = f.read().decode("utf-8", "ignore").replace("\x00", " ").strip()
            details["cmdline"] = cmdline
    except Exception:
        pass

    try:
        with open(os.path.join(proc_dir, "comm"), "r", encoding="utf-8", errors="ignore") as f:
            details["name"] = f.read().strip()
    except Exception:
        pass

    return details

def get_process_details_windows(pid: int) -> dict:
    """在 Windows 下通过 PowerShell WMI 提取进程名称、执行文件与命令行"""
    cmd = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Get-CimInstance Win32_Process -Filter 'ProcessId = {pid}' | Select-Object -Property Name,ExecutablePath,CommandLine | ConvertTo-Json"
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if res.returncode == 0 and res.stdout.strip():
            raw = res.stdout.strip()
            idx = raw.find("{")
            if idx != -1:
                data = json.loads(raw[idx:])
                return {
                    "name": data.get("Name") or "",
                    "exe": data.get("ExecutablePath") or "",
                    "cmdline": data.get("CommandLine") or ""
                }
    except Exception:
        pass
    return {"name": "", "exe": "", "cmdline": ""}

def get_process_info_for_port(port: int) -> dict:
    """尝试获取占用端口的进程信息与项目路径 (适配 Linux/WSL/Windows)"""
    if sys.platform != "win32":
        pid = None
        cmd_name = ""
        try:
            res = subprocess.run(
                ["ss", "-tulpn", f"sport = :{port}"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if res.returncode == 0 and str(port) in res.stdout:
                match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', res.stdout)
                if match:
                    cmd_name = match.group(1)
                    pid = int(match.group(2))
        except Exception:
            pass

        if not pid:
            try:
                res = subprocess.run(
                    ["lsof", "-i", f":{port}", "-sTCP:LISTEN"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if res.returncode == 0:
                    lines = res.stdout.strip().splitlines()
                    if len(lines) > 1:
                        parts = lines[1].split()
                        cmd_name = parts[0]
                        pid = int(parts[1])
            except Exception:
                pass

        if pid:
            details = get_process_details_linux(pid)
            name = details["name"] or cmd_name or "未知进程"
            loc = details["path"] or details["cmdline"]
            desc = f"系统进程 [{name} (PID: {pid})]"
            if loc:
                desc += f" (项目路径: {loc})"
            return {
                "desc": desc,
                "type": "process",
                "pid": pid,
                "kill_command": f"kill -15 {pid} (或 kill -9 {pid})"
            }

        return {
            "desc": "系统占用未知进程",
            "type": "unknown",
            "pid": None,
            "kill_command": ""
        }

    else:
        pid = None
        try:
            res = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=3
            )
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if f":{port} " in line and "LISTENING" in line:
                        parts = line.strip().split()
                        pid = int(parts[-1])
                        break
        except Exception:
            pass

        if pid:
            details = get_process_details_windows(pid)
            name = details.get("name") or "未知进程"
            cmdline = details.get("cmdline") or ""
            exe = details.get("exe") or ""

            project_loc = cmdline if cmdline else exe
            desc = f"Windows 进程 [{name} (PID: {pid})]"
            if project_loc:
                if len(project_loc) > 100:
                    project_loc = project_loc[:97] + "..."
                desc += f" (位置/命令: {project_loc})"

            return {
                "desc": desc,
                "type": "process",
                "pid": pid,
                "kill_command": f"Stop-Process -Id {pid} -Force"
            }

    return {
        "desc": "系统占用未知进程",
        "type": "unknown",
        "pid": None,
        "kill_command": ""
    }

def check_single_port(port: int, docker_ports: dict) -> dict:
    """综合检测单端口占用状态"""
    if port in docker_ports:
        item = docker_ports[port]
        return {
            "free": False,
            "port": port,
            "occupant": item["desc"],
            "kill_command": item["kill_command"]
        }
    
    if not is_socket_free(port):
        item = get_process_info_for_port(port)
        return {
            "free": False,
            "port": port,
            "occupant": item["desc"],
            "kill_command": item["kill_command"]
        }
    
    return {
        "free": True,
        "port": port,
        "occupant": None,
        "kill_command": ""
    }

def find_suggested_ports(start_port: int, count: int = 3, docker_ports: dict = None) -> list:
    """从 start_port + 1 开始向上寻找指定数量的空闲端口"""
    if docker_ports is None:
        docker_ports = get_docker_occupied_ports()
    
    suggested = []
    candidate = start_port + 1
    while len(suggested) < count and candidate < start_port + 200:
        res = check_single_port(candidate, docker_ports)
        if res["free"]:
            suggested.append(candidate)
        candidate += 1
    return suggested

def main():
    parser = argparse.ArgumentParser(description="检测端口是否占用，并提供深度溯源与智能推荐")
    parser.add_argument("--port", "-p", type=int, required=True, help="需要检测的端口号")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出结果")
    parser.add_argument("--suggest-count", type=int, default=3, help="冲突时推荐的可用端口数量")
    args = parser.parse_args()

    docker_ports = get_docker_occupied_ports()
    check_result = check_single_port(args.port, docker_ports)

    output_data = {
        "port": args.port,
        "is_free": check_result["free"],
        "occupant": check_result["occupant"],
        "kill_command": check_result["kill_command"],
        "suggestions": []
    }

    if not check_result["free"]:
        output_data["suggestions"] = find_suggested_ports(args.port, args.suggest_count, docker_ports)

    if args.json:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    else:
        if output_data["is_free"]:
            print(f"[OK] 端口 {args.port} 完全空闲可用！")
        else:
            sug_str = ", ".join(str(p) for p in output_data["suggestions"])
            print(f"[CONFLICT] 警告：端口 {args.port} 已被占用！")
            print(f"  └─ 占用者与位置: {output_data['occupant']}")
            if output_data["kill_command"]:
                print(f"  └─ 释放命令: {output_data['kill_command']}")
            if output_data["suggestions"]:
                print(f"  └─ 建议改用相邻空闲端口: {sug_str}")
            else:
                print("  └─ 未能在附近范围内找到可用端口，请手动指定其他大端口。")

    sys.exit(0 if output_data["is_free"] else 1)

if __name__ == "__main__":
    main()
