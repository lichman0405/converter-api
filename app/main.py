# The module is the entrance point for the FastAPI application
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import io
from .logger import logger
from .converter import convert_cif_to_xyz, convert_xyz_to_cif 

app = FastAPI(
    title="File Type Converter API",
    description="A simple API for converting between CIF and XYZ file formats."
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
        logger.warning("There is no filename provided in the uploaded file.")
        raise HTTPException(status_code=400, detail="No file name.")

    output_content = None
    new_filename = None

    try:
        if filename.lower().endswith('.cif'):
            output_content, new_filename = convert_cif_to_xyz(file)
        elif filename.lower().endswith('.xyz'):
            output_content, new_filename = convert_xyz_to_cif(file)
        else:
            logger.warning(f"Unsupported file format: {filename}")
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .cif or .xyz file.")

        response_stream = io.BytesIO(output_content)

        logger.success(f"Successfully sent converted file {new_filename} for download.")

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
    """Root path providing welcome information"""
    logger.info("Root path accessed.")
    return {"message": "Welcome to the CIF/XYZ file converter. Please POST your files to the /convert/ endpoint."}