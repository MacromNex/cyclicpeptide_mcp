#!/usr/bin/env python3
"""
Script: calculate_properties.py
Description: Calculate comprehensive chemical and physical properties for cyclic peptides

Original Use Case: examples/use_case_4_property_analysis.py
Dependencies Removed: cyclicpeptide.PropertyAnalysis (core functionality inlined)

Usage:
    python scripts/calculate_properties.py --input <input_file> --output <output_file>

Example:
    python scripts/calculate_properties.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --format csv --output results/properties.csv
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import sys

# Essential scientific packages
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski, Crippen, rdMolDescriptors
from rdkit.Chem import AllChem, MACCSkeys

# Add local lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.molecules import parse_smiles, plot_molecule_svg, canonicalize_smiles
from lib.io import load_input_file, save_output_file, ensure_output_dir
from lib.validation import validate_smiles, assess_data_quality

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "output_format": "json",
    "include_fingerprints": True,
    "include_descriptors": True,
    "include_drug_rules": True,
    "visualization": {
        "width": 400,
        "height": 400,
        "enabled": False
    }
}

# ==============================================================================
# Property Calculation Functions (inlined from repo)
# ==============================================================================

def calculate_molecular_descriptors(mol: Chem.Mol) -> Dict[str, Any]:
    """Calculate comprehensive molecular descriptors.

    Inlined from cyclicpeptide.PropertyAnalysis.cal_chemial_physical_properties

    Args:
        mol: RDKit molecule

    Returns:
        Dictionary of molecular descriptors
    """
    descriptors = {}

    try:
        # Basic molecular properties
        descriptors["Exact_Mass"] = Descriptors.ExactMolWt(mol)
        descriptors["Molecular_Weight"] = Descriptors.MolWt(mol)
        descriptors["Heavy_Atom_Count"] = Descriptors.HeavyAtomCount(mol)
        descriptors["Number_of_Atoms"] = mol.GetNumAtoms()
        descriptors["Number_of_Bonds"] = mol.GetNumBonds()

        # Topology descriptors
        descriptors["Topological_Polar_Surface_Area"] = Descriptors.TPSA(mol)
        descriptors["Molecular_Refractivity"] = Descriptors.MolMR(mol)
        descriptors["Balaban_J_Index"] = Descriptors.BalabanJ(mol)
        descriptors["Bertz_CT"] = Descriptors.BertzCT(mol)

        # Lipophilicity
        descriptors["Crippen_LogP"] = Crippen.MolLogP(mol)
        descriptors["Wildman_Crippen_LogP"] = Descriptors.MolLogP(mol)

        # Hydrogen bonding
        descriptors["Hydrogen_Bond_Donor_Count"] = Descriptors.NumHDonors(mol)
        descriptors["Hydrogen_Bond_Acceptor_Count"] = Descriptors.NumHAcceptors(mol)
        descriptors["Hydrogen_Bond_Donor_Sites"] = Lipinski.NumHDonors(mol)
        descriptors["Hydrogen_Bond_Acceptor_Sites"] = Lipinski.NumHAcceptors(mol)

        # Flexibility
        descriptors["Rotatable_Bond_Count"] = Descriptors.NumRotatableBonds(mol)
        descriptors["Flexibility"] = descriptors["Rotatable_Bond_Count"]

        # Charge and polarity
        descriptors["Formal_Charge"] = Chem.rdmolops.GetFormalCharge(mol)
        descriptors["Partial_Charge"] = sum(atom.GetProp("_GasteigerCharge") if atom.HasProp("_GasteigerCharge") else 0.0 for atom in mol.GetAtoms())

        # Ring analysis
        ring_info = mol.GetRingInfo()
        descriptors["Number_of_Rings"] = ring_info.NumRings()
        descriptors["Number_of_Aromatic_Rings"] = Descriptors.NumAromaticRings(mol)
        descriptors["Number_of_Saturated_Rings"] = Descriptors.NumSaturatedRings(mol)
        descriptors["Number_of_Aliphatic_Rings"] = Descriptors.NumAliphaticRings(mol)

        # Complexity measures
        descriptors["Complexity"] = Descriptors.BertzCT(mol)
        descriptors["Molecular_Complexity"] = descriptors["Complexity"]

        # Surface area and volume (if 3D coordinates available)
        try:
            descriptors["Asphericity"] = Descriptors.Asphericity(mol)
            descriptors["Eccentricity"] = Descriptors.Eccentricity(mol)
            descriptors["InertialShapeFactor"] = Descriptors.InertialShapeFactor(mol)
            descriptors["NPR1"] = Descriptors.NPR1(mol)
            descriptors["NPR2"] = Descriptors.NPR2(mol)
            descriptors["PMI1"] = Descriptors.PMI1(mol)
            descriptors["PMI2"] = Descriptors.PMI2(mol)
            descriptors["PMI3"] = Descriptors.PMI3(mol)
            descriptors["RadiusOfGyration"] = Descriptors.RadiusOfGyration(mol)
            descriptors["SpherocityIndex"] = Descriptors.SpherocityIndex(mol)
        except:
            # 3D descriptors may fail if no 3D coordinates
            pass

    except Exception as e:
        print(f"Warning: Error calculating some descriptors: {e}")

    return descriptors

def calculate_drug_likeness_rules(mol: Chem.Mol) -> Dict[str, Any]:
    """Calculate drug-likeness rule compliance.

    Inlined from cyclicpeptide.PropertyAnalysis.cal_rules

    Args:
        mol: RDKit molecule

    Returns:
        Dictionary of drug rule evaluations
    """
    rules = {}

    try:
        # Lipinski's Rule of Five
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        lipinski_violations = 0
        if mw > 500: lipinski_violations += 1
        if logp > 5: lipinski_violations += 1
        if hbd > 5: lipinski_violations += 1
        if hba > 10: lipinski_violations += 1

        rules["Rule_of_Five"] = lipinski_violations <= 1
        rules["Lipinski_Violations"] = lipinski_violations
        rules["Lipinski_MW"] = mw <= 500
        rules["Lipinski_LogP"] = logp <= 5
        rules["Lipinski_HBD"] = hbd <= 5
        rules["Lipinski_HBA"] = hba <= 10

        # Veber's Rule
        rotatable_bonds = Descriptors.NumRotatableBonds(mol)
        tpsa = Descriptors.TPSA(mol)

        veber_compliant = (rotatable_bonds <= 10) and (tpsa <= 140)
        rules["Vebers_Rule"] = veber_compliant
        rules["Veber_RotatableBonds"] = rotatable_bonds <= 10
        rules["Veber_TPSA"] = tpsa <= 140

        # Ghose Filter
        ghose_mw = 160 <= mw <= 480
        ghose_logp = -0.4 <= logp <= 5.6
        ghose_atoms = 20 <= mol.GetNumAtoms() <= 70
        ghose_mr = 40 <= Descriptors.MolMR(mol) <= 130

        rules["Ghose_Filter"] = all([ghose_mw, ghose_logp, ghose_atoms, ghose_mr])
        rules["Ghose_MW"] = ghose_mw
        rules["Ghose_LogP"] = ghose_logp
        rules["Ghose_Atoms"] = ghose_atoms
        rules["Ghose_MR"] = ghose_mr

        # Muegge Filter
        muegge_mw = 200 <= mw <= 600
        muegge_logp = -2 <= logp <= 5
        muegge_tpsa = tpsa <= 150
        muegge_rings = Descriptors.RingCount(mol) <= 7
        muegge_carbons = 4 <= sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 6) <= 35
        muegge_heteroatoms = 1 <= Descriptors.NumHeteroatoms(mol) <= 15
        muegge_rotatable = rotatable_bonds <= 15
        muegge_hbd = hbd <= 5
        muegge_hba = hba <= 10

        rules["Muegge_Filter"] = all([muegge_mw, muegge_logp, muegge_tpsa, muegge_rings,
                                     muegge_carbons, muegge_heteroatoms, muegge_rotatable,
                                     muegge_hbd, muegge_hba])

        # Lead-like properties
        leadlike_mw = 150 <= mw <= 350
        leadlike_logp = logp <= 4
        leadlike_rotatable = rotatable_bonds <= 7

        rules["Lead_Like"] = all([leadlike_mw, leadlike_logp, leadlike_rotatable])

    except Exception as e:
        print(f"Warning: Error calculating drug rules: {e}")

    return rules

def calculate_fingerprints(mol: Chem.Mol) -> Dict[str, Any]:
    """Calculate molecular fingerprints.

    Inlined from cyclicpeptide.PropertyAnalysis fingerprint functions

    Args:
        mol: RDKit molecule

    Returns:
        Dictionary of molecular fingerprints
    """
    fingerprints = {}

    try:
        # RDKit fingerprint
        rdkit_fp = Chem.RDKFingerprint(mol)
        fingerprints["RDKit_Fingerprint"] = rdkit_fp.ToBitString()
        fingerprints["RDKit_Fingerprint_Bits"] = [i for i in range(len(rdkit_fp)) if rdkit_fp[i]]

        # Morgan fingerprint (ECFP-like)
        morgan_fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=2048)
        fingerprints["Morgan_Fingerprint"] = morgan_fp.ToBitString()
        fingerprints["Morgan_Fingerprint_Bits"] = [i for i in range(len(morgan_fp)) if morgan_fp[i]]

        # MACCS keys
        maccs_fp = MACCSkeys.GenMACCSKeys(mol)
        fingerprints["MACCS_Keys"] = maccs_fp.ToBitString()
        fingerprints["MACCS_Keys_Bits"] = [i for i in range(len(maccs_fp)) if maccs_fp[i]]

        # Daylight-like fingerprint
        daylight_fp = Chem.PatternFingerprint(mol)
        fingerprints["Daylight_like_Fingerprint"] = daylight_fp.ToBitString()
        fingerprints["Daylight_like_Fingerprint_Bits"] = [i for i in range(len(daylight_fp)) if daylight_fp[i]]

        # Atom pair fingerprint
        ap_fp = AllChem.GetAtomPairFingerprintAsBitVect(mol)
        fingerprints["AtomPair_Fingerprint"] = ap_fp.ToBitString()

        # Topological torsion fingerprint
        tt_fp = AllChem.GetTopologicalTorsionFingerprintAsBitVect(mol)
        fingerprints["TopologicalTorsion_Fingerprint"] = tt_fp.ToBitString()

    except Exception as e:
        print(f"Warning: Error calculating fingerprints: {e}")

    return fingerprints

def calculate_amino_acid_composition(mol: Chem.Mol, smiles: str) -> Dict[str, Any]:
    """Calculate amino acid composition analysis.

    Args:
        mol: RDKit molecule
        smiles: SMILES string

    Returns:
        Dictionary of amino acid composition data
    """
    composition = {
        "amino_acid_count": 0,
        "amino_acid_types": [],
        "peptide_bonds": 0,
        "cyclic_peptide": False
    }

    try:
        # Check if cyclic
        composition["cyclic_peptide"] = mol.GetRingInfo().NumRings() > 0

        # Estimate peptide bonds (simplified)
        peptide_bonds = 0
        for bond in mol.GetBonds():
            begin_atom = bond.GetBeginAtom()
            end_atom = bond.GetEndAtom()

            # Look for amide bonds: C(=O)-N
            if ((begin_atom.GetAtomicNum() == 6 and end_atom.GetAtomicNum() == 7) or
                (begin_atom.GetAtomicNum() == 7 and end_atom.GetAtomicNum() == 6)):

                carbon_atom = begin_atom if begin_atom.GetAtomicNum() == 6 else end_atom

                # Check for carbonyl
                for neighbor in carbon_atom.GetNeighbors():
                    if neighbor.GetAtomicNum() == 8:
                        c_o_bond = mol.GetBondBetweenAtoms(carbon_atom.GetIdx(), neighbor.GetIdx())
                        if c_o_bond and c_o_bond.GetBondType() == Chem.BondType.DOUBLE:
                            peptide_bonds += 1
                            break

        composition["peptide_bonds"] = peptide_bonds

        # Estimate amino acid count (rough approximation)
        if peptide_bonds > 0:
            composition["amino_acid_count"] = peptide_bonds + (1 if composition["cyclic_peptide"] else 1)
        else:
            # Fallback estimation
            nitrogen_count = sum(1 for atom in mol.GetAtoms() if atom.GetAtomicNum() == 7)
            composition["amino_acid_count"] = max(1, nitrogen_count)

    except Exception as e:
        print(f"Warning: Error calculating amino acid composition: {e}")

    return composition

# ==============================================================================
# Core Function
# ==============================================================================
def run_calculate_properties(
    input_file: Union[str, Path, None] = None,
    smiles: Optional[str] = None,
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Calculate comprehensive chemical and physical properties for cyclic peptides.

    Args:
        input_file: Path to input file containing SMILES
        smiles: Single SMILES string to analyze
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
            print(f"Calculating properties for structure {i+1}/{len(smiles_list)}: {smi[:50]}...")

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

            # Calculate properties
            properties = {
                "SMILES": smi,
                "Canonical_SMILES": canonicalize_smiles(smi)
            }

            # Molecular descriptors
            if config["include_descriptors"]:
                descriptors = calculate_molecular_descriptors(mol)
                properties.update(descriptors)

            # Drug-likeness rules
            if config["include_drug_rules"]:
                drug_rules = calculate_drug_likeness_rules(mol)
                properties.update(drug_rules)

            # Fingerprints
            if config["include_fingerprints"]:
                fingerprints = calculate_fingerprints(mol)
                properties.update(fingerprints)

            # Amino acid composition
            aa_composition = calculate_amino_acid_composition(mol, smi)
            properties.update(aa_composition)

            # Quality assessment
            quality = assess_data_quality(smi, "smiles")
            properties["quality_score"] = quality["quality_score"]
            properties["quality_issues"] = quality["issues"]

            # Generate visualization if requested
            if config["visualization"]["enabled"]:
                svg = plot_molecule_svg(
                    mol,
                    width=config["visualization"]["width"],
                    height=config["visualization"]["height"]
                )
                if svg:
                    properties["svg"] = svg

            results.append(properties)

            # Print key properties
            print(f"  MW: {properties.get('Exact_Mass', 'N/A'):.2f}")
            print(f"  LogP: {properties.get('Crippen_LogP', 'N/A'):.2f}")
            print(f"  TPSA: {properties.get('Topological_Polar_Surface_Area', 'N/A'):.2f}")
            print(f"  Rule of 5: {properties.get('Rule_of_Five', 'N/A')}")

        except Exception as e:
            error_msg = f"Error calculating properties for {smi}: {str(e)}"
            errors.append(error_msg)
            print(f"  -> Error: {str(e)}")

    # Save results if output specified
    output_path = None
    if output_file:
        output_path = Path(output_file)
        output_dir = ensure_output_dir(output_path)

        # Convert fingerprint bit strings to lists for JSON serialization
        if config["output_format"] == "json":
            serializable_results = []
            for result in results:
                serializable_result = {}
                for key, value in result.items():
                    if isinstance(value, str) and key.endswith('_Fingerprint'):
                        # Convert bit string to list of indices
                        serializable_result[key + '_Indices'] = [i for i, bit in enumerate(value) if bit == '1']
                    else:
                        serializable_result[key] = value
                serializable_results.append(serializable_result)
            save_output_file(serializable_results, output_path, "json")

        elif config["output_format"] == "csv":
            # Create CSV with key properties only (fingerprints are too large)
            csv_data = []
            key_properties = [
                'SMILES', 'Canonical_SMILES', 'Exact_Mass', 'Molecular_Weight',
                'Crippen_LogP', 'Topological_Polar_Surface_Area', 'Hydrogen_Bond_Donor_Count',
                'Hydrogen_Bond_Acceptor_Count', 'Rotatable_Bond_Count', 'Number_of_Rings',
                'Rule_of_Five', 'Vebers_Rule', 'Ghose_Filter', 'amino_acid_count',
                'peptide_bonds', 'cyclic_peptide', 'quality_score'
            ]

            for result in results:
                csv_row = {}
                for prop in key_properties:
                    csv_row[prop] = result.get(prop, 'N/A')
                csv_data.append(csv_row)

            save_output_file(csv_data, output_path, "csv")

        else:  # txt format
            with open(output_path, 'w') as f:
                f.write("Cyclic Peptide Property Analysis Report\n")
                f.write("=" * 60 + "\n\n")

                for i, result in enumerate(results):
                    f.write(f"Structure {i+1}:\n")
                    f.write(f"SMILES: {result['SMILES']}\n")
                    f.write(f"Canonical SMILES: {result['Canonical_SMILES']}\n\n")

                    f.write("MOLECULAR PROPERTIES:\n")
                    f.write("-" * 30 + "\n")
                    molecular_props = ['Exact_Mass', 'Molecular_Weight', 'Heavy_Atom_Count',
                                     'Number_of_Atoms', 'Number_of_Rings', 'Number_of_Bonds']
                    for prop in molecular_props:
                        if prop in result:
                            f.write(f"{prop}: {result[prop]}\n")

                    f.write("\nLIPOPHILICITY & POLARITY:\n")
                    f.write("-" * 30 + "\n")
                    lipo_props = ['Crippen_LogP', 'Topological_Polar_Surface_Area', 'Molecular_Refractivity']
                    for prop in lipo_props:
                        if prop in result:
                            f.write(f"{prop}: {result[prop]:.3f}\n")

                    f.write("\nHYDROGEN BONDING:\n")
                    f.write("-" * 30 + "\n")
                    hb_props = ['Hydrogen_Bond_Donor_Count', 'Hydrogen_Bond_Acceptor_Count']
                    for prop in hb_props:
                        if prop in result:
                            f.write(f"{prop}: {result[prop]}\n")

                    f.write("\nDRUG-LIKENESS RULES:\n")
                    f.write("-" * 30 + "\n")
                    rule_props = ['Rule_of_Five', 'Vebers_Rule', 'Ghose_Filter', 'Lead_Like']
                    for prop in rule_props:
                        if prop in result:
                            f.write(f"{prop}: {result[prop]}\n")

                    f.write("\nPEPTIDE PROPERTIES:\n")
                    f.write("-" * 30 + "\n")
                    peptide_props = ['amino_acid_count', 'peptide_bonds', 'cyclic_peptide']
                    for prop in peptide_props:
                        if prop in result:
                            f.write(f"{prop}: {result[prop]}\n")

                    f.write("\nQUALITY ASSESSMENT:\n")
                    f.write("-" * 30 + "\n")
                    f.write(f"Quality Score: {result.get('quality_score', 'N/A')}/100\n")
                    if result.get('quality_issues'):
                        f.write(f"Issues: {', '.join(result['quality_issues'])}\n")

                    f.write("-" * 60 + "\n\n")

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
            "properties_calculated": len([k for k in results[0].keys() if not k.startswith('svg')]) if results else 0,
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
    parser.add_argument('--format', '-f', choices=['json', 'csv', 'txt'],
                       default='json', help='Output format')
    parser.add_argument('--no-fingerprints', action='store_true',
                       help='Skip fingerprint calculation')
    parser.add_argument('--no-descriptors', action='store_true',
                       help='Skip molecular descriptor calculation')
    parser.add_argument('--no-drug-rules', action='store_true',
                       help='Skip drug-likeness rule evaluation')
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
    config["include_fingerprints"] = not args.no_fingerprints
    config["include_descriptors"] = not args.no_descriptors
    config["include_drug_rules"] = not args.no_drug_rules

    if args.visualize:
        config.setdefault("visualization", {})["enabled"] = True

    try:
        # Run property calculation
        result = run_calculate_properties(
            input_file=args.input,
            smiles=args.smiles,
            output_file=args.output,
            config=config
        )

        # Print summary
        print(f"\nProperty calculation completed!")
        print(f"  Total structures: {result['metadata']['total_structures']}")
        print(f"  Successful: {result['metadata']['successful']}")
        print(f"  Failed: {result['metadata']['failed']}")
        print(f"  Properties calculated: {result['metadata']['properties_calculated']}")

        if result['output_file']:
            print(f"  Output saved to: {result['output_file']}")

        if result['errors']:
            print("\nErrors:")
            for error in result['errors']:
                print(f"  - {error}")

        return 0 if result['metadata']['successful'] > 0 else 1

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    main()