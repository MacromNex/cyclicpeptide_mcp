#!/usr/bin/env python3
"""
Use Case 2: Structure to Sequence for Essential Amino Acids

This script converts SMILES structures back to amino acid sequences for cyclic peptides
containing only essential amino acids.
"""

import argparse
import sys
import os

# Add parent directory to path to import cyclicpeptide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from rdkit import Chem
from cyclicpeptide import Structure2Sequence, IOManager

def structure_to_sequence(smiles, output_dir="output", visualize=False):
    """
    Convert SMILES structure to amino acid sequence.

    Args:
        smiles (str): SMILES representation of the cyclic peptide
        output_dir (str): Directory to save outputs
        visualize (bool): Whether to generate structure visualization

    Returns:
        tuple: (renumbered_mol, sequence)
    """
    print(f"Processing SMILES: {smiles}")

    try:
        # Parse SMILES to molecule
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise ValueError("Invalid SMILES string")

        # Convert structure to sequence
        mol_renum, sequence = Structure2Sequence.mol2seq_for_essentialAA(mol)

        print(f"Detected sequence: {sequence}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save sequence to file
        seq_file = os.path.join(output_dir, "structure_to_sequence.txt")
        with open(seq_file, 'w') as f:
            f.write(f"SMILES: {smiles}\n")
            f.write(f"Sequence: {sequence}\n")
        print(f"Sequence saved to: {seq_file}")

        # Generate visualization if requested
        if visualize:
            svg_file = os.path.join(output_dir, "structure_visualization.svg")
            try:
                # Generate SVG visualization
                svg = IOManager.plot_smiles(smiles, w=400, h=400, isdisplay=False)
                with open(svg_file, 'w') as f:
                    f.write(svg)
                print(f"Structure visualization saved to: {svg_file}")
            except Exception as e:
                print(f"Warning: Could not generate visualization: {e}")

        return mol_renum, sequence

    except Exception as e:
        print(f"Error processing SMILES {smiles}: {e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Convert SMILES structures to amino acid sequences')
    parser.add_argument('--smiles', '-s', type=str,
                       default='C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O',
                       help='SMILES string (default: APG cyclic peptide)')
    parser.add_argument('--input', '-i', type=str,
                       help='File containing SMILES strings (one per line)')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Generate structure visualization')

    args = parser.parse_args()

    if args.input:
        # Process multiple SMILES from file
        print(f"Processing SMILES from: {args.input}")
        try:
            with open(args.input, 'r') as f:
                smiles_list = [line.strip() for line in f if line.strip()]

            results = []
            for i, smiles in enumerate(smiles_list):
                print(f"\n--- Processing SMILES {i+1}/{len(smiles_list)} ---")
                mol_renum, sequence = structure_to_sequence(smiles, args.output, args.visualize)
                if sequence:
                    results.append((smiles, sequence))
                print("-" * 50)

            # Save summary
            summary_file = os.path.join(args.output, "structure_to_sequence_summary.txt")
            with open(summary_file, 'w') as f:
                f.write("SMILES\tSequence\n")
                for smiles, sequence in results:
                    f.write(f"{smiles}\t{sequence}\n")
            print(f"Summary saved to: {summary_file}")

        except FileNotFoundError:
            print(f"Error: File {args.input} not found")
            return 1
    else:
        # Process single SMILES
        mol_renum, sequence = structure_to_sequence(args.smiles, args.output, args.visualize)

        if sequence is None:
            return 1

    print("Processing completed successfully!")
    return 0

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("Example usage:")
        print("  python use_case_2_structure_to_sequence.py --smiles 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O' --visualize")
        print("  python use_case_2_structure_to_sequence.py --input examples/data/smiles.txt")
        print()
        print("Running default example...")
        sys.argv = [sys.argv[0], '--smiles', 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O', '--visualize']

    sys.exit(main())