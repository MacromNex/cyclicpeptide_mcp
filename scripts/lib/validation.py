"""
Validation utilities for cyclic peptide MCP scripts.

Input validation functions extracted from the cyclicpeptide repository.
"""

import re
from typing import Optional, Tuple, List
from rdkit import Chem
from .molecules import AMINO_ACID_CODES, parse_smiles

def validate_smiles(smiles: str) -> Tuple[bool, Optional[str]]:
    """Validate SMILES string.

    Args:
        smiles: SMILES string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not smiles or not smiles.strip():
        return False, "Empty SMILES string"

    smiles = smiles.strip()

    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return False, "Invalid SMILES: Could not parse molecule"

        # Additional checks
        if mol.GetNumAtoms() == 0:
            return False, "SMILES represents empty molecule"

        return True, None

    except Exception as e:
        return False, f"SMILES validation error: {str(e)}"

def validate_sequence(sequence: str) -> Tuple[bool, Optional[str]]:
    """Validate amino acid sequence.

    Args:
        sequence: Amino acid sequence (1-letter or 3-letter codes)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sequence or not sequence.strip():
        return False, "Empty sequence"

    sequence = sequence.strip().upper()

    # Check if it's 3-letter codes
    if re.search(r'[A-Z][a-z]{2}', sequence):
        # Validate 3-letter codes
        three_letter_codes = re.findall(r'[A-Z][a-z]{2}', sequence)
        for code in three_letter_codes:
            if code not in AMINO_ACID_CODES.values():
                return False, f"Invalid 3-letter amino acid code: {code}"
        return True, None

    else:
        # Validate 1-letter codes
        for char in sequence:
            if char not in AMINO_ACID_CODES:
                return False, f"Invalid 1-letter amino acid code: {char}"
        return True, None

def validate_cyclic_peptide(smiles: str) -> Tuple[bool, Optional[str]]:
    """Validate that SMILES represents a cyclic peptide.

    Args:
        smiles: SMILES string

    Returns:
        Tuple of (is_valid, error_message)
    """
    # First validate SMILES
    is_valid, error = validate_smiles(smiles)
    if not is_valid:
        return False, error

    try:
        mol = parse_smiles(smiles)
        if mol is None:
            return False, "Could not parse SMILES"

        # Check for rings
        ring_info = mol.GetRingInfo()
        if ring_info.NumRings() == 0:
            return False, "Molecule is not cyclic"

        # Check if it contains peptide bonds (amide bonds)
        has_amide = False
        for bond in mol.GetBonds():
            begin_atom = bond.GetBeginAtom()
            end_atom = bond.GetEndAtom()

            # Look for C(=O)N pattern (amide bond)
            if ((begin_atom.GetAtomicNum() == 6 and end_atom.GetAtomicNum() == 7) or
                (begin_atom.GetAtomicNum() == 7 and end_atom.GetAtomicNum() == 6)):

                # Check for carbonyl oxygen
                for neighbor in begin_atom.GetNeighbors():
                    if neighbor.GetAtomicNum() == 8:  # Oxygen
                        for neighbor_bond in neighbor.GetBonds():
                            if neighbor_bond.GetBondType() == Chem.BondType.DOUBLE:
                                has_amide = True
                                break
                if has_amide:
                    break

        if not has_amide:
            return False, "Molecule does not appear to contain peptide bonds"

        return True, None

    except Exception as e:
        return False, f"Validation error: {str(e)}"

def validate_input_file_format(file_path: str, expected_content: str = "auto") -> Tuple[bool, Optional[str]]:
    """Validate input file format and content.

    Args:
        file_path: Path to input file
        expected_content: Expected content type ("smiles", "sequence", "auto")

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        from pathlib import Path
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return False, f"File does not exist: {file_path}"

        suffix = file_path_obj.suffix.lower()
        valid_formats = ['.txt', '.csv', '.smi', '.json']

        if suffix not in valid_formats:
            return False, f"Unsupported file format: {suffix}. Supported: {valid_formats}"

        # Basic content validation
        try:
            with open(file_path_obj, 'r') as f:
                content = f.read(1000)  # Read first 1KB
                if not content.strip():
                    return False, "File is empty"

        except UnicodeDecodeError:
            return False, "File is not a valid text file"

        return True, None

    except Exception as e:
        return False, f"File validation error: {str(e)}"

def assess_data_quality(data: str, data_type: str = "auto") -> dict:
    """Assess quality of input data.

    Args:
        data: Input data (SMILES or sequence)
        data_type: Type of data ("smiles", "sequence", "auto")

    Returns:
        Dictionary with quality assessment
    """
    assessment = {
        "quality_score": 0,  # 0-100
        "issues": [],
        "warnings": [],
        "data_type": data_type
    }

    if not data or not data.strip():
        assessment["issues"].append("Empty data")
        return assessment

    data = data.strip()

    # Auto-detect data type if not specified
    if data_type == "auto":
        # Simple heuristic: if contains common SMILES chars, assume SMILES
        if any(char in data for char in ['(', ')', '[', ']', '=', '#', '@']):
            data_type = "smiles"
        else:
            data_type = "sequence"
        assessment["data_type"] = data_type

    if data_type == "smiles":
        is_valid, error = validate_smiles(data)
        if is_valid:
            assessment["quality_score"] += 50

            # Additional quality checks for SMILES
            mol = parse_smiles(data)
            if mol:
                num_atoms = mol.GetNumAtoms()
                if num_atoms > 0:
                    assessment["quality_score"] += 30

                # Check for reasonable peptide size
                if 10 <= num_atoms <= 200:
                    assessment["quality_score"] += 20
                elif num_atoms > 200:
                    assessment["warnings"].append("Large molecule (>200 atoms)")
                elif num_atoms < 10:
                    assessment["warnings"].append("Small molecule (<10 atoms)")

        else:
            assessment["issues"].append(f"Invalid SMILES: {error}")

    elif data_type == "sequence":
        is_valid, error = validate_sequence(data)
        if is_valid:
            assessment["quality_score"] += 50

            # Additional quality checks for sequences
            seq_length = len(data) if not re.search(r'[A-Z][a-z]{2}', data) else len(re.findall(r'[A-Z][a-z]{2}', data))

            if 3 <= seq_length <= 50:
                assessment["quality_score"] += 30
            elif seq_length > 50:
                assessment["warnings"].append("Long sequence (>50 residues)")
            elif seq_length < 3:
                assessment["warnings"].append("Short sequence (<3 residues)")

            if seq_length >= 3:
                assessment["quality_score"] += 20

        else:
            assessment["issues"].append(f"Invalid sequence: {error}")

    return assessment

def validate_output_path(output_path: str, create_dirs: bool = True) -> Tuple[bool, Optional[str]]:
    """Validate output path.

    Args:
        output_path: Output file or directory path
        create_dirs: Whether to create directories if they don't exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        from pathlib import Path
        output_path_obj = Path(output_path)

        # Check parent directory
        parent_dir = output_path_obj.parent
        if not parent_dir.exists():
            if create_dirs:
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return False, f"Cannot create output directory: {e}"
            else:
                return False, f"Output directory does not exist: {parent_dir}"

        # Check write permissions
        try:
            # Try to create a temporary file in the directory
            test_file = parent_dir / ".test_write_permission"
            test_file.touch()
            test_file.unlink()
        except Exception:
            return False, f"No write permission in output directory: {parent_dir}"

        return True, None

    except Exception as e:
        return False, f"Output path validation error: {str(e)}"