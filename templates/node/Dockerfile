FROM node:20-slim

ENV TZ=Asia/Shanghai \
    LANG=C.UTF-8 \
    NODE_ENV=development

WORKDIR /app

# 安装基础库与配置国内 npm 镜像源加速
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && npm config set registry https://registry.npmmirror.com

# 依赖层缓存
COPY package*.json ./
RUN npm install

# 复制业务代码
COPY . .

EXPOSE 3000

CMD ["node", "src/index.js"]
