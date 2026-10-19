# 🐳 Service Dockerizer (服务容器化专家工作流)

<p align="center">
  <img src="https://img.shields.io/badge/Antigravity-Skill-blue.svg?style=flat-square" alt="Antigravity Skill" />
  <img src="https://img.shields.io/badge/Docker-Compose_V2-2496ED.svg?style=flat-square&logo=docker&logoColor=white" alt="Docker Compose" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20WSL2%20%7C%20Linux-green.svg?style=flat-square" alt="Platform Support" />
  <img src="https://img.shields.io/badge/License-MIT-orange.svg?style=flat-square" alt="License" />
</p>

专为 **Google Antigravity AI Agent** 打造的**通用服务标准化、交互式容器化专家技能（Skill）**。

无论是 Python (FastAPI/Flask/Django)、Node.js (Express/Next/Vite/Koa)、Go 还是静态 HTML/前端项目，`service-dockerizer` 都能通过标准的**八步引导流水线**，协助开发者无缝就位生产级 Docker 环境，拒绝传统容器化过程中常见的**权限被 root 锁死、端口冲突两眼一抹黑、开发不能热重载、历史数据丢失、宿主机与 WSL 路径错位乱放**等痛点。

---

## 🌟 核心设计原则

1. **四维分离**：
   - 📦 **代码归代码**（宿主机目录）
   - 🧱 **环境归镜像**（轻量 Dockerfile，分层缓存加速）
   - 🔑 **配置归环境变量**（标准 `.env` 参数化）
   - 💾 **数据归挂载卷**（外挂 `./data`，历史数据防丢）
2. **开发即改即生效**：通过源码卷实时映射与热重载命令，宿主机按 `Ctrl+S` 时容器内毫秒级更新，告别每次修改都重新 `docker build`。
3. **宿主权限无感对齐**：自动探测 Linux/WSL 用户 `UID:GID`（如 `1000:1000`）注入容器，根治容器生成的文件在宿主机被 `root` 锁死无法修改或删除的顽疾。
4. **端口深度溯源与建议**：端口冲突不仅报 PID，更深挖占用进程的名称、命令行、所属项目工作目录与专属释放命令（`kill_command`），并自动探测推荐可用空闲端口。
5. **部署位置防偏移**：跨平台感知 Windows 盘符与 WSL2 子系统路径，主动与开发者确认目标落盘位置，绝不擅自乱建文件夹。
6. **前置停机防撞车**：容器拉起前，主动排查本地正在裸跑的老进程与同名旧容器，保障控制权平滑交接。
7. **交付报告落盘沉淀**：容器化启动验证后，自动生成全景 Markdown 交付报告（`DOCKER_DEPLOY_REPORT.md`）保存在项目根目录下，并在会话中完整回显。

---

## 🔄 八步交互流水线 (Pipeline)

```text
[Step 1. 嗅探项目指纹与依赖检查]
       │
[Step 2. 部署目标位置确认与跨系统同步]
       │
[Step 3. 原项目运行状态排查与前置停机]
       │
[Step 4. 权限提取与 UID/GID 对齐]
       │
[Step 5. 端口智能探测与深度溯源]
       │
[Step 6. 生成标准四件套 (热重载+数据外挂)]
       │
[Step 7. 一键拉起验证与访问引导]
       │
[Step 8. 部署交付报告生成与落盘沉淀]
```

### 各阶段详细动作：

