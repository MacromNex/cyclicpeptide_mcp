#!/usr/bin/env python3
"""
Script: analyze_structure.py
Description: Generate comprehensive structure analysis reports for cyclic peptides

Original Use Case: examples/use_case_3_structure_analysis.py
Dependencies Removed: cyclicpeptide.Structure2Sequence.transform (functionality inlined)

Usage:
    python scripts/analyze_structure.py --input <input_file> --output <output_file>

Example:
    python scripts/analyze_structure.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --output results/analysis.html
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
from pathlib import Path
from typing import Union, Optional, Dict, Any, List
import json
import sys
from datetime import datetime

# Essential scientific packages
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

# Add local lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.molecules import (parse_smiles, plot_molecule_svg, canonicalize_smiles,
                          calculate_molecular_weight, count_atoms, count_rings)
from lib.io import load_input_file, save_output_file, ensure_output_dir
from lib.validation import validate_smiles, validate_cyclic_peptide, assess_data_quality

# Import property calculation functions from calculate_properties.py
try:
    from calculate_properties import (calculate_molecular_descriptors,
                                    calculate_drug_likeness_rules,
                                    calculate_amino_acid_composition)
except ImportError:
    # Fallback if import fails
    def calculate_molecular_descriptors(mol):
        return {"error": "Could not import property calculation functions"}
    def calculate_drug_likeness_rules(mol):
        return {"error": "Could not import property calculation functions"}
    def calculate_amino_acid_composition(mol, smiles):
        return {"error": "Could not import property calculation functions"}

# Import sequence detection from structure_to_sequence.py
try:
    from structure_to_sequence import detect_amino_acids_simple, analyze_structure_composition
except ImportError:
    def detect_amino_acids_simple(smiles):
        return ["X"]  # Unknown
    def analyze_structure_composition(mol, smiles):
        return {"error": "Could not import structure analysis functions"}

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "output_format": "html",
    "include_visualization": True,
    "include_properties": True,
    "include_sequence_analysis": True,
    "include_drug_rules": True,
    "visualization": {
        "width": 600,
        "height": 400,
        "style": "detailed"
    },
    "analysis": {
        "detailed_breakdown": True,
        "comparative_analysis": False
    }
}

# ==============================================================================
# HTML Report Generation Functions
# ==============================================================================

def generate_html_header(title: str = "Cyclic Peptide Structure Analysis") -> str:
    """Generate HTML header with CSS styling."""
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            color: #7f8c8d;
            margin-top: 10px;
            font-size: 1.1em;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            background-color: #fafafa;
        }}
        .section h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .section h3 {{
            color: #2980b9;
            margin-top: 25px;
        }}
        .property-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }}
        .property-item {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        .property-label {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .property-value {{
            font-size: 1.1em;
            color: #27ae60;
        }}
        .molecule-viz {{
            text-align: center;
            margin: 20px 0;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
        }}
        .quality-indicator {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 15px;
            color: white;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .quality-high {{ background-color: #27ae60; }}
        .quality-medium {{ background-color: #f39c12; }}
        .quality-low {{ background-color: #e74c3c; }}
        .quality-very-low {{ background-color: #8e44ad; }}
        .warning-box {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .error-box {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .success-box {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e1e8ed;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
"""

