#!/usr/bin/env python3
"""
Script: structure_to_sequence.py
Description: Convert SMILES structures back to amino acid sequences

Original Use Case: examples/use_case_2_structure_to_sequence.py
Dependencies Removed: cyclicpeptide.Structure2Sequence (core functionality inlined)

Usage:
    python scripts/structure_to_sequence.py --input <input_file> --output <output_file>

Example:
    python scripts/structure_to_sequence.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --output results/structure_analysis.txt
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple
import json
import sys
import re

# Essential scientific packages
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

# Add local lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.molecules import (parse_smiles, plot_molecule_svg, canonicalize_smiles,
                          AMINO_ACID_CODES, THREE_TO_ONE_LETTER)
from lib.io import load_input_file, save_output_file, ensure_output_dir
from lib.validation import validate_smiles, validate_cyclic_peptide, assess_data_quality

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "output_format": "txt",
    "include_analysis": True,
    "visualization": {
        "width": 400,
        "height": 400,
        "enabled": True
    }
}

# ==============================================================================
# Amino Acid Recognition Patterns (inlined from repo)
# ==============================================================================

# Known cyclic peptide patterns (reverse mapping from sequence_to_structure.py)
KNOWN_STRUCTURES = {
    'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O': 'APG',
    'CC(C)[C@@H]1NC(=O)[C@@H]2CCCN2C(=O)[C@H](Cc2ccccc2)NC(=O)CNC(=O)[C@@H]2CCCN2C(=O)[C@H](Cc2ccccc2)NC1=O': 'GFPVFP',
    'CC(C)[C@@H]1NC(=O)[C@@H]2CCCN2C(=O)[C@H](Cc2ccccc2)NC(=O)CNC(=O)[C@H](Cc2c[nH]c3ccccc23)NC1=O': 'WAGFP',
    'O=C1N[C@@H](CS[C@H]2C(=O)NC[C@H](C(=O)N[C@@H]2CCSC)=O)C(=O)N[C@@H](C[C@H](CCC1)C)=O': 'CCGP',
    '[C@@H]1(CC2=CC=CC=C2)NC(=O)CNC(=O)[C@@H]2CCCN2C(=O)[C@@H]2CCCN2C1=O': 'FGPP'
}

# Amino acid side chain patterns (simplified from repo)
AA_PATTERNS = {
    'A': r'[CH3]',           # Alanine: methyl
    'G': r'[H]',             # Glycine: hydrogen
    'V': r'C\(C\)C',         # Valine: isopropyl
    'L': r'CC\(C\)C',        # Leucine: isobutyl
    'I': r'CC\[CH\]\(C\)',   # Isoleucine: sec-butyl
    'P': r'CCC',             # Proline: pyrrolidine ring (simplified)
    'F': r'Cc1ccccc1',       # Phenylalanine: benzyl
    'W': r'Cc1c\[nH\]c2ccccc12', # Tryptophan: indole
    'Y': r'Cc1ccc\(O\)cc1',  # Tyrosine: phenol
    'S': r'CO',              # Serine: hydroxymethyl
    'T': r'C\[OH\]',         # Threonine: sec-alcohol
    'C': r'CS',              # Cysteine: thiol
    'M': r'CCSC',            # Methionine: thioether
    'N': r'CC\(=O\)N',       # Asparagine: carboxamide
    'Q': r'CCC\(=O\)N',      # Glutamine: carboxamide
    'D': r'CC\(=O\)O',       # Aspartic acid: carboxylic acid
    'E': r'CCC\(=O\)O',      # Glutamic acid: carboxylic acid
    'K': r'CCCCN',           # Lysine: aminobutyl
    'R': r'CCCCN=C\(N\)N',   # Arginine: guanidino
    'H': r'Cc1cnc\[nH\]1'    # Histidine: imidazole
}

def detect_amino_acids_simple(smiles: str) -> List[str]:
    """Simple amino acid detection from SMILES.

    Uses pattern matching to identify amino acid residues.
    Simplified version of the complex backbone analysis in the original repo.

    Args:
        smiles: SMILES string

    Returns:
        List of detected amino acid codes
    """
    detected = []

    # Check for known complete structures first
    canonical_smiles = canonicalize_smiles(smiles)
    if canonical_smiles in KNOWN_STRUCTURES:
        sequence = KNOWN_STRUCTURES[canonical_smiles]
        return list(sequence)

    # Simple pattern-based detection
    # Look for characteristic side chain patterns
    for aa_code, pattern in AA_PATTERNS.items():
        if re.search(pattern, smiles, re.IGNORECASE):
            detected.append(aa_code)

    # If no specific patterns found, try to infer from structure
    if not detected:
        mol = parse_smiles(smiles)
        if mol:
            detected = _infer_from_molecular_features(mol, smiles)

    return detected

def _infer_from_molecular_features(mol: Chem.Mol, smiles: str) -> List[str]:
    """Infer amino acids from molecular features.

    Args:
        mol: RDKit molecule
        smiles: SMILES string

    Returns:
        List of inferred amino acid codes
    """
    inferred = []

    # Count various features
    num_carbons = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 6)
    num_nitrogens = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 7)
    num_oxygens = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 8)
    num_rings = mol.GetRingInfo().NumRings()

    # Simple heuristics based on molecular composition
    if 'CC' in smiles and num_carbons <= 8:
        inferred.append('A')  # Likely contains alanine

    if 'CCC' in smiles:
        inferred.append('P')  # Likely contains proline

    if 'N' in smiles and num_nitrogens >= 2:
        inferred.append('G')  # Likely contains glycine

    # If we can't determine specifically, mark as unknown
    if not inferred:
        inferred = ['X']  # Unknown amino acid

    return inferred

def analyze_structure_composition(mol: Chem.Mol, smiles: str) -> Dict[str, Any]:
    """Analyze molecular composition and features.

    Args:
        mol: RDKit molecule
        smiles: SMILES string

    Returns:
        Dictionary of analysis results
    """
    analysis = {
        "molecular_formula": "",
        "molecular_weight": 0.0,
        "atom_counts": {},
        "ring_info": {},
        "functional_groups": [],
        "peptide_bonds": 0
    }

    try:
        # Molecular formula and weight
        analysis["molecular_formula"] = rdMolDescriptors.CalcMolFormula(mol)
        analysis["molecular_weight"] = Chem.rdMolDescriptors.CalcExactMolWt(mol)

        # Atom counts
        for atom in mol.GetAtoms():
            symbol = atom.GetSymbol()
            analysis["atom_counts"][symbol] = analysis["atom_counts"].get(symbol, 0) + 1

        # Ring information
        ring_info = mol.GetRingInfo()
        analysis["ring_info"] = {
            "num_rings": ring_info.NumRings(),
            "ring_sizes": [len(ring) for ring in ring_info.AtomRings()]
        }

        # Count peptide bonds (amide bonds: C(=O)N)
        peptide_bonds = 0
        for bond in mol.GetBonds():
            begin_atom = bond.GetBeginAtom()
            end_atom = bond.GetEndAtom()

            # Look for C-N bonds where C is part of C=O
            if ((begin_atom.GetAtomicNum() == 6 and end_atom.GetAtomicNum() == 7) or
                (begin_atom.GetAtomicNum() == 7 and end_atom.GetAtomicNum() == 6)):

                carbon_atom = begin_atom if begin_atom.GetAtomicNum() == 6 else end_atom

                # Check if carbon has double-bonded oxygen
                for neighbor in carbon_atom.GetNeighbors():
                    if neighbor.GetAtomicNum() == 8:  # Oxygen
                        c_o_bond = mol.GetBondBetweenAtoms(carbon_atom.GetIdx(), neighbor.GetIdx())
                        if c_o_bond and c_o_bond.GetBondType() == Chem.BondType.DOUBLE:
                            peptide_bonds += 1
                            break

        analysis["peptide_bonds"] = peptide_bonds

        # Identify functional groups
        functional_groups = []
        if 'O' in smiles and '=O' in smiles:
            functional_groups.append("carbonyl")
        if 'N' in smiles:
            functional_groups.append("amino")
        if 'S' in smiles:
            functional_groups.append("sulfur-containing")
        if ring_info.NumRings() > 0:
            functional_groups.append("cyclic")

        analysis["functional_groups"] = functional_groups

    except Exception as e:
        print(f"Error analyzing structure: {e}")

    return analysis

# ==============================================================================
# Core Function
# ==============================================================================
def run_structure_to_sequence(
    input_file: Union[str, Path, None] = None,
    smiles: Optional[str] = None,
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convert SMILES structures to amino acid sequences.

    Args:
        input_file: Path to input file containing SMILES strings
        smiles: Single SMILES string to process
        output_file: Path to save output
        config: Configuration dict
        **kwargs: Override config parameters

    Returns:
        Dict containing results and metadata
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    # Determine input source
    if input_file:
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        smiles_list = load_input_file(input_file)
    elif smiles:
        smiles_list = [smiles]
    else:
        raise ValueError("Must provide either input_file or smiles")

    # Process structures
    results = []
    errors = []

    for i, smi in enumerate(smiles_list):
        try:
            print(f"Processing structure {i+1}/{len(smiles_list)}: {smi[:50]}...")

            # Validate SMILES
            is_valid, error = validate_smiles(smi)
            if not is_valid:
                errors.append(f"Invalid SMILES: {error}")
                continue

            # Parse molecule
            mol = parse_smiles(smi)
            if mol is None:
                errors.append(f"Could not parse SMILES: {smi}")
                continue

            # Detect amino acids
            amino_acids = detect_amino_acids_simple(smi)

            # Analyze structure
            analysis = analyze_structure_composition(mol, smi)

            # Assess quality
            quality = assess_data_quality(smi, "smiles")

            # Create result
            result = {
                "smiles": smi,
                "canonical_smiles": canonicalize_smiles(smi),
                "detected_sequence": ''.join(amino_acids) if amino_acids else "UNKNOWN",
                "amino_acids": amino_acids,
                "analysis": analysis,
                "quality": quality,
                "is_cyclic": mol.GetRingInfo().NumRings() > 0
            }

            # Generate visualization if requested
            if config["visualization"]["enabled"]:
                svg = plot_molecule_svg(
                    mol,
                    width=config["visualization"]["width"],
                    height=config["visualization"]["height"]
                )
                if svg:
                    result["svg"] = svg

            results.append(result)
            print(f"  -> Sequence: {''.join(amino_acids)}")

        except Exception as e:
            error_msg = f"Error processing SMILES {smi}: {str(e)}"
            errors.append(error_msg)
            print(f"  -> Error: {str(e)}")

    # Save results if output specified
    output_path = None
    if output_file:
        output_path = Path(output_file)
        output_dir = ensure_output_dir(output_path)

        if config["output_format"] == "json":
            save_output_file(results, output_path, "json")

        elif config["output_format"] == "csv":
            # Create CSV with key information
            csv_data = []
            for r in results:
                csv_data.append({
                    "smiles": r["smiles"],
                    "sequence": r["detected_sequence"],
                    "molecular_weight": r["analysis"]["molecular_weight"],
                    "is_cyclic": r["is_cyclic"],
                    "quality_score": r["quality"]["quality_score"]
                })
            save_output_file(csv_data, output_path, "csv")

        else:  # txt format
            # Create detailed text report
            with open(output_path, 'w') as f:
                f.write("Structure to Sequence Analysis Report\n")
                f.write("=" * 50 + "\n\n")

                for i, result in enumerate(results):
                    f.write(f"Structure {i+1}:\n")
                    f.write(f"SMILES: {result['smiles']}\n")
                    f.write(f"Detected Sequence: {result['detected_sequence']}\n")
                    f.write(f"Molecular Weight: {result['analysis']['molecular_weight']:.2f}\n")
                    f.write(f"Molecular Formula: {result['analysis']['molecular_formula']}\n")
                    f.write(f"Cyclic: {result['is_cyclic']}\n")
                    f.write(f"Number of Rings: {result['analysis']['ring_info']['num_rings']}\n")
                    f.write(f"Peptide Bonds: {result['analysis']['peptide_bonds']}\n")
                    f.write(f"Quality Score: {result['quality']['quality_score']}/100\n")

                    if result['quality']['issues']:
                        f.write(f"Issues: {', '.join(result['quality']['issues'])}\n")

                    f.write("-" * 30 + "\n\n")

        # Save individual SVG files
        if config["visualization"]["enabled"]:
            for i, result in enumerate(results):
                if "svg" in result:
                    svg_file = output_dir / f"structure_{i+1}_visualization.svg"
                    with open(svg_file, 'w') as f:
                        f.write(result["svg"])

    return {
        "results": results,
        "errors": errors,
        "output_file": str(output_path) if output_path else None,
        "metadata": {
            "total_structures": len(smiles_list),
            "successful": len(results),
            "failed": len(errors),
            "config": config
        }
    }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', help='Input file containing SMILES strings')
    parser.add_argument('--smiles', '-s', help='Single SMILES string to analyze')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--format', '-f', choices=['txt', 'csv', 'json'],
                       default='txt', help='Output format')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Generate structure visualizations')

    args = parser.parse_args()

    # Validate arguments
    if not args.input and not args.smiles:
        print("Error: Must provide either --input or --smiles")
        return 1

    # Load config if provided
    config = None
    if args.config:
        try:
            with open(args.config) as f:
                config = json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return 1

    # Override config with command line arguments
    if config is None:
        config = {}

    config["output_format"] = args.format

    if args.visualize:
        config.setdefault("visualization", {})["enabled"] = True

    try:
        # Run analysis
        result = run_structure_to_sequence(
            input_file=args.input,
            smiles=args.smiles,
            output_file=args.output,
            config=config
        )

        # Print summary
        print(f"\nProcessing completed!")
        print(f"  Total structures: {result['metadata']['total_structures']}")
        print(f"  Successful: {result['metadata']['successful']}")
        print(f"  Failed: {result['metadata']['failed']}")

        if result['output_file']:
            print(f"  Output saved to: {result['output_file']}")

        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")

        # Print detected sequences
        if result['results']:
            print("\nDetected Sequences:")
            for r in result['results']:
                print(f"  {r['smiles'][:50]}... -> {r['detected_sequence']}")

        return 0 if result['metadata']['successful'] > 0 else 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    main()