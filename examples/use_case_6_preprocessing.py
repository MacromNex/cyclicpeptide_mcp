#!/usr/bin/env python3
"""
Use Case 6: Preprocessing and Standardization for Cyclic Peptides

This script provides comprehensive preprocessing and standardization tools for cyclic peptide
data including SMILES canonicalization, sequence validation, and data cleaning.
"""

import argparse
import sys
import os
import pandas as pd
import re

# Add parent directory to path to import cyclicpeptide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rdkit import Chem
from rdkit.Chem import AllChem
from cyclicpeptide import IOManager, Sequence2Structure, Structure2Sequence

def canonicalize_smiles(smiles):
    """
    Canonicalize SMILES string.

    Args:
        smiles (str): Input SMILES string

    Returns:
        str: Canonical SMILES string or None if invalid
    """
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None

def validate_sequence(sequence, sequence_type="essential"):
    """
    Validate amino acid sequence format.

    Args:
        sequence (str): Amino acid sequence
        sequence_type (str): Type of validation ('essential', 'extended', 'cyclic')

    Returns:
        dict: Validation results
    """
    validation_result = {
        'valid': False,
        'issues': [],
        'sequence_length': len(sequence) if sequence else 0,
        'amino_acids': []
    }

    if not sequence:
        validation_result['issues'].append("Empty sequence")
        return validation_result

    # Essential amino acids (standard 20)
    essential_aa = {'A', 'R', 'N', 'D', 'C', 'Q', 'E', 'G', 'H', 'I', 'L', 'K',
                    'M', 'F', 'P', 'S', 'T', 'W', 'Y', 'V'}

    # Extended amino acids (including non-standard)
    extended_aa = essential_aa.union({
        'Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Gln', 'Glu', 'Gly', 'His', 'Ile',
        'Leu', 'Lys', 'Met', 'Phe', 'Pro', 'Ser', 'Thr', 'Trp', 'Tyr', 'Val',
        'Orn', 'Aile', 'DL', 'D', 'Dap', 'Athr', '4OH', 'OH'
    })

    if sequence_type == "cyclic":
        # Parse cyclic peptide sequence format (e.g., 'Ala(1)--Ala--Gly--Phe(1)')
        if '--' in sequence:
            amino_acids = sequence.split('--')
            for aa in amino_acids:
                # Remove cyclic connection indicators
                clean_aa = re.sub(r'\(\d+\)', '', aa).strip()
                # Remove prefixes like "4OH-", "DL-"
                if '-' in clean_aa:
                    clean_aa = clean_aa.split('-')[-1]
                validation_result['amino_acids'].append(clean_aa)

                if clean_aa not in extended_aa:
                    validation_result['issues'].append(f"Unknown amino acid: {clean_aa}")

            # Check for proper cyclic connections
            connections = re.findall(r'\((\d+)\)', sequence)
            if len(set(connections)) * 2 != len(connections):
                validation_result['issues'].append("Mismatched cyclic connections")

        else:
            validation_result['issues'].append("Invalid cyclic sequence format (missing '--')")

    elif sequence_type == "essential":
        # Single letter code validation
        for aa in sequence:
            validation_result['amino_acids'].append(aa)
            if aa not in essential_aa:
                validation_result['issues'].append(f"Non-essential amino acid: {aa}")

    else:  # extended
        # Three letter code or mixed format
        if all(c in essential_aa for c in sequence):
            validation_result['amino_acids'] = list(sequence)
        else:
            validation_result['issues'].append("Mixed or unsupported sequence format")

    validation_result['valid'] = len(validation_result['issues']) == 0

    return validation_result

