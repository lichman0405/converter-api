
# CIF/XYZ File Format Converter API

A lightweight FastAPI-based web service for bidirectional conversion between Crystallographic Information Files (`.cif`) and XYZ coordinate files (`.xyz`).

## ✨ Key Features

- **Automatic Format Detection**: Automatically detects whether the uploaded file is `.cif` or `.xyz`.
- **Bidirectional Conversion**:
  - CIF → XYZ
  - XYZ → CIF
- **Instant Download**: Returns the converted file immediately for easy saving.
- **One-Click Deployment**: Fully containerized using Docker and Docker Compose — no manual environment setup required.
- **Pretty Logging**: Integrated `rich` logging for clear, colorful console output.

## ⚙️ Requirements

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🚀 Quick Start

1. **Clone or Download the Project**
   Download or clone the project, including `app/`, `Dockerfile`, `docker-compose.yml`, and `requirements.txt`.

2. **Build and Run the Service**
   In the project root directory, run:

   ```bash
   docker-compose up --build
   ```

   Once you see logs indicating the server is running at `http://0.0.0.0:8000`, you're good to go.

3. **Access the API**
   The service runs locally on port `8000` by default.

## 🛠️ How to Use

Send a `POST` request to the `/convert/` endpoint to upload your file.

- **Endpoint**: `POST http://localhost:8000/convert/`
- **Request Body**: `multipart/form-data`
- **Parameter**:
  - `file`: The `.cif` or `.xyz` file to convert.

### Example Using `curl`

**Convert CIF to XYZ:**

```bash
curl -X POST -F "file=@/path/to/your/my_structure.cif" http://localhost:8000/convert/ -o converted.xyz
```

**Convert XYZ to CIF:**

```bash
curl -X POST -F "file=@/path/to/your/atoms.xyz" http://localhost:8000/convert/ -o converted.cif
```