| 步骤 | 阶段名称 | 核心动作说明 |
| :--- | :--- | :--- |
| **Step 1** | **项目指纹与依赖检查** | 识别语言框架，排查 Python `requirements.txt` 完备性，自动探测 SQLite 数据库与上传附件防丢 |
| **Step 2** | **部署位置确认** | 感知 Windows 路径，主动询问集中部署至 WSL2（如 `/home/yh/self/project/{服务}`）还是原地容器化 |
| **Step 3** | **原项目排查与前置停机** | 检查本地正在裸跑的 Python/Node 进程及同名旧容器，征得同意后安全释放，避免双实例撞车 |
| **Step 4** | **权限提取与对齐** | 动态提取宿主机 UID/GID 注入配置，确保容器生成的日志与数据文件在宿主机拥有原生读写权限 |
| **Step 5** | **端口智能探测与溯源** | 运行 `check_port.py`，底层 Socket 校验 + Docker 端口映射 + 进程工作目录溯源，提供一键释放命令与备选端口 |
| **Step 6** | **生成标准四件套** | 基于内置模板生成参数化 `docker-compose.yml`、`.env`、优化缓存与国内源加速的 `Dockerfile` 及安全排除的 `.dockerignore` |
| **Step 7** | **一键启动与直达验证** | 协助执行 `docker compose up -d`，打印日志验证健康状态，输出浏览器直达访问链接与日常口诀 |
| **Step 8** | **交付报告生成与落盘** | 汇总项目拓扑、网络端点、环境变量及运维指令速查表，生成 `DOCKER_DEPLOY_REPORT.md` 存入项目根目录并回显 |

---

## 📂 项目结构

```text
skill_service-dockerizer/
├── SKILL.md                 # Antigravity 技能主定义文件（八步交互法完整执行指令）
├── README.md                # 技能详细文档与使用指南
├── LICENSE                  # MIT 开源协议
├── .gitignore               # Git 忽略文件
├── scripts/
│   └── check_port.py        # 跨平台端口智能检测、深度溯源与空闲推荐脚本
└── templates/               # 标准容器化模板库
    ├── python/              # Python (FastAPI/Flask) 标准模版 (热重载+数据卷外挂)
    │   ├── Dockerfile
    │   ├── docker-compose.yml
    │   ├── .env.example
    │   └── .dockerignore
    ├── node/                # Node.js 现代工程模版 (匿名卷防覆盖+npm run dev)
    │   ├── Dockerfile
    │   ├── docker-compose.yml
    │   ├── .env.example
    │   └── .dockerignore
    └── static/              # 纯前端/静态页面模版 (Nginx Alpine + SPA路由支持)
        ├── Dockerfile
        ├── docker-compose.yml
        ├── nginx.conf
        ├── .env.example
        └── .dockerignore
```

---

## 🚀 安装与在 Antigravity 中使用

### 1. 安装方式

#### 方式 A：作为全局技能（推荐）
直接克隆或复制到 Antigravity 全局技能配置目录：
```bash
# Windows PowerShell
git clone https://github.com/WiseMaterialismer/skill_service-dockerizer.git "$HOME\.gemini\config\skills\service-dockerizer"

# Linux / WSL
git clone https://github.com/WiseMaterialismer/skill_service-dockerizer.git ~/.gemini/config/skills/service-dockerizer
```

#### 方式 B：作为项目工作区技能
直接安装到当前代码仓库的 `.gemini/skills/` 目录下：
```bash
cd your-project
mkdir -p .gemini/skills
git clone https://github.com/WiseMaterialismer/skill_service-dockerizer.git .gemini/skills/service-dockerizer
```

### 2. 触发与使用

无需手动执行复杂命令，在 Antigravity 对话中直接用自然语言描述需求，Agent 会自动识别意图并激活该技能：

- *“帮我把当前这个 FastAPI 项目容器化并启动。”*
- *“这个 Node 项目需要部署到 Docker，还要能支持我本地热重载改代码。”*
- *“把这个静态网站用 Nginx 容器化运行。”*
- *“将当前服务容器化，并部署到我的 WSL 环境下。”*

---

## 🔍 独立工具：端口深度检测与溯源脚本 (`check_port.py`)

技能内附的 `scripts/check_port.py` 可在任何 Linux、WSL 或 Windows 终端中单独执行：

```bash
# 检测指定端口
python scripts/check_port.py --port 8000

# 以 JSON 格式输出详情（方便脚本或 Agent 解析）
python scripts/check_port.py --port 8000 --json
```

