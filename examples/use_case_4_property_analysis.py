#!/usr/bin/env python3
"""
Use Case 4: Property Analysis for Cyclic Peptides

This script calculates comprehensive chemical and physical properties for cyclic peptides
including molecular descriptors, fingerprints, and drug-likeness rules.
"""

import argparse
import sys
import os
import json
import pandas as pd

# Add parent directory to path to import cyclicpeptide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cyclicpeptide import PropertyAnalysis as pa, IOManager

def analyze_properties(smiles, output_dir="output", format="json", visualize=False):
    """
    Analyze comprehensive properties of a cyclic peptide.

    Args:
        smiles (str): SMILES representation of the cyclic peptide
        output_dir (str): Directory to save outputs
        format (str): Output format ('json', 'csv', 'txt')
        visualize (bool): Whether to generate structure visualization

    Returns:
        dict: Dictionary containing all calculated properties
    """
    print(f"Analyzing properties for SMILES: {smiles}")

    try:
        # Calculate comprehensive properties
        properties = pa.chemial_physical_properties_from_smiles(smiles)

        if not properties:
            raise ValueError("Could not calculate properties - invalid SMILES")

        print(f"Successfully calculated {len(properties)} properties")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Save properties based on format
        if format.lower() == 'json':
            # Convert numpy arrays and other non-serializable objects to lists
            serializable_props = {}
            for key, value in properties.items():
                if hasattr(value, 'tolist'):
                    serializable_props[key] = value.tolist()
                else:
                    serializable_props[key] = value

            output_file = os.path.join(output_dir, "properties.json")
            with open(output_file, 'w') as f:
                json.dump(serializable_props, f, indent=2)

        elif format.lower() == 'csv':
            # Create DataFrame for tabular data
            df_data = []
            for key, value in properties.items():
                if isinstance(value, (list, tuple)):
                    # For fingerprints, create a summary
                    df_data.append({
                        'Property': key,
                        'Value': f"Array/List of length {len(value)}",
                        'Type': type(value).__name__
                    })
                else:
                    df_data.append({
                        'Property': key,
                        'Value': str(value),
                        'Type': type(value).__name__
                    })

            df = pd.DataFrame(df_data)
            output_file = os.path.join(output_dir, "properties.csv")
            df.to_csv(output_file, index=False)

        else:  # txt format
            output_file = os.path.join(output_dir, "properties.txt")
            with open(output_file, 'w') as f:
                f.write(f"Property Analysis for SMILES: {smiles}\n")
                f.write("=" * 60 + "\n\n")

                # Molecular Properties
                f.write("MOLECULAR PROPERTIES:\n")
                f.write("-" * 30 + "\n")
                molecular_props = ['Exact_Mass', 'Topological_Polar_Surface_Area', 'Complexity',
                                 'Crippen_LogP', 'Heavy_Atom_Count', 'Hydrogen_Bond_Donor_Count',
                                 'Hydrogen_Bond_Acceptor_Count', 'Rotatable_Bond_Count',
                                 'Formal_Charge', 'Refractivity', 'Number_of_Rings', 'Number_of_Atoms']

                for prop in molecular_props:
                    if prop in properties:
                        f.write(f"{prop}: {properties[prop]}\n")

                # Drug-likeness Rules
                f.write("\nDRUG-LIKENESS RULES:\n")
                f.write("-" * 30 + "\n")
                rule_props = ['Rule_of_Five', 'Vebers_Rule', 'Ghose_Filter']
                for prop in rule_props:
                    if prop in properties:
                        f.write(f"{prop}: {properties[prop]}\n")

                # Fingerprints
                f.write("\nFINGERPRINTS:\n")
                f.write("-" * 30 + "\n")
                fingerprint_props = ['RDKit_Fingerprint', 'Daylight_like_Fingerprint',
                                   'Morgan_Fingerprint', 'MACCS_Keys']
                for prop in fingerprint_props:
                    if prop in properties:
                        if isinstance(properties[prop], (list, tuple)):
                            f.write(f"{prop}: Array of length {len(properties[prop])}\n")
                        else:
                            f.write(f"{prop}: {properties[prop]}\n")

        print(f"Properties saved to: {output_file}")

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

        # Print key properties to console
        print("\nKey Properties:")
        print(f"  Molecular Weight: {properties.get('Exact_Mass', 'N/A')}")
        print(f"  LogP: {properties.get('Crippen_LogP', 'N/A')}")
        print(f"  TPSA: {properties.get('Topological_Polar_Surface_Area', 'N/A')}")
        print(f"  H-Bond Donors: {properties.get('Hydrogen_Bond_Donor_Count', 'N/A')}")
        print(f"  H-Bond Acceptors: {properties.get('Hydrogen_Bond_Acceptor_Count', 'N/A')}")
        print(f"  Rotatable Bonds: {properties.get('Rotatable_Bond_Count', 'N/A')}")
        print(f"  Rule of 5: {properties.get('Rule_of_Five', 'N/A')}")

        return properties

    except Exception as e:
        print(f"Error analyzing properties for {smiles}: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Analyze chemical and physical properties of cyclic peptides')
    parser.add_argument('--smiles', '-s', type=str,
                       default='C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O',
                       help='SMILES string (default: APG cyclic peptide)')
    parser.add_argument('--input', '-i', type=str,
                       help='File containing SMILES strings (one per line)')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output directory (default: output)')
    parser.add_argument('--format', '-f', choices=['json', 'csv', 'txt'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--visualize', '-v', action='store_true',
                       help='Generate structure visualization')

    args = parser.parse_args()

    if args.input:
        # Process multiple SMILES from file
        print(f"Processing SMILES from: {args.input}")
        try:
            with open(args.input, 'r') as f:
                smiles_list = [line.strip() for line in f if line.strip()]

            all_results = []
            for i, smiles in enumerate(smiles_list):
                print(f"\n--- Processing SMILES {i+1}/{len(smiles_list)} ---")

                # Create individual output directory for each structure
                individual_output = os.path.join(args.output, f"structure_{i+1}")

                properties = analyze_properties(smiles, individual_output, args.format, args.visualize)
                if properties:
                    properties['SMILES'] = smiles
                    all_results.append(properties)
                print("-" * 50)

            # Create summary for multiple structures
            if all_results and args.format == 'csv':
                summary_data = []
                for result in all_results:
                    row = {'SMILES': result['SMILES']}
                    # Add key properties to summary
                    key_props = ['Exact_Mass', 'Crippen_LogP', 'Topological_Polar_Surface_Area',
                               'Hydrogen_Bond_Donor_Count', 'Hydrogen_Bond_Acceptor_Count',
                               'Rotatable_Bond_Count', 'Rule_of_Five', 'Vebers_Rule', 'Ghose_Filter']
                    for prop in key_props:
                        row[prop] = result.get(prop, 'N/A')
                    summary_data.append(row)

                summary_df = pd.DataFrame(summary_data)
                summary_file = os.path.join(args.output, "property_analysis_summary.csv")
                summary_df.to_csv(summary_file, index=False)
                print(f"Summary saved to: {summary_file}")

        except FileNotFoundError:
            print(f"Error: File {args.input} not found")
            return 1
    else:
        # Process single SMILES
        properties = analyze_properties(args.smiles, args.output, args.format, args.visualize)

        if properties is None:
            return 1

    print("Property analysis completed successfully!")
    return 0

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("Example usage:")
        print("  python use_case_4_property_analysis.py --smiles 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O' --format csv --visualize")
        print("  python use_case_4_property_analysis.py --input examples/data/smiles.txt --format json")
        print()
        print("Running default example...")
        sys.argv = [sys.argv[0], '--smiles', 'C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O', '--format', 'txt', '--visualize']

    sys.exit(main())