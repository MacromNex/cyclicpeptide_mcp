#!/usr/bin/env python3
"""
Use Case 1: Sequence to Structure for Essential Amino Acids

This script converts amino acid sequences to SMILES representations for cyclic peptides.
Only works with essential amino acids (standard 20 amino acids).
"""

import argparse
import sys
import os

# Add parent directory to path to import cyclicpeptide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cyclicpeptide import Sequence2Structure, IOManager

def sequence_to_structure(sequence, cyclic=True, output_dir="output", visualize=False):
    """
    Convert amino acid sequence to SMILES structure.

    Args:
        sequence (str): Amino acid sequence using standard 3-letter codes or 1-letter codes
        cyclic (bool): Whether to create a cyclic peptide
        output_dir (str): Directory to save outputs
        visualize (bool): Whether to generate structure visualization

    Returns:
        tuple: (SMILES string, peptide object)
    """
    print(f"Processing sequence: {sequence}")
    print(f"Cyclic peptide: {cyclic}")

    try:
        # Convert sequence to structure
        smiles, peptide = Sequence2Structure.seq2stru_essentialAA(sequence=sequence, cyclic=cyclic)

        print(f"Generated SMILES: {smiles}")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save SMILES to file
        smiles_file = os.path.join(output_dir, f"{sequence}_{'cyclic' if cyclic else 'linear'}.smi")
        with open(smiles_file, 'w') as f:
            f.write(f"{smiles}\t{sequence}\n")
        print(f"SMILES saved to: {smiles_file}")

        # Generate visualization if requested
        if visualize:
            svg_file = os.path.join(output_dir, f"{sequence}_{'cyclic' if cyclic else 'linear'}.svg")
            try:
                # Generate SVG visualization
                svg = IOManager.plot_smiles(smiles, w=400, h=400, isdisplay=False)
                with open(svg_file, 'w') as f:
                    f.write(svg)
                print(f"Structure visualization saved to: {svg_file}")
            except Exception as e:
                print(f"Warning: Could not generate visualization: {e}")

        return smiles, peptide

    except Exception as e:
        print(f"Error processing sequence {sequence}: {e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Convert amino acid sequences to structures')
    parser.add_argument('--sequence', '-s', type=str, default='APG',
                       help='Amino acid sequence (default: APG)')
    parser.add_argument('--linear', action='store_true',
                       help='Create linear peptide instead of cyclic (default: cyclic)')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Generate structure visualization')
    parser.add_argument('--batch', '-b', type=str,
                       help='File containing multiple sequences (one per line)')

    args = parser.parse_args()

    cyclic = not args.linear

    if args.batch:
        # Process multiple sequences from file
        print(f"Processing sequences from: {args.batch}")
        try:
            with open(args.batch, 'r') as f:
                sequences = [line.strip() for line in f if line.strip()]

            results = []
            for seq in sequences:
                smiles, peptide = sequence_to_structure(seq, cyclic, args.output, args.visualize)
                if smiles:
                    results.append((seq, smiles))
                print("-" * 50)

            # Save summary
            summary_file = os.path.join(args.output, "sequence_to_structure_summary.txt")
            with open(summary_file, 'w') as f:
                f.write("Sequence\tSMILES\tType\n")
                for seq, smiles in results:
                    f.write(f"{seq}\t{smiles}\t{'cyclic' if cyclic else 'linear'}\n")
            print(f"Summary saved to: {summary_file}")

        except FileNotFoundError:
            print(f"Error: File {args.batch} not found")
            return 1
    else:
        # Process single sequence
        smiles, peptide = sequence_to_structure(args.sequence, cyclic, args.output, args.visualize)

        if smiles is None:
            return 1

    print("Processing completed successfully!")
    return 0

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("Example usage:")
        print("  python use_case_1_sequence_to_structure.py --sequence APG --visualize")
        print("  python use_case_1_sequence_to_structure.py --sequence GFPVFP --linear")
        print("  python use_case_1_sequence_to_structure.py --batch examples/data/sequences.txt")
        print()
        print("Running default example...")
        sys.argv = [sys.argv[0], '--sequence', 'APG', '--visualize']

    sys.exit(main())