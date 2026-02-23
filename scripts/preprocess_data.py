#!/usr/bin/env python3
"""
Script: preprocess_data.py
Description: Preprocessing and standardization for cyclic peptide data

Original Use Case: examples/use_case_6_preprocessing.py
Dependencies Removed: cyclicpeptide modules (functionality inlined)

Usage:
    python scripts/preprocess_data.py --input <input_file> --output <output_file>

Example:
    python scripts/preprocess_data.py --input examples/data/example_peptides.csv --output results/standardized.csv
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
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

# Add local lib to path
sys.path.insert(0, str(Path(__file__).parent))
from lib.molecules import (parse_smiles, canonicalize_smiles, calculate_molecular_weight,
                          count_atoms, count_rings, convert_sequence_codes, AMINO_ACID_CODES)
from lib.io import load_input_file, save_output_file, ensure_output_dir
from lib.validation import (validate_smiles, validate_sequence, validate_cyclic_peptide,
                          assess_data_quality)

# ==============================================================================
# Configuration
# ==============================================================================
DEFAULT_CONFIG = {
    "output_format": "csv",
    "standardization": {
        "canonicalize_smiles": True,
        "normalize_sequences": True,
        "remove_duplicates": True,
        "validate_structures": True
    },
    "quality_assessment": {
        "enable_scoring": True,
        "min_quality_score": 0,  # Don't filter by default
        "flag_low_quality": True
    },
    "data_cleaning": {
        "remove_empty": True,
        "remove_invalid": False,  # Keep invalid but flag them
        "standardize_format": True
    }
}

# ==============================================================================
# Data Preprocessing Functions
# ==============================================================================

def standardize_smiles(smiles: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """Standardize SMILES string and return metadata.

    Args:
        smiles: Input SMILES string

    Returns:
        Tuple of (standardized_smiles, metadata)
    """
    metadata = {
        "original": smiles,
        "standardized": None,
        "is_valid": False,
        "is_canonical": False,
        "errors": []
    }

    try:
        if not smiles or not smiles.strip():
            metadata["errors"].append("Empty SMILES")
            return None, metadata

        smiles = smiles.strip()

        # Validate SMILES
        is_valid, error = validate_smiles(smiles)
        metadata["is_valid"] = is_valid

        if not is_valid:
            metadata["errors"].append(f"Invalid SMILES: {error}")
            return None, metadata

        # Canonicalize
        canonical = canonicalize_smiles(smiles)
        if canonical is None:
            metadata["errors"].append("Could not canonicalize SMILES")
            return None, metadata

        metadata["standardized"] = canonical
        metadata["is_canonical"] = (canonical == smiles)

        return canonical, metadata

    except Exception as e:
        metadata["errors"].append(f"Standardization error: {str(e)}")
        return None, metadata

def standardize_sequence(sequence: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """Standardize amino acid sequence and return metadata.

    Args:
        sequence: Input sequence string

    Returns:
        Tuple of (standardized_sequence, metadata)
    """
    metadata = {
        "original": sequence,
        "standardized": None,
        "format": "unknown",
        "length": 0,
        "is_valid": False,
        "errors": []
    }

    try:
        if not sequence or not sequence.strip():
            metadata["errors"].append("Empty sequence")
            return None, metadata

        sequence = sequence.strip().upper()

        # Validate sequence
        is_valid, error = validate_sequence(sequence)
        metadata["is_valid"] = is_valid

        if not is_valid:
            metadata["errors"].append(f"Invalid sequence: {error}")
            return None, metadata

        # Determine format and standardize to 1-letter codes
        if re.search(r'[A-Z][a-z]{2}', sequence):
            # 3-letter codes
            metadata["format"] = "3-letter"
            three_letter_codes = re.findall(r'[A-Z][a-z]{2}', sequence)
            standardized = ""
            for code in three_letter_codes:
                if code in AMINO_ACID_CODES.values():
                    # Find 1-letter code
                    for k, v in AMINO_ACID_CODES.items():
                        if v == code:
                            standardized += k
                            break
                else:
                    metadata["errors"].append(f"Unknown amino acid: {code}")
                    return None, metadata
        else:
            # 1-letter codes
            metadata["format"] = "1-letter"
            standardized = sequence

        metadata["standardized"] = standardized
        metadata["length"] = len(standardized)

        return standardized, metadata

    except Exception as e:
        metadata["errors"].append(f"Sequence standardization error: {str(e)}")
        return None, metadata

def calculate_quality_score(data_type: str, data: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate comprehensive quality score for data.

    Args:
        data_type: Type of data ("smiles" or "sequence")
        data: The data string
        metadata: Metadata from standardization

    Returns:
        Quality assessment dictionary
    """
    quality = {
        "overall_score": 0,
        "validity_score": 0,
        "completeness_score": 0,
        "standardization_score": 0,
        "chemical_score": 0,
        "flags": [],
        "warnings": [],
        "category": "unknown"
    }

    try:
        # Base validity score
        if metadata.get("is_valid", False):
            quality["validity_score"] = 100
            quality["overall_score"] += 25
        else:
            quality["flags"].append("invalid_structure")
            quality["validity_score"] = 0

        # Completeness score
        if data and data.strip():
            quality["completeness_score"] = 100
            quality["overall_score"] += 25
        else:
            quality["flags"].append("incomplete_data")

        # Standardization score
        if metadata.get("is_canonical", False) or metadata.get("format") == "1-letter":
            quality["standardization_score"] = 100
            quality["overall_score"] += 25
        elif metadata.get("standardized"):
            quality["standardization_score"] = 75
            quality["overall_score"] += 20
        else:
            quality["flags"].append("not_standardized")

        if data_type == "smiles":
            # Chemical validity for SMILES
            mol = parse_smiles(data)
            if mol:
                quality["chemical_score"] = 50

                # Check if cyclic
                is_cyclic = count_rings(mol) > 0
                if is_cyclic:
                    quality["chemical_score"] += 30
                    quality["overall_score"] += 15
                else:
                    quality["warnings"].append("not_cyclic")

                # Check reasonable size for peptide
                num_atoms = count_atoms(mol)
                if 10 <= num_atoms <= 200:
                    quality["chemical_score"] += 20
                    quality["overall_score"] += 10
                elif num_atoms > 200:
                    quality["warnings"].append("large_molecule")
                elif num_atoms < 10:
                    quality["warnings"].append("small_molecule")

        elif data_type == "sequence":
            # Sequence quality
            seq_length = metadata.get("length", 0)
            if 3 <= seq_length <= 50:
                quality["chemical_score"] = 80
                quality["overall_score"] += 20
            elif seq_length > 50:
                quality["chemical_score"] = 60
                quality["warnings"].append("long_sequence")
                quality["overall_score"] += 15
            elif seq_length < 3:
                quality["chemical_score"] = 40
                quality["warnings"].append("short_sequence")
                quality["overall_score"] += 10
            else:
                quality["chemical_score"] = 0

        # Categorize quality
        if quality["overall_score"] >= 80:
            quality["category"] = "high"
        elif quality["overall_score"] >= 60:
            quality["category"] = "medium"
        elif quality["overall_score"] >= 40:
            quality["category"] = "low"
        else:
            quality["category"] = "very_low"

    except Exception as e:
        quality["flags"].append(f"quality_assessment_error: {str(e)}")

    return quality

