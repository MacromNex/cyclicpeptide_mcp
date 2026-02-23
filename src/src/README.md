# CycPep MCP Server

Model Context Protocol (MCP) server for cyclic peptide computational tools.

## Quick Start

```bash
# Activate environment
mamba activate ../env  # or: conda activate ../env

# Start development server (with hot reload)
fastmcp dev server.py

# Start production server
fastmcp run server.py
```

## Available Tools

### Job Management (5 tools)
- `get_job_status(job_id)` - Check job progress
- `get_job_result(job_id)` - Get completed results
- `get_job_log(job_id)` - View execution logs
- `cancel_job(job_id)` - Cancel running job
- `list_jobs(status=None)` - List all jobs

### Synchronous Tools (4 tools - Fast operations)
- `calculate_cyclic_peptide_properties()` - Calculate molecular properties
- `convert_sequence_to_structure()` - Sequence to SMILES conversion
- `convert_structure_to_sequence()` - SMILES to sequence conversion
- `preprocess_cyclic_peptide_data()` - Data cleaning and standardization

### Submit Tools (4 tools - Long-running operations)
- `submit_comprehensive_structure_analysis()` - Generate detailed HTML reports
- `submit_batch_property_calculation()` - Batch property calculation
- `submit_batch_sequence_conversion()` - Batch sequence conversion
- `submit_batch_data_preprocessing()` - Large dataset preprocessing

## API Design

### Synchronous API (< 10 minutes)
Direct function calls with immediate results.

```python
result = calculate_cyclic_peptide_properties(smiles="CCO")
# Returns: {"status": "success", "results": [...]}
```

### Submit API (> 10 minutes)
Background job processing with status tracking.

```python
# Submit job
job = submit_comprehensive_structure_analysis(smiles="CCO")
job_id = job["job_id"]

# Check status
status = get_job_status(job_id)

# Get results when completed
if status["status"] == "completed":
    result = get_job_result(job_id)
```

## Testing

```bash
# Test basic functionality
python ../test_mcp.py

# Test server import
python -c "import server; print('Ready')"
```

## Files

- `server.py` - Main MCP server
- `jobs/manager.py` - Job management system
- `jobs/__init__.py` - Jobs module
- `tools/__init__.py` - Tools module

For complete documentation, see `../reports/step6_mcp_tools.md`.