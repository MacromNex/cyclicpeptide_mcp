#!/usr/bin/env python3
"""MCP Server for Cyclic Peptide Tools

Provides both synchronous and asynchronous (submit) APIs for all tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import sys
import importlib.util

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("cycpep-tools")

# ==============================================================================
# Helper function to import scripts dynamically
# ==============================================================================

def import_script_function(script_name: str, function_name: str):
    """Dynamically import a function from a script."""
    script_path = SCRIPTS_DIR / f"{script_name}.py"
    if not script_path.exists():
        raise ImportError(f"Script {script_name}.py not found")

    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, function_name)

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted cyclic peptide computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed cyclic peptide computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running cyclic peptide computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted cyclic peptide computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def calculate_cyclic_peptide_properties(
    smiles: Optional[str] = None,
    input_file: Optional[str] = None,
    properties: Optional[List[str]] = None,
    include_fingerprints: bool = True,
    output_file: Optional[str] = None
) -> dict:
    """
    Calculate molecular properties for cyclic peptides.

    Fast operation - returns results immediately. Can process single SMILES or batch file.

    Args:
        smiles: SMILES string of the cyclic peptide (for single calculation)
        input_file: Path to file with multiple SMILES (for batch calculation)
        properties: List of properties to calculate (default: all)
                   Options: molecular_weight, logp, tpsa, hbd, hba, rotatable_bonds
        include_fingerprints: Whether to include molecular fingerprints
        output_file: Optional path to save output

    Returns:
        Dictionary with calculated properties or batch results
    """
    try:
        run_calculate_properties = import_script_function("calculate_properties", "run_calculate_properties")

        result = run_calculate_properties(
            smiles=smiles,
            input_file=input_file,
            output_file=output_file,
            include_fingerprints=include_fingerprints,
            properties=properties
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Property calculation failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def convert_sequence_to_structure(
    sequence: Optional[str] = None,
    input_file: Optional[str] = None,
    cyclic: bool = True,
    visualize: bool = False,
    output_file: Optional[str] = None
) -> dict:
    """
    Convert amino acid sequences to cyclic peptide SMILES structures.

    Fast operation for converting peptide sequences to SMILES representations.

    Args:
        sequence: Single amino acid sequence (1-letter or 3-letter codes)
        input_file: Path to file with multiple sequences (for batch)
        cyclic: Whether to create cyclic peptides (default: True)
        visualize: Whether to generate structure visualizations
        output_file: Optional path to save output

    Returns:
        Dictionary with generated SMILES and metadata
    """
    try:
        run_sequence_to_structure = import_script_function("sequence_to_structure", "run_sequence_to_structure")

        result = run_sequence_to_structure(
            sequence=sequence,
            input_file=input_file,
            output_file=output_file,
            cyclic=cyclic,
            visualize=visualize
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid sequence: {e}"}
    except Exception as e:
        logger.error(f"Sequence conversion failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def convert_structure_to_sequence(
    smiles: Optional[str] = None,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None
) -> dict:
    """
    Convert SMILES structures back to amino acid sequences.

    Attempts to identify amino acid components in cyclic peptide structures.

    Args:
        smiles: Single SMILES string to analyze
        input_file: Path to file with multiple SMILES (for batch)
        output_file: Optional path to save output

    Returns:
        Dictionary with detected sequences and analysis
    """
    try:
        run_structure_to_sequence = import_script_function("structure_to_sequence", "run_structure_to_sequence")

        result = run_structure_to_sequence(
            smiles=smiles,
            input_file=input_file,
            output_file=output_file
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid SMILES: {e}"}
    except Exception as e:
        logger.error(f"Structure analysis failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def preprocess_cyclic_peptide_data(
    input_file: str,
    output_file: Optional[str] = None,
    min_quality_score: int = 0,
    remove_duplicates: bool = True,
    standardize_format: bool = True
) -> dict:
    """
    Preprocess and standardize cyclic peptide datasets.

    Cleans and validates cyclic peptide data, removes duplicates, and standardizes formats.

    Args:
        input_file: Path to input data file (CSV/TXT)
        output_file: Optional path to save cleaned data
        min_quality_score: Minimum quality score to keep (0-100)
        remove_duplicates: Whether to remove duplicate entries
        standardize_format: Whether to standardize SMILES and sequence formats

    Returns:
        Dictionary with preprocessing results and statistics
    """
    try:
        run_preprocess_data = import_script_function("preprocess_data", "run_preprocess_data")

        result = run_preprocess_data(
            input_file=input_file,
            output_file=output_file,
            min_quality_score=min_quality_score,
            remove_duplicates=remove_duplicates,
            standardize_format=standardize_format
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except Exception as e:
        logger.error(f"Data preprocessing failed: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations > 10 min)
# ==============================================================================

@mcp.tool()
def submit_comprehensive_structure_analysis(
    smiles: Optional[str] = None,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    include_visualization: bool = True,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a comprehensive structure analysis job for cyclic peptides.

    This generates detailed HTML reports with molecular properties, sequence analysis,
    and visualizations. May take several minutes for complex structures.

    Args:
        smiles: SMILES string of the cyclic peptide (for single analysis)
        input_file: Path to file with multiple SMILES (for batch analysis)
        output_file: Optional path to save report (HTML format)
        include_visualization: Whether to include structure visualizations
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    script_path = str(SCRIPTS_DIR / "analyze_structure.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "smiles": smiles,
            "input-file": input_file,
            "output-file": output_file,
            "visualize": include_visualization
        },
        job_name=job_name or "structure_analysis"
    )

@mcp.tool()
def submit_batch_property_calculation(
    input_file: str,
    properties: Optional[List[str]] = None,
    include_fingerprints: bool = True,
    output_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch property calculation for multiple cyclic peptides.

    Processes large datasets in the background. Suitable for:
    - Processing many cyclic peptide candidates at once
    - Large-scale virtual screening
    - Library enumeration analysis

    Args:
        input_file: Path to file with multiple SMILES/sequences
        properties: Properties to calculate (default: all)
        include_fingerprints: Whether to calculate molecular fingerprints
        output_file: Optional path to save results
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    script_path = str(SCRIPTS_DIR / "calculate_properties.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input-file": input_file,
            "properties": ",".join(properties) if properties else None,
            "include-fingerprints": include_fingerprints,
            "output-file": output_file
        },
        job_name=job_name or f"batch_properties"
    )

@mcp.tool()
def submit_batch_sequence_conversion(
    input_file: str,
    cyclic: bool = True,
    visualize: bool = False,
    output_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch sequence to structure conversion for multiple peptides.

    Converts large numbers of amino acid sequences to SMILES structures in the background.

    Args:
        input_file: Path to file with multiple sequences
        cyclic: Whether to create cyclic peptides (default: True)
        visualize: Whether to generate structure visualizations
        output_file: Optional path to save results
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking
    """
    script_path = str(SCRIPTS_DIR / "sequence_to_structure.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input-file": input_file,
            "cyclic": cyclic,
            "visualize": visualize,
            "output-file": output_file
        },
        job_name=job_name or "batch_seq_to_struct"
    )

@mcp.tool()
def submit_batch_data_preprocessing(
    input_file: str,
    min_quality_score: int = 0,
    remove_duplicates: bool = True,
    standardize_format: bool = True,
    output_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch data preprocessing for large cyclic peptide datasets.

    Processes large datasets with quality assessment and standardization.

    Args:
        input_file: Path to input data file
        min_quality_score: Minimum quality score to keep (0-100)
        remove_duplicates: Whether to remove duplicate entries
        standardize_format: Whether to standardize formats
        output_file: Optional path to save cleaned data
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking
    """
    script_path = str(SCRIPTS_DIR / "preprocess_data.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input-file": input_file,
            "min-quality-score": min_quality_score,
            "remove-duplicates": remove_duplicates,
            "standardize-format": standardize_format,
            "output-file": output_file
        },
        job_name=job_name or "batch_preprocessing"
    )

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()