def standardize_data(input_data, output_dir="output", format="csv"):
    """
    Standardize cyclic peptide data.

    Args:
        input_data (list): List of dictionaries containing peptide data
        output_dir (str): Directory to save standardized data
        format (str): Output format ('csv', 'json', 'sdf')

    Returns:
        list: Standardized data
    """
    print(f"Standardizing {len(input_data)} records...")

    standardized_data = []
    invalid_records = []

    for i, record in enumerate(input_data):
        print(f"Processing record {i+1}/{len(input_data)}")

        standardized_record = {
            'Original_ID': record.get('id', f"Record_{i+1}"),
            'Original_SMILES': record.get('smiles', ''),
            'Original_Sequence': record.get('sequence', ''),
            'Original_Name': record.get('name', ''),
        }

        # Canonicalize SMILES
        if standardized_record['Original_SMILES']:
            canonical_smiles = canonicalize_smiles(standardized_record['Original_SMILES'])
            standardized_record['Canonical_SMILES'] = canonical_smiles
            standardized_record['SMILES_Valid'] = canonical_smiles is not None
        else:
            standardized_record['Canonical_SMILES'] = ''
            standardized_record['SMILES_Valid'] = False

        # Validate sequence
        if standardized_record['Original_Sequence']:
            # Try different sequence types
            validation_essential = validate_sequence(standardized_record['Original_Sequence'], "essential")
            validation_cyclic = validate_sequence(standardized_record['Original_Sequence'], "cyclic")

            if validation_essential['valid']:
                standardized_record['Sequence_Type'] = 'Essential'
                standardized_record['Sequence_Valid'] = True
                standardized_record['Validation_Issues'] = []
            elif validation_cyclic['valid']:
                standardized_record['Sequence_Type'] = 'Cyclic'
                standardized_record['Sequence_Valid'] = True
                standardized_record['Validation_Issues'] = []
            else:
                standardized_record['Sequence_Type'] = 'Unknown'
                standardized_record['Sequence_Valid'] = False
                standardized_record['Validation_Issues'] = (
                    validation_essential['issues'] + validation_cyclic['issues']
                )
        else:
            standardized_record['Sequence_Type'] = 'Missing'
            standardized_record['Sequence_Valid'] = False
            standardized_record['Validation_Issues'] = ['No sequence provided']

        # Calculate molecular properties if SMILES is valid
        if standardized_record['SMILES_Valid']:
            try:
                mol = Chem.MolFromSmiles(standardized_record['Canonical_SMILES'])
                standardized_record['Molecular_Weight'] = Chem.GetFormalCharge(mol)
                standardized_record['Atom_Count'] = mol.GetNumAtoms()
                standardized_record['Ring_Count'] = Chem.rdMolDescriptors.CalcNumRings(mol)
            except Exception as e:
                standardized_record['Molecular_Weight'] = None
                standardized_record['Atom_Count'] = None
                standardized_record['Ring_Count'] = None

        # Determine record quality
        if standardized_record['SMILES_Valid'] and standardized_record['Sequence_Valid']:
            standardized_record['Data_Quality'] = 'High'
            standardized_data.append(standardized_record)
        elif standardized_record['SMILES_Valid'] or standardized_record['Sequence_Valid']:
            standardized_record['Data_Quality'] = 'Medium'
            standardized_data.append(standardized_record)
        else:
            standardized_record['Data_Quality'] = 'Low'
            invalid_records.append(standardized_record)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Save standardized data
    if format == 'csv':
        if standardized_data:
            df = pd.DataFrame(standardized_data)
            output_file = os.path.join(output_dir, "standardized_data.csv")
            df.to_csv(output_file, index=False)
            print(f"Standardized data saved to: {output_file}")

        if invalid_records:
            invalid_df = pd.DataFrame(invalid_records)
            invalid_file = os.path.join(output_dir, "invalid_records.csv")
            invalid_df.to_csv(invalid_file, index=False)
            print(f"Invalid records saved to: {invalid_file}")

    elif format == 'json':
        import json
        output_file = os.path.join(output_dir, "standardized_data.json")
        with open(output_file, 'w') as f:
            json.dump({
                'standardized_data': standardized_data,
                'invalid_records': invalid_records,
                'summary': {
                    'total_records': len(input_data),
                    'valid_records': len(standardized_data),
                    'invalid_records': len(invalid_records)
                }
            }, f, indent=2)
        print(f"Standardized data saved to: {output_file}")

    # Generate summary
    summary = {
        'total_records': len(input_data),
        'valid_records': len(standardized_data),
        'invalid_records': len(invalid_records),
        'high_quality': len([r for r in standardized_data if r['Data_Quality'] == 'High']),
        'medium_quality': len([r for r in standardized_data if r['Data_Quality'] == 'Medium']),
        'low_quality': len(invalid_records)
    }

    print("\nStandardization Summary:")
    print(f"  Total records: {summary['total_records']}")
    print(f"  Valid records: {summary['valid_records']}")
    print(f"  Invalid records: {summary['invalid_records']}")
    print(f"  High quality: {summary['high_quality']}")
    print(f"  Medium quality: {summary['medium_quality']}")
    print(f"  Low quality: {summary['low_quality']}")

    return standardized_data, invalid_records, summary

