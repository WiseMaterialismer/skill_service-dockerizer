# 1. 基础镜像：Debian-slim 体积小且包管理器完善
FROM python:3.11-slim

# 2. 核心系统环境变量：实时输出日志、禁用 pyc、设置中国时区与 UTF-8
ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 3. 安装时区支持与必要的基础系统库
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 依赖层缓存：仅 requirements.txt 变更时才重新安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 复制全部业务代码到容器
COPY . .

# 6. 默认暴露端口（声明性质，具体在 compose 中映射）
EXPOSE 8000

# 7. 默认启动命令（开发环境可在 compose 中被 uvicorn --reload 等覆盖）
CMD ["python", "main.py"]