**示例输出（冲突深度溯源）：**
```json
{
  "port": 8000,
  "free": false,
  "occupant": "Python 进程 [python.exe] (PID: 14220, 路径: D:\\workspace\\old_service, 命令行: python app.py)",
  "kill_command": "Stop-Process -Id 14220 -Force",
  "suggestions": [8001, 8002, 8003]
}
```

---

## 📊 交付报告示例 (`DOCKER_DEPLOY_REPORT.md`)

容器化完成后，项目根目录会自动生成类似如下格式的运维交付报告：

```markdown
# 🚀 my-fastapi-app 容器化部署交付报告

- **生成时间**：2026-10-19 21:55:00
- **部署路径**：`/home/yh/self/project/my-fastapi-app`
- **运行状态**：运行中 (Up healthy)

---

## 一、 🌐 访问端点与网络拓扑
- **浏览器直达访问**：http://localhost:8000
- **宿主机暴露端口**：8000
- **容器内部端口**：8000
- **网络模式**：bridge

---

## 二、 ⚙️ 运行时身份与环境配置
- **容器名称**：my-fastapi-app
- **宿主权限对齐**：UID: 1000 / GID: 1000（杜绝 root 锁死）
- **环境配置文件**：.env

---

## 三、 📂 目录挂载与数据持久化拓扑
| 宿主机路径 | 容器内挂载点 | 模式/说明 |
| :--- | :--- | :--- |
| `./app` | `/app/app` | 源码热重载（改代码保存即刻生效） |
| `./data` | `/app/data` | 数据持久化外挂（数据安全防丢） |

---

## 四、 🛠️ 日常运维指令速查
| 运维场景 | 执行命令 |
| :--- | :--- |
| **查看实时日志** | `docker compose logs -f` |
| **引入新依赖重构** | `docker compose up -d --build` |
| **进入容器调试** | `docker compose exec app sh` |
| **停止容器** | `docker compose down` |
```

---

## ❓ 开发者常见疑问与避坑解答 (FAQ)

### Q1: 改了业务代码需要重新构建或部署容器吗？
> **答：完全不需要！**  
> `service-dockerizer` 核心坚持“开发即改即生效”原则：
> 1. **源码卷实时挂载**：本地代码目录（如 `./app` 或 `./`）实时双向挂载至容器内部，本地文件变动在操作系统内核层同步更新。
> 2. **进程热重载监听**：
>    - **Python**：启动命令注入了 `--reload` / `--debug`（如 `uvicorn app.main:app --reload`），保存文件后毫秒级重启 Worker。
>    - **Node.js**：采用 `npm run dev`（由 Vite、Next.js、Nodemon 原生提供 HMR 热更新）。
>    - **静态页面**：静态资源直接挂载进 Nginx，改完**直接刷新浏览器**即可生效。

---

### Q2: 什么时候才需要重新构建或重新部署容器？
> **答：只有底层运行环境、依赖或编排配置发生变动时才需要。**
> 
> | 变更场景 | 是否需重建 | 对应执行命令 |
> | :--- | :---: | :--- |
> | **日常改业务代码**（逻辑、页面、路由） | ❌ **不需要** | 本地 `Ctrl+S` 保存即刻自动生效 |
> | **引入新依赖**（修改了 `requirements.txt` 或 `package.json`） | ✅ **需要** | `docker compose up -d --build` |
> | **修改容器底层**（修改了 `Dockerfile`，如加装系统 apt 库） | ✅ **需要** | `docker compose up -d --build` |
> | **修改编排配置**（修改了 `docker-compose.yml` 端口或 `.env` 变量） | ✅ **需要** | `docker compose up -d` |

---

### Q3: 容器停止或被我误删除了，我的数据库和历史数据会丢吗？
> **答：绝对不会丢失！**  
> - 核心数据严格遵循**“数据归挂载卷”**原则，无论是 SQLite 数据库（`*.db` / `*.sqlite3`）还是文件上传目录（`uploads/`），统一外挂在宿主机的 `./data` 目录下。
> - 即使你执行了 `docker compose down` 甚至 `docker rm -f` 强制删除了容器，宿主机磁盘上的 `./data/` 目录依然毫发无损。下次重新启动容器时，数据会自动重新加载。

