# The module is to provide file conversion functionality
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0

import io
import re
from ase.io import read, write
from .logger import logger

def convert_cif_to_xyz(content: str) -> str:
    logger.info("Starting CIF to XYZ lossless conversion...")
    input_stream = io.StringIO(content)
    try:
        atoms = read(input_stream, format='cif')
        cell = atoms.get_cell().flatten()
        cell_str = " ".join(map(str, cell))
        pbc_str = " ".join(["T" if p else "F" for p in atoms.pbc])
        comment = f'Lattice="{cell_str}" pbc="{pbc_str}"'
        logger.info(f"Embedded lattice info into comment: {comment}")
        output_stream = io.StringIO()
        write(output_stream, atoms, format='xyz', comment=comment)
        logger.success("CIF to XYZ conversion successful.")
        return output_stream.getvalue()
    finally:
        input_stream.close()
        if 'output_stream' in locals():
            output_stream.close()

def convert_xyz_to_cif(content: str) -> str:
    logger.info("Starting XYZ to CIF lossless conversion...")
    input_stream = io.StringIO(content)
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
                except (ValueError, IndexError):
                    logger.warning("Found 'Lattice' tag but failed to parse it. Proceeding without lattice info.")
                    lattice_matrix = None
            pbc_match = re.search(r'pbc="([^"]+)"', comment_line)
            if pbc_match:
                pbc_flags = pbc_match.group(1).strip().split()
                pbc = [flag.upper() == 'T' for flag in pbc_flags]
                logger.info(f"Found and parsed PBC info: {pbc}")
        atoms = read(input_stream, format='xyz')
        if lattice_matrix is not None:
            atoms.set_cell(lattice_matrix)
            atoms.set_pbc(pbc)
            logger.info("Applied parsed lattice and PBC data to the structure.")
        else:
            logger.warning("No valid lattice data found in XYZ. Generating CIF with default cell.")
        output_stream = io.StringIO()
        write(output_stream, atoms, format='cif')
        logger.success("XYZ to CIF conversion successful.")
        return output_stream.getvalue()
    finally:
        input_stream.close()
        if 'output_stream' in locals():
            output_stream.close()