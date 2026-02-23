"""
Shared library for cyclic peptide MCP scripts.

This package contains common utilities extracted from the cyclicpeptide
repository to minimize dependencies and create self-contained scripts.
"""

__version__ = "1.0.0"

from .molecules import *
from .io import *
from .validation import *

__all__ = [
    'parse_smiles',
    'generate_3d_conformer',
    'is_cyclic_peptide',
    'save_molecule',
    'load_input_file',
    'save_output_file',
    'validate_smiles',
    'validate_sequence',
]