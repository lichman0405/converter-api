# The module is to provide file conversion functionality
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0


import io
import os
from ase import Atoms
from ase.io import read, write
from fastapi import UploadFile, HTTPException
from .logger import logger

# flag to identify lattice information in XYZ comment lines
LATTICE_INFO_TAG = "Lattice_Info:"

def convert_cif_to_xyz(file: UploadFile):
    """
    Converts a CIF file to XYZ format, embedding lattice information
    in the comment line of the XYZ file.
    """
    filename = file.filename
    try:
        content = file.file.read()
        input_stream = io.StringIO(content.decode('utf-8'))
        atoms = read(input_stream, format='cif')
    except Exception as e:
        logger.error(f"Failed to read CIF file '{filename}': {e}")
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted CIF file: {e}")
    finally:
        input_stream.close()

    # parse the lattice parameters from the Atoms object
    try:
        cell_params = atoms[0].get_cell().cellpar() # type: ignore
        # standardize to 6 parameters
        lattice_str = ";".join(f"{p:.8f}" for p in cell_params)
        comment_line = f"{LATTICE_INFO_TAG} {lattice_str}"
        logger.info(f"Embedding lattice info into XYZ comment: {comment_line}")
    except Exception:
        # no lattice information available, set a default comment
        comment_line = "No lattice information in source CIF."
        logger.warning(f"No lattice info found in {filename}, XYZ comment will be empty.")

    
    output_stream = io.StringIO()
    try:
        # passing the comment line to the write function
        write(output_stream, atoms, format='xyz', comment=comment_line)
        output_content = output_stream.getvalue().encode('utf-8')
        new_filename = os.path.splitext(filename)[0] + '.xyz' # type: ignore
        logger.success(f"Successfully converted {filename} to {new_filename} with lattice info.")
    except Exception as e:
        logger.error(f"Error writing XYZ file format: {e}")
        raise HTTPException(status_code=500, detail=f"File conversion failed: {e}")
    finally:
        output_stream.close()

    return output_content, new_filename


def convert_xyz_to_cif(file: UploadFile):
    """
    Converts an XYZ file to CIF format. It intelligently checks for
    lattice information in the comment line to rebuild a periodic CIF.
    """
    filename = file.filename
    content = file.file.read()
    
    logger.info(f"Starting XYZ to CIF conversion for file: {filename}...")
    
    # parse the content to extract lattice information if available
    cell = None
    try:
        decoded_content = content.decode('utf-8')
        lines = decoded_content.splitlines()
        if len(lines) > 1 and lines[1].strip().startswith(LATTICE_INFO_TAG):
            param_str = lines[1].strip().replace(LATTICE_INFO_TAG, "").strip()
            cell_params = [float(p) for p in param_str.split(';')]
            if len(cell_params) == 6:
                # build the cell from the parameters
                cell = Atoms.fromdict({'cell': cell_params, 'pbc': True}).get_cell()
                logger.info("Successfully decoded lattice info from XYZ comment.")
    except Exception as e:
        logger.warning(f"Could not decode lattice info from comment line, will proceed without it. Error: {e}")

    input_stream = io.StringIO(decoded_content)
    try:
        # read the XYZ file into an Atoms object
        atoms = read(input_stream, format='xyz')
        
        # if we successfully decoded the cell, apply it to the Atoms object
        if cell is not None:
            atoms.set_cell(cell) # type: ignore
            atoms.set_pbc(True) # set periodic boundary conditions # type: ignore
            logger.info("Applied decoded cell to Atoms object before writing to CIF.")

    except Exception as e:
        logger.error(f"Failed to read XYZ file for conversion: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted XYZ file: {e}")
    finally:
        input_stream.close()

    output_stream = io.BytesIO()
    try:
        write(output_stream, atoms, format='cif')
        output_content = output_stream.getvalue()
        new_filename = os.path.splitext(filename)[0] + '.cif'# type: ignore
        logger.success(f"Successfully converted {filename} to {new_filename}.")
    except Exception as e:
        logger.error(f"Error writing final CIF file: {e}")
        raise HTTPException(status_code=500, detail=f"File conversion failed: {e}")
    finally:
        output_stream.close()

    return output_content, new_filename