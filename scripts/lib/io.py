"""
Input/Output utilities for cyclic peptide MCP scripts.

Simplified I/O functions extracted from the cyclicpeptide repository.
"""

import json
import csv
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import pandas as pd

def load_input_file(file_path: Union[str, Path]) -> List[str]:
    """Load input file containing sequences or SMILES.

    Args:
        file_path: Path to input file

    Returns:
        List of strings (sequences or SMILES)

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is unsupported
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == '.txt':
        # Plain text file - one entry per line
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines

    elif suffix == '.csv':
        # CSV file - first column assumed to contain data
        df = pd.read_csv(file_path)
        if df.empty:
            return []
        # Use first column
        return df.iloc[:, 0].astype(str).tolist()

    elif suffix == '.smi':
        # SMILES file format
        smiles_list = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    # SMILES files can have SMILES and name separated by tab/space
                    smiles = line.split()[0]
                    smiles_list.append(smiles)
        return smiles_list

    elif suffix == '.json':
        # JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            return [str(item) for item in data]
        elif isinstance(data, dict):
            # Try to find sequences/smiles in dict values
            for key in ['sequences', 'smiles', 'data', 'items']:
                if key in data and isinstance(data[key], list):
                    return [str(item) for item in data[key]]
            # If no standard key found, use first list value
            for value in data.values():
                if isinstance(value, list):
                    return [str(item) for item in value]
        return [str(data)]  # Single item

    else:
        raise ValueError(f"Unsupported file format: {suffix}")

def save_output_file(data: Any, file_path: Union[str, Path],
                     file_format: Optional[str] = None) -> bool:
    """Save data to output file.

    Args:
        data: Data to save (dict, list, DataFrame, etc.)
        file_path: Output file path
        file_format: Format to use ('json', 'csv', 'txt'). Auto-detected if None.

    Returns:
        True if successful, False otherwise
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Auto-detect format from extension if not specified
        if file_format is None:
            file_format = file_path.suffix.lower().lstrip('.')

        if file_format == 'json':
            # Convert non-serializable objects
            serializable_data = _make_json_serializable(data)
            with open(file_path, 'w') as f:
                json.dump(serializable_data, f, indent=2)

        elif file_format == 'csv':
            if isinstance(data, pd.DataFrame):
                data.to_csv(file_path, index=False)
            elif isinstance(data, list):
                # List of dicts or simple list
                if data and isinstance(data[0], dict):
                    df = pd.DataFrame(data)
                    df.to_csv(file_path, index=False)
                else:
                    # Simple list
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.writer(f)
                        for item in data:
                            writer.writerow([str(item)])
            elif isinstance(data, dict):
                # Convert dict to DataFrame
                df = pd.DataFrame([data])
                df.to_csv(file_path, index=False)

        elif file_format in ['txt', 'text']:
            with open(file_path, 'w') as f:
                if isinstance(data, (list, tuple)):
                    for item in data:
                        f.write(f"{item}\n")
                elif isinstance(data, dict):
                    for key, value in data.items():
                        f.write(f"{key}: {value}\n")
                else:
                    f.write(str(data))

        elif file_format == 'html':
            # HTML format
            with open(file_path, 'w') as f:
                if isinstance(data, str):
                    f.write(data)
                else:
                    f.write(f"<html><body><pre>{data}</pre></body></html>")

        elif file_format in ['smi', 'smiles']:
            # SMILES format
            with open(file_path, 'w') as f:
                if isinstance(data, (list, tuple)):
                    for item in data:
                        f.write(f"{item}\n")
                else:
                    f.write(str(data))

        else:
            raise ValueError(f"Unsupported output format: {file_format}")

        return True

    except Exception as e:
        print(f"Error saving file {file_path}: {e}")
        return False

def _make_json_serializable(data: Any) -> Any:
    """Convert data to JSON-serializable format.

    Args:
        data: Input data

    Returns:
        JSON-serializable version of data
    """
    if hasattr(data, 'tolist'):
        # NumPy arrays
        return data.tolist()
    elif isinstance(data, dict):
        return {key: _make_json_serializable(value) for key, value in data.items()}
    elif isinstance(data, (list, tuple)):
        return [_make_json_serializable(item) for item in data]
    elif hasattr(data, '__dict__'):
        # Objects with attributes
        return data.__dict__
    else:
        return data

def create_summary_report(results: List[Dict[str, Any]], output_path: Union[str, Path]) -> bool:
    """Create summary report from results.

    Args:
        results: List of result dictionaries
        output_path: Path to save summary

    Returns:
        True if successful
    """
    try:
        output_path = Path(output_path)

        # Create summary DataFrame
        if results:
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
            return True
        else:
            # Empty results
            with open(output_path, 'w') as f:
                f.write("No results to summarize.\n")
            return True

    except Exception as e:
        print(f"Error creating summary report: {e}")
        return False

def load_config_file(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration file.

    Args:
        config_path: Path to config file (JSON)

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid JSON
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")

def ensure_output_dir(output_path: Union[str, Path]) -> Path:
    """Ensure output directory exists.

    Args:
        output_path: Output file or directory path

    Returns:
        Output directory path
    """
    output_path = Path(output_path)

    if output_path.suffix:
        # It's a file path, get parent directory
        output_dir = output_path.parent
    else:
        # It's a directory path
        output_dir = output_path

    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir