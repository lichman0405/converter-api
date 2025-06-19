# The module is the entrance point for the FastAPI application
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


import io
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from .logger import logger
from .converter import convert_cif_to_xyz, convert_xyz_to_cif

app = FastAPI(
    title="Lossless File Type Converter API",
    version="1.0.0",
    description="A containerized API for **lossless** round-trip conversion between CIF and XYZ file formats."
)

@app.on_event("startup")
async def startup_event():
    logger.rule("Service started")
    logger.info("FastAPI application is ready.")
    logger.info("Waiting for file upload requests at /convert endpoint.")

@app.post("/convert/", response_class=StreamingResponse)
async def create_upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename} (type: {file.content_type})")
    filename = file.filename
    if not filename:
        logger.warning("No filename provided in the uploaded file.")
        raise HTTPException(status_code=400, detail="No file name.")
    try:
        contents_bytes = await file.read()
        contents_str = contents_bytes.decode('utf-8')
        suffix = Path(filename).suffix.lower()
        stem = Path(filename).stem
        if suffix == '.cif':
            output_content = convert_cif_to_xyz(contents_str)
            new_filename = f"{stem}.xyz"
        elif suffix == '.xyz':
            output_content = convert_xyz_to_cif(contents_str)
            new_filename = f"{stem}.cif"
        else:
            logger.warning(f"Unsupported file format: {filename}")
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .cif or .xyz file.")
        response_stream = io.StringIO(output_content)
        logger.success(f"Successfully sending converted file {new_filename} for download.")
        return StreamingResponse(
            response_stream,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={new_filename}"}
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception(f"Unexpected error occurred while processing file {file.filename}")
        raise HTTPException(status_code=500, detail=f"Internal server error occurred: {str(e)}")

@app.get("/")
async def root():
    logger.info("Root path accessed.")
    return {"message": "Welcome to the Lossless CIF/XYZ file converter. POST files to /convert/."}