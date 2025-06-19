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
    """
    if not content.strip():
        logger.error("CIF content is empty or contains only whitespace.")
        raise ValueError("Input CIF content is empty.")

    logger.info("Starting CIF to XYZ lossless conversion...")
    
    with io.StringIO(content) as input_stream:
        atoms = read(input_stream, format='cif')

    cell = atoms.get_cell().flatten()
    cell_str = " ".join(map(str, cell))
    pbc_str = " ".join(["T" if p else "F" for p in atoms.pbc])
    comment = f'Lattice="{cell_str}" pbc="{pbc_str}"'
    logger.info(f"Embedded lattice info into comment: {comment}")

    with io.StringIO() as output_stream:
        write(output_stream, atoms, format='xyz', comment=comment)
        logger.success("CIF to XYZ conversion successful.")
        return output_stream.getvalue()


def convert_xyz_to_cif(content: str, filename: str) -> str:
    """
    Converts an XYZ string to a CIF string. It always trusts the lattice
    information from the comment line if present, ensuring the original
    periodicity is preserved even after external modifications.
    """
    if not content.strip():
        logger.error("XYZ content is empty or contains only whitespace.")
        raise ValueError("Input XYZ content is empty.")
        
    logger.info(f"Starting XYZ to CIF conversion for: {filename}")
    
    lines = content.splitlines()
    lattice_matrix = None
    pbc = [False, False, False]
    
    # Always try to read lattice information to preserve periodicity for downstream tools.
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
        atoms = read(input_stream, format='xyz')

    # If lattice information was successfully parsed, apply it to the Atoms object.
    # This correctly combines optimized coordinates with the original cell.
    if lattice_matrix is not None:
        atoms.set_cell(lattice_matrix)
        atoms.set_pbc(pbc)
        logger.info("Applied parsed lattice and PBC data to the structure.")
    else:
        logger.warning("No valid lattice data found in XYZ comment. Generating CIF with a default (non-periodic) cell.")

    with io.BytesIO() as output_stream:
        write(output_stream, atoms, format='cif')
        logger.success("XYZ to CIF conversion successful.")
        return output_stream.getvalue().decode('utf-8')