def generate_structure_overview_html(smiles: str, analysis: Dict[str, Any],
                                   svg_visualization: Optional[str] = None) -> str:
    """Generate structure overview section."""
    html = """
        <div class="section">
            <h2>🧬 Structure Overview</h2>
    """

    # Basic information
    html += f"""
            <div class="property-grid">
                <div class="property-item">
                    <div class="property-label">SMILES String</div>
                    <div class="property-value" style="font-family: monospace; word-break: break-all;">{smiles}</div>
                </div>
                <div class="property-item">
                    <div class="property-label">Canonical SMILES</div>
                    <div class="property-value" style="font-family: monospace; word-break: break-all;">{analysis.get('canonical_smiles', 'N/A')}</div>
                </div>
                <div class="property-item">
                    <div class="property-label">Molecular Formula</div>
                    <div class="property-value">{analysis.get('molecular_formula', 'N/A')}</div>
                </div>
                <div class="property-item">
                    <div class="property-label">Molecular Weight</div>
                    <div class="property-value">{analysis.get('molecular_weight', 'N/A'):.2f} g/mol</div>
                </div>
            </div>
    """

    # Visualization
    if svg_visualization:
        html += f"""
            <div class="molecule-viz">
                <h3>Structure Visualization</h3>
                {svg_visualization}
            </div>
        """

    html += """
        </div>
    """

    return html

def generate_sequence_analysis_html(sequence_info: Dict[str, Any]) -> str:
    """Generate sequence analysis section."""
    html = """
        <div class="section">
            <h2>🧪 Sequence Analysis</h2>
    """

    detected_seq = sequence_info.get('detected_sequence', 'Unknown')
    amino_acids = sequence_info.get('amino_acids', [])

    if detected_seq != "Unknown" and amino_acids:
        html += f"""
            <div class="success-box">
                <strong>Detected Sequence:</strong> {detected_seq}
            </div>

            <h3>Amino Acid Composition</h3>
            <div class="property-grid">
        """

        # Count amino acid frequencies
        aa_count = {}
        for aa in amino_acids:
            aa_count[aa] = aa_count.get(aa, 0) + 1

        for aa, count in aa_count.items():
            aa_name = {
                'A': 'Alanine', 'R': 'Arginine', 'N': 'Asparagine', 'D': 'Aspartic acid',
                'C': 'Cysteine', 'E': 'Glutamic acid', 'Q': 'Glutamine', 'G': 'Glycine',
                'H': 'Histidine', 'I': 'Isoleucine', 'L': 'Leucine', 'K': 'Lysine',
                'M': 'Methionine', 'F': 'Phenylalanine', 'P': 'Proline', 'S': 'Serine',
                'T': 'Threonine', 'W': 'Tryptophan', 'Y': 'Tyrosine', 'V': 'Valine'
            }.get(aa, aa)

            html += f"""
                <div class="property-item">
                    <div class="property-label">{aa_name} ({aa})</div>
                    <div class="property-value">{count} residue{'s' if count > 1 else ''}</div>
                </div>
            """

        html += """
            </div>
        """
    else:
        html += """
            <div class="warning-box">
                <strong>Sequence Detection:</strong> Could not reliably identify amino acid sequence from structure.
                This may indicate a non-standard cyclic peptide or complex modifications.
            </div>
        """

    html += """
        </div>
    """

    return html

def generate_properties_html(properties: Dict[str, Any]) -> str:
    """Generate molecular properties section."""
    html = """
        <div class="section">
            <h2>⚗️ Molecular Properties</h2>

            <h3>Basic Molecular Descriptors</h3>
            <div class="property-grid">
    """

    # Key molecular properties
    key_props = [
        ('Exact_Mass', 'Exact Mass', 'g/mol', '.3f'),
        ('Heavy_Atom_Count', 'Heavy Atoms', '', 'd'),
        ('Number_of_Rings', 'Ring Count', '', 'd'),
        ('Topological_Polar_Surface_Area', 'TPSA', 'Ų', '.2f'),
        ('Crippen_LogP', 'LogP', '', '.2f'),
        ('Hydrogen_Bond_Donor_Count', 'H-Bond Donors', '', 'd'),
        ('Hydrogen_Bond_Acceptor_Count', 'H-Bond Acceptors', '', 'd'),
        ('Rotatable_Bond_Count', 'Rotatable Bonds', '', 'd')
    ]

    for prop_key, label, unit, format_spec in key_props:
        value = properties.get(prop_key, 'N/A')
        if isinstance(value, (int, float)) and value is not None:
            if format_spec.endswith('f'):
                formatted_value = f"{value:{format_spec}}"
            else:
                formatted_value = f"{value:{format_spec}}"
            display_value = f"{formatted_value} {unit}".strip()
        else:
            display_value = str(value)

        html += f"""
            <div class="property-item">
                <div class="property-label">{label}</div>
                <div class="property-value">{display_value}</div>
            </div>
        """

    html += """
            </div>
        </div>
    """

    return html

