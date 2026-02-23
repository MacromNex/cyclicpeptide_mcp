"""
Shared molecular manipulation functions for cyclic peptide MCP scripts.

These are extracted and simplified from the cyclicpeptide repository code
to minimize dependencies and create self-contained functionality.
"""

from pathlib import Path
from typing import Union, Optional, List, Dict, Any
import re
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit.Chem.Draw import rdMolDraw2D

def parse_smiles(smiles: str) -> Optional[Chem.Mol]:
    """Parse SMILES string to RDKit molecule.

    Args:
        smiles: SMILES string

    Returns:
        RDKit molecule object or None if invalid
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        return mol
    except Exception:
        return None

def generate_3d_conformer(mol: Chem.Mol, num_conformers: int = 1) -> Optional[Chem.Mol]:
    """Generate 3D conformer(s) for a molecule.

    Args:
        mol: RDKit molecule
        num_conformers: Number of conformers to generate

    Returns:
        Molecule with 3D conformers or None if failed
    """
    try:
        mol_copy = Chem.Mol(mol)
        mol_copy = Chem.AddHs(mol_copy)

        # Generate conformers
        if num_conformers == 1:
            AllChem.EmbedMolecule(mol_copy, randomSeed=42)
        else:
            AllChem.EmbedMultipleConfs(mol_copy, numConfs=num_conformers, randomSeed=42)

        # Optimize geometry
        AllChem.MMFFOptimizeMoleculeConfs(mol_copy)
        return mol_copy
    except Exception:
        return None

def is_cyclic_peptide(mol: Chem.Mol) -> bool:
    """Check if molecule is a cyclic peptide.

    Args:
        mol: RDKit molecule

    Returns:
        True if molecule has rings (cyclic)
    """
    try:
        ring_info = mol.GetRingInfo()
        return ring_info.NumRings() > 0
    except Exception:
        return False

def save_molecule(mol: Chem.Mol, file_path: Union[str, Path],
                  file_format: str = "pdb") -> bool:
    """Save molecule to file in specified format.

    Args:
        mol: RDKit molecule
        file_path: Output file path
        file_format: Output format ('pdb', 'sdf', 'smi', 'mol')

    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        if file_format.lower() == "pdb":
            Chem.MolToPDBFile(mol, str(file_path))
        elif file_format.lower() == "sdf":
            writer = Chem.SDWriter(str(file_path))
            writer.write(mol)
            writer.close()
        elif file_format.lower() in ["smi", "smiles"]:
            with open(file_path, 'w') as f:
                f.write(Chem.MolToSmiles(mol))
        elif file_format.lower() == "mol":
            Chem.MolToMolFile(mol, str(file_path))
        else:
            raise ValueError(f"Unsupported format: {file_format}")

        return True
    except Exception:
        return False

def plot_molecule_svg(mol: Chem.Mol, width: int = 400, height: int = 400) -> Optional[str]:
    """Generate SVG visualization of molecule.

    Args:
        mol: RDKit molecule
        width: Image width
        height: Image height

    Returns:
        SVG string or None if failed
    """
    try:
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        svg = drawer.GetDrawingText()
        return svg
    except Exception:
        return None

def canonicalize_smiles(smiles: str) -> Optional[str]:
    """Canonicalize SMILES string.

    Args:
        smiles: Input SMILES string

    Returns:
        Canonical SMILES string or None if invalid
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol)
    except Exception:
        return None

# Amino acid reference data (inlined from cyclicpeptide package)
AMINO_ACID_CODES = {
    'A': 'Ala', 'R': 'Arg', 'N': 'Asn', 'D': 'Asp', 'C': 'Cys',
    'E': 'Glu', 'Q': 'Gln', 'G': 'Gly', 'H': 'His', 'I': 'Ile',
    'L': 'Leu', 'K': 'Lys', 'M': 'Met', 'F': 'Phe', 'P': 'Pro',
    'S': 'Ser', 'T': 'Thr', 'W': 'Trp', 'Y': 'Tyr', 'V': 'Val'
}

# Reverse mapping
THREE_TO_ONE_LETTER = {v: k for k, v in AMINO_ACID_CODES.items()}

def convert_sequence_codes(sequence: str) -> str:
    """Convert between 1-letter and 3-letter amino acid codes.

    Args:
        sequence: Amino acid sequence

    Returns:
        Converted sequence
    """
    if not sequence:
        return ""

    # Check if it's 3-letter codes (contains uppercase letters > 1 char)
    if re.search(r'[A-Z][a-z]{2}', sequence):
        # Convert 3-letter to 1-letter
        parts = re.findall(r'[A-Z][a-z]{2}', sequence)
        result = ""
        for part in parts:
            if part in THREE_TO_ONE_LETTER:
                result += THREE_TO_ONE_LETTER[part]
        return result
    else:
        # Convert 1-letter to 3-letter
        result = ""
        for char in sequence.upper():
            if char in AMINO_ACID_CODES:
                result += AMINO_ACID_CODES[char]
        return result

def calculate_molecular_weight(mol: Chem.Mol) -> Optional[float]:
    """Calculate molecular weight of molecule.

    Args:
        mol: RDKit molecule

    Returns:
        Molecular weight in g/mol or None if failed
    """
    try:
        return Descriptors.ExactMolWt(mol)
    except Exception:
        return None

def count_atoms(mol: Chem.Mol) -> Optional[int]:
    """Count number of atoms in molecule.

    Args:
        mol: RDKit molecule

    Returns:
        Number of atoms or None if failed
    """
    try:
        return mol.GetNumAtoms()
    except Exception:
        return None

def count_rings(mol: Chem.Mol) -> Optional[int]:
    """Count number of rings in molecule.

    Args:
        mol: RDKit molecule

    Returns:
        Number of rings or None if failed
    """
    try:
        return mol.GetRingInfo().NumRings()
    except Exception:
        return None