def detect_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """Detect data types in DataFrame columns.

    Args:
        df: Input DataFrame

    Returns:
        Dictionary mapping column names to data types
    """
    column_types = {}

    for col in df.columns:
        sample_values = df[col].dropna().head(10).astype(str)

        if sample_values.empty:
            column_types[col] = "empty"
            continue

        # Check for SMILES patterns
        smiles_indicators = 0
        for val in sample_values:
            if any(char in val for char in ['(', ')', '[', ']', '=', '#', '@']):
                smiles_indicators += 1

        if smiles_indicators >= len(sample_values) * 0.7:
            column_types[col] = "smiles"
            continue

        # Check for sequence patterns
        sequence_indicators = 0
        for val in sample_values:
            # Remove common non-sequence characters
            clean_val = re.sub(r'[^A-Za-z]', '', str(val))
            if clean_val and all(c.upper() in AMINO_ACID_CODES for c in clean_val if c.isalpha()):
                sequence_indicators += 1
            elif re.search(r'([A-Z][a-z]{2})+', str(val)):  # 3-letter codes
                sequence_indicators += 1

        if sequence_indicators >= len(sample_values) * 0.7:
            column_types[col] = "sequence"
            continue

        # Check for numeric data
        try:
            pd.to_numeric(sample_values, errors='raise')
            column_types[col] = "numeric"
            continue
        except:
            pass

        # Default to text
        column_types[col] = "text"

    return column_types