def main():
    parser = argparse.ArgumentParser(description='Preprocess and standardize cyclic peptide data')
    parser.add_argument('--input', '-i', type=str, required=True,
                       help='Input file (CSV, JSON, or text file)')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--format', '-f', choices=['csv', 'json'], default='csv',
                       help='Output format (default: csv)')
    parser.add_argument('--smiles-col', type=str, default='smiles',
                       help='Name of SMILES column in input file (default: smiles)')
    parser.add_argument('--sequence-col', type=str, default='sequence',
                       help='Name of sequence column in input file (default: sequence)')
    parser.add_argument('--name-col', type=str, default='name',
                       help='Name of name column in input file (default: name)')
    parser.add_argument('--id-col', type=str, default='id',
                       help='Name of ID column in input file (default: id)')

    args = parser.parse_args()

    # Load input data
    try:
        if args.input.endswith('.csv'):
            df = pd.read_csv(args.input)
            input_data = []
            for _, row in df.iterrows():
                record = {
                    'id': row.get(args.id_col, ''),
                    'smiles': row.get(args.smiles_col, ''),
                    'sequence': row.get(args.sequence_col, ''),
                    'name': row.get(args.name_col, '')
                }
                input_data.append(record)

        elif args.input.endswith('.json'):
            import json
            with open(args.input, 'r') as f:
                data = json.load(f)
            if isinstance(data, list):
                input_data = data
            else:
                input_data = [data]

        elif args.input.endswith('.txt'):
            # Assume each line contains SMILES or sequence
            with open(args.input, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]

            input_data = []
            for i, line in enumerate(lines):
                # Try to determine if it's SMILES or sequence
                if any(c in line for c in ['(', ')', '[', ']', '=', '#']):
                    # Likely SMILES
                    input_data.append({
                        'id': f"Record_{i+1}",
                        'smiles': line,
                        'sequence': '',
                        'name': ''
                    })
                else:
                    # Likely sequence
                    input_data.append({
                        'id': f"Record_{i+1}",
                        'smiles': '',
                        'sequence': line,
                        'name': ''
                    })

        else:
            print(f"Unsupported file format: {args.input}")
            return 1

        print(f"Loaded {len(input_data)} records from {args.input}")

    except FileNotFoundError:
        print(f"Error: File {args.input} not found")
        return 1
    except Exception as e:
        print(f"Error loading input file: {e}")
        return 1

    # Perform standardization
    standardized_data, invalid_records, summary = standardize_data(
        input_data, args.output, args.format
    )

    print("Preprocessing and standardization completed successfully!")
    return 0

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("Example usage:")
        print("  python use_case_6_preprocessing.py --input examples/data/raw_peptides.csv")
        print("  python use_case_6_preprocessing.py --input examples/data/smiles.txt --format json")
        print()
        print("This script requires an input file. Creating example data...")

        # Create example data
        os.makedirs("examples/data", exist_ok=True)
        example_data = [
            {'id': 'CP001', 'smiles': 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O', 'sequence': 'APG', 'name': 'Cyclic APG'},
            {'id': 'CP002', 'smiles': 'invalid_smiles', 'sequence': 'GFPVFP', 'name': 'Linear peptide'},
            {'id': 'CP003', 'smiles': '', 'sequence': 'Ala(1)--Gly--Pro--Phe(1)', 'name': 'Cyclic AGPF'},
        ]

        example_file = "examples/data/example_peptides.csv"
        df = pd.DataFrame(example_data)
        df.to_csv(example_file, index=False)
        print(f"Created example file: {example_file}")

        sys.argv = [sys.argv[0], '--input', example_file]

    sys.exit(main())