def generate_drug_rules_html(drug_rules: Dict[str, Any]) -> str:
    """Generate drug-likeness rules section."""
    html = """
        <div class="section">
            <h2>💊 Drug-Likeness Assessment</h2>

            <h3>Rule-of-Five Analysis</h3>
            <table>
                <tr><th>Rule</th><th>Value</th><th>Limit</th><th>Status</th></tr>
    """

    # Lipinski's Rule of 5
    rules_data = [
        ('Molecular Weight', drug_rules.get('Exact_Mass', 'N/A'), '≤ 500 Da',
         '✅ Pass' if drug_rules.get('Lipinski_MW', False) else '❌ Fail'),
        ('LogP', drug_rules.get('Crippen_LogP', 'N/A'), '≤ 5',
         '✅ Pass' if drug_rules.get('Lipinski_LogP', False) else '❌ Fail'),
        ('H-Bond Donors', drug_rules.get('Hydrogen_Bond_Donor_Count', 'N/A'), '≤ 5',
         '✅ Pass' if drug_rules.get('Lipinski_HBD', False) else '❌ Fail'),
        ('H-Bond Acceptors', drug_rules.get('Hydrogen_Bond_Acceptor_Count', 'N/A'), '≤ 10',
         '✅ Pass' if drug_rules.get('Lipinski_HBA', False) else '❌ Fail')
    ]

    for rule, value, limit, status in rules_data:
        if isinstance(value, float):
            value = f"{value:.2f}"
        html += f"<tr><td>{rule}</td><td>{value}</td><td>{limit}</td><td>{status}</td></tr>"

    html += """
            </table>

            <h3>Overall Drug-Likeness</h3>
            <div class="property-grid">
    """

    # Overall assessments
    assessments = [
        ('Lipinski Rule of 5', drug_rules.get('Rule_of_Five', False)),
        ('Veber Rule', drug_rules.get('Vebers_Rule', False)),
        ('Ghose Filter', drug_rules.get('Ghose_Filter', False)),
        ('Lead-like Properties', drug_rules.get('Lead_Like', False))
    ]

    for rule_name, passes in assessments:
        status = "✅ Pass" if passes else "❌ Fail"
        color = "#27ae60" if passes else "#e74c3c"

        html += f"""
            <div class="property-item">
                <div class="property-label">{rule_name}</div>
                <div class="property-value" style="color: {color}; font-weight: bold;">{status}</div>
            </div>
        """

    html += """
            </div>
        </div>
    """

    return html

def generate_quality_html(quality: Dict[str, Any]) -> str:
    """Generate quality assessment section."""
    html = """
        <div class="section">
            <h2>🎯 Quality Assessment</h2>
    """

    score = quality.get('quality_score', 0)
    category = quality.get('category', 'unknown')

    quality_class = f"quality-{category.replace('_', '-')}"

    html += f"""
            <div class="property-grid">
                <div class="property-item">
                    <div class="property-label">Overall Quality Score</div>
                    <div class="property-value">
                        {score}/100
                        <span class="quality-indicator {quality_class}">{category.replace('_', ' ').title()}</span>
                    </div>
                </div>
            </div>
    """

    # Issues and warnings
    if quality.get('issues') or quality.get('warnings'):
        html += "<h3>Quality Notes</h3>"

        if quality.get('issues'):
            html += "<div class='error-box'><strong>Issues:</strong><ul>"
            for issue in quality['issues']:
                html += f"<li>{issue}</li>"
            html += "</ul></div>"

        if quality.get('warnings'):
            html += "<div class='warning-box'><strong>Warnings:</strong><ul>"
            for warning in quality['warnings']:
                html += f"<li>{warning}</li>"
            html += "</ul></div>"

    html += """
        </div>
    """

    return html

