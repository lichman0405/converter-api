# The module is to provide file conversion functionality
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


import io
from ase.io import read, write
from fastapi import UploadFile, HTTPException
from .logger import logger

def convert_structure_file(file: UploadFile):
    """
    Detects file type, converts it, and returns the new content and filename.
    """
    filename = file.filename
    content = file.file.read()

    # Input stream for reading is always text-based for .cif and .xyz
    input_stream = io.StringIO(content.decode('utf-8'))
    
    atoms = None
    new_filename = None

    if not filename:
        logger.warning("There is no filename provided in the uploaded file.")
        raise HTTPException(status_code=400, detail="No file name.")

    if filename.lower().endswith('.cif'):
        logger.info(f"Detected CIF file: {filename}. Starting conversion to XYZ...")
        try:
            atoms = read(input_stream, format='cif')
            output_format = 'xyz'
            new_filename = filename[:-4] + '.xyz'
        except Exception as e:
            logger.error(f"Failed to read CIF file: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted CIF file: {e}")

    elif filename.lower().endswith('.xyz'):
        logger.info(f"Detected XYZ file: {filename}. Starting conversion to CIF...")
        try:
            atoms = read(input_stream, format='xyz')
            output_format = 'cif'
            new_filename = filename[:-4] + '.cif'
        except Exception as e:
            logger.error(f"Failed to read XYZ file: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid or corrupted XYZ file: {e}")
            
    else:
        logger.warning(f"Unsupported file format: {filename}")
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .cif or .xyz file.")

    # Modified: Always use BytesIO for writing and getvalue() will correctly return bytes.
    # The 'write' function of ase.io handles the internal encoding for text formats.
    output_stream = io.BytesIO() 
    try:
        write(output_stream, atoms, format=output_format)
        # getvalue() from BytesIO already returns bytes, so no need for .encode('utf-8')
        output_content = output_stream.getvalue() 
        logger.success(f"Successfully converted {filename} to {new_filename}.")
    except Exception as e:
        logger.error(f"Error writing new file format: {e}")
        raise HTTPException(status_code=500, detail=f"File conversion failed: {e}")
    finally:
        input_stream.close()
        output_stream.close()

    return output_content, new_filename