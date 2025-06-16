
# CIF/XYZ 文件格式转换器 API

这是一个基于 FastAPI 构建的轻量级 Web 服务，支持晶体学信息文件（`.cif`）与 XYZ 坐标文件（`.xyz`）的双向转换。

## ✨ 功能特色

- **自动格式识别**：自动判断上传文件的格式（`.cif` 或 `.xyz`）。
- **双向转换**：
  - CIF → XYZ
  - XYZ → CIF
- **即时下载**：转换后直接返回文件，方便保存。
- **一键部署**：支持 Docker 和 Docker Compose，快速搭建，无需手动配置环境。
- **美观日志**：集成 `rich` 日志，输出清晰易读。

## ⚙️ 环境准备

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 快速启动

1. **获取代码**
   下载或克隆本项目，包括 `app/`、`Dockerfile`、`docker-compose.yml`、`requirements.txt` 等文件。

2. **构建并运行容器**
   在项目根目录执行：

   ```bash
   docker-compose up --build
   ```

   等待构建完成并看到服务已在 `http://0.0.0.0:8000` 运行即可。

3. **访问服务**
   默认在本机的 `8000` 端口提供服务。

## 🛠️ 使用方法

通过向 `/convert/` 端点发送 `POST` 请求上传文件。

- **接口**：`POST http://localhost:8000/convert/`
- **请求体**：`multipart/form-data`
- **参数**：
  - `file`：选择上传的 `.cif` 或 `.xyz` 文件

### `curl` 使用示例

**CIF 转换为 XYZ**：

```bash
curl -X POST -F "file=@/path/to/your/my_structure.cif" http://localhost:8000/convert/ -o converted.xyz
```

**XYZ 转换为 CIF**：

```bash
curl -X POST -F "file=@/path/to/your/atoms.xyz" http://localhost:8000/convert/ -o converted.cif
```
