# The module is to provide file conversion functionality
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0

import io
import re
import numpy as np
from ase.io import read, write
from .logger import logger

def convert_cif_to_xyz(content: str) -> str:
    """
    Converts CIF content string to an 'enhanced' XYZ string for lossless conversion.
    This version includes enhanced error handling and resource management.
    """
    if not content.strip():
        logger.error("CIF content is empty or contains only whitespace.")
        raise ValueError("Input CIF content is empty.")

    logger.info("Starting CIF to XYZ lossless conversion...")
    
    try:
        with io.StringIO(content) as input_stream:
            try:
                atoms = read(input_stream, format='cif')
            except Exception as e:
                logger.error(f"ASE failed to read CIF data. Error: {e}")
                raise ValueError(f"Invalid or corrupted CIF file content: {e}")

        cell = atoms.get_cell().flatten()
        cell_str = " ".join(map(str, cell))
        pbc_str = " ".join(["T" if p else "F" for p in atoms.pbc])
        comment = f'Lattice="{cell_str}" pbc="{pbc_str}"'
        logger.info(f"Embedded lattice info into comment: {comment}")

        with io.StringIO() as output_stream:
            try:
                write(output_stream, atoms, format='xyz', comment=comment)
                logger.success("CIF to XYZ conversion successful.")
                return output_stream.getvalue()
            except Exception as e:
                logger.error(f"ASE failed to write XYZ data. Error: {e}")
                raise ValueError(f"Failed to write atoms to XYZ format: {e}")

    except ValueError as ve:
        # Re-raise known value errors to be handled by the endpoint
        raise ve
    except Exception as e:
        # Catch any other unexpected errors during the process
        logger.error(f"An unexpected error occurred during CIF to XYZ conversion: {e}")
        raise RuntimeError(f"A critical error occurred in conversion logic: {e}")


def convert_xyz_to_cif(content: str) -> str:
    """
    Converts an 'enhanced' or standard XYZ string to a CIF string.
    This version includes enhanced error handling and resource management.
    """
    if not content.strip():
        logger.error("XYZ content is empty or contains only whitespace.")
        raise ValueError("Input XYZ content is empty.")
        
    logger.info("Starting XYZ to CIF lossless conversion...")
    
    try:
        lines = content.splitlines()
        lattice_matrix = None
        pbc = [False, False, False]

        if len(lines) >= 2:
            comment_line = lines[1]
            lattice_match = re.search(r'Lattice="([^"]+)"', comment_line)
            if lattice_match:
                try:
                    cell_flat = np.fromstring(lattice_match.group(1), sep=' ')
                    lattice_matrix = cell_flat.reshape(3, 3)
                    logger.info("Found and parsed lattice data from XYZ comment.")
                except (ValueError, IndexError) as e:
                    logger.warning(f"Found 'Lattice' tag but failed to parse it: {e}. Proceeding without lattice info.")
                    lattice_matrix = None
            
            pbc_match = re.search(r'pbc="([^"]+)"', comment_line)
            if pbc_match:
                pbc_flags = pbc_match.group(1).strip().split()
                pbc = [flag.upper() == 'T' for flag in pbc_flags]
                logger.info(f"Found and parsed PBC info: {pbc}")

        with io.StringIO(content) as input_stream:
            try:
                atoms = read(input_stream, format='xyz')
            except Exception as e:
                logger.error(f"ASE failed to read XYZ data. Error: {e}")
                raise ValueError(f"Invalid or corrupted XYZ file content: {e}")

        if lattice_matrix is not None:
            atoms.set_cell(lattice_matrix)
            atoms.set_pbc(pbc)
            logger.info("Applied parsed lattice and PBC data to the structure.")
        else:
            logger.warning("No valid lattice data found in XYZ. Generating CIF with a default cell.")

        # FIX: Use BytesIO because ASE CIF writer produces bytes, which causes a TypeError with StringIO.
        with io.BytesIO() as output_stream:
            try:
                write(output_stream, atoms, format='cif')
                logger.success("XYZ to CIF conversion successful.")
                # Decode the bytes back to a string for the response.
                return output_stream.getvalue().decode('utf-8')
            except Exception as e:
                logger.error(f"ASE failed to write CIF data. Error: {e}")
                raise ValueError(f"Failed to write atoms to CIF format: {e}")
                
    except ValueError as ve:
        raise ve
    except Exception as e:
        logger.error(f"An unexpected error occurred during XYZ to CIF conversion: {e}")
        raise RuntimeError(f"A critical error occurred in conversion logic: {e}")