def generate_html_footer() -> str:
    """Generate HTML footer."""
    return """
        <div class="footer">
            Generated by Cyclic Peptide MCP Structure Analysis Tool<br>
            <em>This analysis is for research purposes only</em>
        </div>
    </div>
</body>
</html>
"""

# ==============================================================================
# Core Function
# ==============================================================================
def run_analyze_structure(
    input_file: Union[str, Path, None] = None,
    smiles: Optional[str] = None,
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate comprehensive structure analysis for cyclic peptides.

    Args:
        input_file: Path to input file containing SMILES
        smiles: Single SMILES string to analyze
        output_file: Path to save analysis report
        config: Configuration dict
        **kwargs: Override config parameters

    Returns:
        Dict containing analysis results and metadata
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
            print(f"Analyzing structure {i+1}/{len(smiles_list)}: {smi[:50]}...")

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

            # Basic analysis
            basic_analysis = {
                "smiles": smi,
                "canonical_smiles": canonicalize_smiles(smi),
                "molecular_formula": rdMolDescriptors.CalcMolFormula(mol),
                "molecular_weight": Descriptors.ExactMolWt(mol),
                "num_atoms": mol.GetNumAtoms(),
                "num_rings": mol.GetRingInfo().NumRings(),
                "is_cyclic": mol.GetRingInfo().NumRings() > 0
            }

            # Quality assessment
            quality = assess_data_quality(smi, "smiles")

            # Sequence analysis
            sequence_info = {
                "detected_sequence": ''.join(detect_amino_acids_simple(smi)),
                "amino_acids": detect_amino_acids_simple(smi),
                "composition_analysis": analyze_structure_composition(mol, smi)
            }

            # Molecular properties
            properties = {}
            if config.get("include_properties", True):
                properties = calculate_molecular_descriptors(mol)

            # Drug-likeness rules
            drug_rules = {}
            if config.get("include_drug_rules", True):
                drug_rules = calculate_drug_likeness_rules(mol)

            # Generate visualization
            svg_viz = None
            if config.get("include_visualization", True):
                svg_viz = plot_molecule_svg(
                    mol,
                    width=config["visualization"]["width"],
                    height=config["visualization"]["height"]
                )

            # Compile complete analysis
            complete_analysis = {
                "basic_analysis": basic_analysis,
                "sequence_info": sequence_info,
                "properties": properties,
                "drug_rules": drug_rules,
                "quality": quality,
                "svg_visualization": svg_viz
            }

            results.append(complete_analysis)
            print(f"  -> Analysis complete. Quality: {quality['quality_score']}/100")

        except Exception as e:
            error_msg = f"Error analyzing structure {smi}: {str(e)}"
            errors.append(error_msg)
            print(f"  -> Error: {str(e)}")

    # Generate reports if output specified
    output_path = None
    if output_file and results:
        output_path = Path(output_file)
        output_dir = ensure_output_dir(output_path)

        if config["output_format"] == "html":
            # Generate HTML reports
            if len(results) == 1:
                # Single structure report
                analysis = results[0]
                html_content = generate_html_header("Cyclic Peptide Structure Analysis")
                html_content += generate_structure_overview_html(
                    analysis["basic_analysis"]["smiles"],
                    analysis["basic_analysis"],
                    analysis["svg_visualization"]
                )

                if config.get("include_sequence_analysis", True):
                    html_content += generate_sequence_analysis_html(analysis["sequence_info"])

                if config.get("include_properties", True):
                    html_content += generate_properties_html(analysis["properties"])

                if config.get("include_drug_rules", True):
                    html_content += generate_drug_rules_html({**analysis["properties"], **analysis["drug_rules"]})

                html_content += generate_quality_html(analysis["quality"])
                html_content += generate_html_footer()

                with open(output_path, 'w') as f:
                    f.write(html_content)
            else:
                # Multiple structure reports
                for i, analysis in enumerate(results):
                    report_file = output_dir / f"structure_analysis_{i+1}.html"

                    html_content = generate_html_header(f"Structure Analysis {i+1}")
                    html_content += generate_structure_overview_html(
                        analysis["basic_analysis"]["smiles"],
                        analysis["basic_analysis"],
                        analysis["svg_visualization"]
                    )

                    if config.get("include_sequence_analysis", True):
                        html_content += generate_sequence_analysis_html(analysis["sequence_info"])

                    if config.get("include_properties", True):
                        html_content += generate_properties_html(analysis["properties"])

                    if config.get("include_drug_rules", True):
                        html_content += generate_drug_rules_html({**analysis["properties"], **analysis["drug_rules"]})

                    html_content += generate_quality_html(analysis["quality"])
                    html_content += generate_html_footer()

                    with open(report_file, 'w') as f:
                        f.write(html_content)

                output_path = output_dir / "structure_analysis_summary.txt"
                with open(output_path, 'w') as f:
                    f.write("Structure Analysis Summary\n")
                    f.write("=" * 30 + "\n\n")
                    for i, analysis in enumerate(results):
                        f.write(f"Structure {i+1}:\n")
                        f.write(f"  SMILES: {analysis['basic_analysis']['smiles']}\n")
                        f.write(f"  Sequence: {analysis['sequence_info']['detected_sequence']}\n")
                        f.write(f"  Quality: {analysis['quality']['quality_score']}/100\n")
                        f.write(f"  Report: structure_analysis_{i+1}.html\n\n")

        elif config["output_format"] == "json":
            # Save as JSON
            save_output_file(results, output_path, "json")

        elif config["output_format"] == "csv":
            # Create summary CSV
            csv_data = []
            for analysis in results:
                row = {
                    "smiles": analysis["basic_analysis"]["smiles"],
                    "detected_sequence": analysis["sequence_info"]["detected_sequence"],
                    "molecular_weight": analysis["basic_analysis"]["molecular_weight"],
                    "num_rings": analysis["basic_analysis"]["num_rings"],
                    "quality_score": analysis["quality"]["quality_score"],
                    "lipinski_compliant": analysis["drug_rules"].get("Rule_of_Five", False)
                }
                csv_data.append(row)
            save_output_file(csv_data, output_path, "csv")

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
    parser.add_argument('--format', '-f', choices=['html', 'json', 'csv'],
                       default='html', help='Output format')
    parser.add_argument('--no-visualization', action='store_true',
                       help='Skip structure visualization')
    parser.add_argument('--no-properties', action='store_true',
                       help='Skip molecular properties calculation')
    parser.add_argument('--no-sequence', action='store_true',
                       help='Skip sequence analysis')
    parser.add_argument('--no-drug-rules', action='store_true',
                       help='Skip drug-likeness analysis')

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
    config["include_visualization"] = not args.no_visualization
    config["include_properties"] = not args.no_properties
    config["include_sequence_analysis"] = not args.no_sequence
    config["include_drug_rules"] = not args.no_drug_rules

    try:
        # Run analysis
        result = run_analyze_structure(
            input_file=args.input,
            smiles=args.smiles,
            output_file=args.output,
            config=config
        )

        # Print summary
        print(f"\nStructure analysis completed!")
        print(f"  Total structures: {result['metadata']['total_structures']}")
        print(f"  Successful: {result['metadata']['successful']}")
        print(f"  Failed: {result['metadata']['failed']}")

        if result['output_file']:
            print(f"  Analysis report saved to: {result['output_file']}")

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