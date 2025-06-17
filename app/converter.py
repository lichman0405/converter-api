# The module is to provide file conversion functionality
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


import io
from ase.io import read, write
from fastapi import UploadFile, HTTPException
from .logger import logger

def convert_cif_to_xyz(file: UploadFile):
    """
    Converts a CIF file to XYZ format and returns the new content and filename.
    """
    filename = file.filename
    content = file.file.read()

    input_stream = io.StringIO(content.decode('utf-8'))
    
    atoms = None
    new_filename = None

    if not filename:
        logger.warning("No filename provided for CIF to XYZ conversion.")
        raise HTTPException(status_code=400, detail="No file name.")

    if not filename.lower().endswith('.cif'):
        logger.warning(f"Invalid file format for CIF to XYZ conversion: {filename}")
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .cif file for CIF to XYZ conversion.")

    logger.info(f"Starting CIF to XYZ conversion for file: {filename}...")
    try:
        atoms = read(input_stream, format='cif')
        output_format = 'xyz'
        new_filename = filename[:-4] + '.xyz'
    except Exception as e:
        logger.error(f"Failed to read CIF file for conversion: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted CIF file: {e}")

    output_stream = io.StringIO() 
    try:
        write(output_stream, atoms, format=output_format)
        output_content = output_stream.getvalue().encode('utf-8') 
        logger.success(f"Successfully converted {filename} to {new_filename}.")
    except Exception as e:
        logger.error(f"Error writing XYZ file format: {e}")
        raise HTTPException(status_code=500, detail=f"File conversion failed: {e}")
    finally:
        input_stream.close()
        output_stream.close()

    return output_content, new_filename


def convert_xyz_to_cif(file: UploadFile):
    """
    Converts an XYZ file to CIF format and returns the new content and filename.
    """
    filename = file.filename
    content = file.file.read()

    input_stream = io.StringIO(content.decode('utf-8'))
    
    atoms = None
    new_filename = None

    if not filename:
        logger.warning("No filename provided for XYZ to CIF conversion.")
        raise HTTPException(status_code=400, detail="No file name.")

    if not filename.lower().endswith('.xyz'):
        logger.warning(f"Invalid file format for XYZ to CIF conversion: {filename}")
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an .xyz file for XYZ to CIF conversion.")

    logger.info(f"Starting XYZ to CIF conversion for file: {filename}...")
    try:
        atoms = read(input_stream, format='xyz')
        output_format = 'cif'
        new_filename = filename[:-4] + '.cif'
    except Exception as e:
        logger.error(f"Failed to read XYZ file for conversion: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted XYZ file: {e}")

    output_stream = io.BytesIO() 
    try:
        write(output_stream, atoms, format=output_format)
        output_content = output_stream.getvalue() 
        logger.success(f"Successfully converted {filename} to {new_filename}.")
    except Exception as e:
        logger.error(f"Error writing CIF file format: {e}")
        raise HTTPException(status_code=500, detail=f"File conversion failed: {e}")
    finally:
        input_stream.close()
        output_stream.close()

    return output_content, new_filename