---

### Q4: 为什么在 WSL2 或 Linux 下，容器生成的文件不会被 root 权限锁死？
> **答：因为工作流自动完成了 UID/GID 宿主身份对齐。**  
> - 传统 Docker 容器默认以 `root` 用户运行，容器内创建的日志和 `./data` 文件在宿主机所有权全都是 `root:root`，导致用户在宿主机无法编辑甚至无法直接删除。
> - `service-dockerizer` 在 Step 4 会自动获取当前系统的原生用户身份（`id -u` / `id -g`，如 `1000:1000`），并将其写入 `.env` 与 `docker-compose.yml` 的 `user: "${UID:-1000}:${GID:-1000}"`。容器内部以你的原生宿主用户运行，文件权限天然一致。

---

### Q5: 端口发生冲突时，工具会不会擅自强杀我正在运行的其他项目？
> **答：绝不擅自越权！**  
> - 内置的 `scripts/check_port.py` 会进行深度进程溯源，不仅能找出冲突进程的 PID，更会深挖出该进程的**启动命令行、工作目录绝对路径以及属于哪个 Docker Compose 项目**。
> - 工具会以清晰的高亮格式把占用详情和一键释放命令展示给你，并**优先推荐附近可用的连续空闲端口**（如 `8001`、`8002`），决定权完全交由开发者自主选择。

---

### Q6: Node.js 本地开发时，`node_modules` 会不会因为卷挂载被冲掉或跨平台报错？
> **答：不会，模版内置了“匿名卷保护机制”。**  
> - 在 `docker-compose.yml` 中挂载宿主机源码时，配置了 `- /app/node_modules` 匿名卷保护。
> - 这样容器内 Linux 编译的原生二进制模块（如 esbuild、sharp 等）会被安全保存在独立卷中，不会被宿主机 Windows 端的 `node_modules` 覆盖冲掉，彻底解决跨平台架构报错的问题。

---

### Q7: Windows 与 WSL2 混用时，源码到底放在哪里运行效率最高？
> **答：强烈推荐放在 WSL2 的原生 Linux 文件系统下（如 `/home/yh/self/project/...`）！**  
> - 如果把代码放在 Windows 盘符（如 `I:\...` 或 `C:\...`）并在 WSL2 Docker 中挂载，文件 I/O 需要经过 `9P` 跨系统协议转换，性能会下降 3~5 倍，且文件修改事件有时无法正常触发热重载。
> - 本技能在 Step 2 会主动感知当前路径，如果检测到处于 Windows 路径，会主动询问并协助你集中同步至 WSL 目录中运行，保障毫秒级文件监控与高性能 I/O。

---

### Q8: 容器长期在后台运行，日志会不会把我的磁盘撑爆？
> **答：不会，所有模版标配了 Docker 官方日志轮转策略。**  
> 每个服务的 `docker-compose.yml` 中均默认配置了防炸盘限制：
> ```yaml
> logging:
>   driver: "json-file"
>   options:
>     max-size: "10m"
>     max-file: "3"
> ```
> 单个容器日志最大限制为 10MB，最多保留 3 份历史轮转，总占用严格锁死在 30MB 以内，安全无忧。

---

### Q9: 本地调通后，如果要上线到生产服务器（Production），如何平滑过渡？
> **答：只需极简微调两项配置即可直接用于生产：**
> 1. **移除源码卷挂载**：在生产部署的 compose 中移除宿主机代码的实时映射（如 `- ./app:/app/app`），直接使用 `Dockerfile` 打包阶段复制到镜像内部的不可变代码资产。
> 2. **关闭热重载参数**：将开发启动命令（如 `--reload` 或 `npm run dev`）调整为生产级多进程命令（如 `gunicorn -w 4 -k uvicorn.workers.UvicornWorker` 或 `npm start`）。

---

## 📄 开源许可证

本项目遵循 [MIT License](LICENSE) 开源协议。欢迎提交 Issue 与 Pull Request！