def preprocess_dataframe(df: pd.DataFrame, config: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Preprocess entire DataFrame.

    Args:
        df: Input DataFrame
        config: Configuration dictionary

    Returns:
        Tuple of (processed_DataFrame, processing_summary)
    """
    summary = {
        "original_rows": len(df),
        "processed_rows": 0,
        "removed_rows": 0,
        "columns_processed": {},
        "quality_distribution": {"high": 0, "medium": 0, "low": 0, "very_low": 0},
        "warnings": [],
        "errors": []
    }

    try:
        # Detect column types
        column_types = detect_data_types(df)
        summary["columns_detected"] = column_types

        # Create a copy for processing
        processed_df = df.copy()

        # Add standardization columns
        standardized_cols = []

        for col, col_type in column_types.items():
            if col_type in ["smiles", "sequence"]:
                print(f"Processing column '{col}' as {col_type}...")

                # Create new columns for standardized data
                std_col = f"{col}_standardized"
                quality_col = f"{col}_quality"
                score_col = f"{col}_quality_score"

                standardized_data = []
                quality_data = []
                quality_scores = []

                for idx, value in processed_df[col].items():
                    if pd.isna(value) or value == "":
                        standardized_data.append(None)
                        quality_data.append("empty")
                        quality_scores.append(0)
                        continue

                    if col_type == "smiles":
                        std_value, metadata = standardize_smiles(str(value))
                        quality = calculate_quality_score("smiles", str(value), metadata)
                    else:  # sequence
                        std_value, metadata = standardize_sequence(str(value))
                        quality = calculate_quality_score("sequence", str(value), metadata)

                    standardized_data.append(std_value)
                    quality_data.append(quality["category"])
                    quality_scores.append(quality["overall_score"])

                    # Update quality distribution
                    summary["quality_distribution"][quality["category"]] += 1

                processed_df[std_col] = standardized_data
                processed_df[quality_col] = quality_data
                processed_df[score_col] = quality_scores

                standardized_cols.extend([std_col, quality_col, score_col])

                summary["columns_processed"][col] = {
                    "type": col_type,
                    "standardized_column": std_col,
                    "quality_column": quality_col,
                    "score_column": score_col,
                    "valid_entries": sum(1 for x in standardized_data if x is not None)
                }

        # Remove duplicates if requested
        if config.get("standardization", {}).get("remove_duplicates", False):
            original_length = len(processed_df)
            # Remove duplicates based on standardized columns
            duplicate_cols = [col for col in standardized_cols if col.endswith("_standardized")]
            if duplicate_cols:
                processed_df = processed_df.drop_duplicates(subset=duplicate_cols, keep='first')
                duplicates_removed = original_length - len(processed_df)
                if duplicates_removed > 0:
                    summary["warnings"].append(f"Removed {duplicates_removed} duplicate entries")

        # Filter by quality if requested
        min_quality = config.get("quality_assessment", {}).get("min_quality_score", 0)
        if min_quality > 0:
            quality_score_cols = [col for col in processed_df.columns if col.endswith("_quality_score")]
            if quality_score_cols:
                # Keep rows where at least one quality score meets threshold
                quality_mask = processed_df[quality_score_cols].max(axis=1) >= min_quality
                filtered_df = processed_df[quality_mask]
                filtered_count = len(processed_df) - len(filtered_df)
                if filtered_count > 0:
                    summary["warnings"].append(f"Filtered {filtered_count} low-quality entries")
                processed_df = filtered_df

        # Remove empty rows if requested
        if config.get("data_cleaning", {}).get("remove_empty", True):
            # Remove rows where all standardized columns are None
            std_cols = [col for col in processed_df.columns if col.endswith("_standardized")]
            if std_cols:
                non_empty_mask = processed_df[std_cols].notna().any(axis=1)
                empty_count = len(processed_df) - non_empty_mask.sum()
                if empty_count > 0:
                    processed_df = processed_df[non_empty_mask]
                    summary["warnings"].append(f"Removed {empty_count} empty entries")

        summary["processed_rows"] = len(processed_df)
        summary["removed_rows"] = summary["original_rows"] - summary["processed_rows"]

    except Exception as e:
        summary["errors"].append(f"DataFrame processing error: {str(e)}")

    return processed_df, summary

# ==============================================================================
# Core Function
# ==============================================================================
def run_preprocess_data(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Preprocess and standardize cyclic peptide data.

    Args:
        input_file: Path to input file (CSV, JSON, TXT)
        output_file: Path to save processed output
        config: Configuration dict
        **kwargs: Override config parameters

    Returns:
        Dict containing results and metadata
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    input_file = Path(input_file)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    try:
        # Load data
        print(f"Loading data from {input_file}...")

        if input_file.suffix.lower() == '.csv':
            df = pd.read_csv(input_file)
        elif input_file.suffix.lower() == '.json':
            df = pd.read_json(input_file)
        elif input_file.suffix.lower() in ['.txt', '.tsv']:
            # Try to detect delimiter
            with open(input_file, 'r') as f:
                first_line = f.readline()
                if '\t' in first_line:
                    df = pd.read_csv(input_file, sep='\t')
                else:
                    df = pd.read_csv(input_file)
        else:
            raise ValueError(f"Unsupported file format: {input_file.suffix}")

        print(f"Loaded {len(df)} records with {len(df.columns)} columns")

        # Preprocess data
        processed_df, summary = preprocess_dataframe(df, config)

        # Save results if output specified
        output_path = None
        if output_file:
            output_path = Path(output_file)
            output_dir = ensure_output_dir(output_path)

            # Save processed data
            if config["output_format"] == "csv":
                processed_df.to_csv(output_path, index=False)
            elif config["output_format"] == "json":
                processed_df.to_json(output_path, orient='records', indent=2)
            else:
                processed_df.to_csv(output_path, index=False)

            # Save processing summary
            summary_file = output_dir / f"preprocessing_summary.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)

            print(f"Processed data saved to: {output_path}")
            print(f"Processing summary saved to: {summary_file}")

        return {
            "processed_data": processed_df,
            "summary": summary,
            "output_file": str(output_path) if output_path else None,
            "metadata": {
                "input_file": str(input_file),
                "original_rows": summary["original_rows"],
                "processed_rows": summary["processed_rows"],
                "removed_rows": summary["removed_rows"],
                "config": config
            }
        }

    except Exception as e:
        raise Exception(f"Error preprocessing data: {str(e)}")

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Input file path (CSV, JSON, TXT)')
    parser.add_argument('--output', '-o', help='Output file path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--format', '-f', choices=['csv', 'json'],
                       default='csv', help='Output format')
    parser.add_argument('--min-quality', type=int, default=0,
                       help='Minimum quality score (0-100)')
    parser.add_argument('--remove-duplicates', action='store_true',
                       help='Remove duplicate entries')
    parser.add_argument('--keep-invalid', action='store_true',
                       help='Keep invalid entries (flag them)')

    args = parser.parse_args()

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

    if args.min_quality > 0:
        config.setdefault("quality_assessment", {})["min_quality_score"] = args.min_quality

    if args.remove_duplicates:
        config.setdefault("standardization", {})["remove_duplicates"] = True

    if args.keep_invalid:
        config.setdefault("data_cleaning", {})["remove_invalid"] = False

    try:
        # Run preprocessing
        result = run_preprocess_data(
            input_file=args.input,
            output_file=args.output,
            config=config
        )

        # Print summary
        print(f"\nPreprocessing completed!")
        print(f"  Original records: {result['metadata']['original_rows']}")
        print(f"  Processed records: {result['metadata']['processed_rows']}")
        print(f"  Removed records: {result['metadata']['removed_rows']}")

        # Quality distribution
        quality_dist = result['summary']['quality_distribution']
        print(f"\nQuality Distribution:")
        print(f"  High quality: {quality_dist['high']}")
        print(f"  Medium quality: {quality_dist['medium']}")
        print(f"  Low quality: {quality_dist['low']}")
        print(f"  Very low quality: {quality_dist['very_low']}")

        if result['output_file']:
            print(f"\nOutput saved to: {result['output_file']}")

        if result['summary']['warnings']:
            print(f"\nWarnings:")
            for warning in result['summary']['warnings']:
                print(f"  - {warning}")

        if result['summary']['errors']:
            print(f"\nErrors:")
            for error in result['summary']['errors']:
                print(f"  - {error}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    main()