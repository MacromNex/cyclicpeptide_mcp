#!/usr/bin/env python3
"""
Use Case 3: General Structure Analysis with Custom Monomer Database

This script performs comprehensive structure analysis for any cyclic peptide using
a custom monomer database, not limited to essential amino acids.
"""

import argparse
import sys
import os

# Add parent directory to path to import cyclicpeptide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cyclicpeptide import Structure2Sequence, IOManager

def structure_analysis(smiles, monomers_path="", output_dir="output", visualize=False):
    """
    Perform comprehensive structure analysis using custom monomer database.

    Args:
        smiles (str): SMILES representation of the cyclic peptide
        monomers_path (str): Path to custom monomer database file (empty = use default)
        output_dir (str): Directory to save outputs
        visualize (bool): Whether to generate structure visualization

    Returns:
        str: HTML report of the analysis
    """
    print(f"Processing SMILES: {smiles}")
    print(f"Monomer database: {monomers_path if monomers_path else 'default'}")

    try:
        # Perform structure transformation analysis
        html_report = Structure2Sequence.transform(smiles, monomers_path=monomers_path)

        print("Analysis completed successfully!")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save HTML report
        report_file = os.path.join(output_dir, "structure_analysis_report.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"HTML report saved to: {report_file}")

        # Generate visualization if requested
        if visualize:
            svg_file = os.path.join(output_dir, "input_structure_visualization.svg")
            try:
                # Generate SVG visualization
                svg = IOManager.plot_smiles(smiles, w=400, h=400, isdisplay=False)
                with open(svg_file, 'w') as f:
                    f.write(svg)
                print(f"Structure visualization saved to: {svg_file}")
            except Exception as e:
                print(f"Warning: Could not generate visualization: {e}")

        return html_report

    except Exception as e:
        print(f"Error analyzing structure {smiles}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Analyze cyclic peptide structures with custom monomer database')
    parser.add_argument('--smiles', '-s', type=str,
                       default='C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O',
                       help='SMILES string (default: APG cyclic peptide)')
    parser.add_argument('--input', '-i', type=str,
                       help='File containing SMILES strings (one per line)')
    parser.add_argument('--monomers', '-m', type=str, default="",
                       help='Path to custom monomer database file (default: use built-in database)')
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

            for i, smiles in enumerate(smiles_list):
                print(f"\n--- Processing SMILES {i+1}/{len(smiles_list)} ---")

                # Create individual output directory for each structure
                individual_output = os.path.join(args.output, f"structure_{i+1}")

                html_report = structure_analysis(smiles, args.monomers, individual_output, args.visualize)
                if html_report is None:
                    print(f"Failed to analyze structure {i+1}")
                print("-" * 50)

            print(f"All analyses saved to: {args.output}")

        except FileNotFoundError:
            print(f"Error: File {args.input} not found")
            return 1
    else:
        # Process single SMILES
        html_report = structure_analysis(args.smiles, args.monomers, args.output, args.visualize)

        if html_report is None:
            return 1

    print("Analysis completed successfully!")
    return 0

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("Example usage:")
        print("  python use_case_3_structure_analysis.py --smiles 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O' --visualize")
        print("  python use_case_3_structure_analysis.py --input examples/data/smiles.txt --monomers examples/data/custom_monomers.tsv")
        print("  python use_case_3_structure_analysis.py --smiles 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CC(CCCCC)CN2C1=O'")
        print()
        print("Running default example...")
        sys.argv = [sys.argv[0], '--smiles', 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O', '--visualize']

    sys.exit(main())