# Cyclic Peptide MCP Server - Claude Code Integration Guide

## Quick Start

### 1. Installation
```bash
# Add MCP server to Claude Code
cd /path/to/cyclicpeptide_mcp
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
# Should show: cycpep-tools - ✓ Connected
```

### 2. Start Claude Code
```bash
claude
```

## Available Tools

The MCP server provides 13 tools for cyclic peptide analysis:

### 🔬 Sync Tools (Fast < 30s)
- `calculate_cyclic_peptide_properties` - Molecular property calculation
- `convert_sequence_to_structure` - Amino acid sequence → SMILES
- `convert_structure_to_sequence` - SMILES → amino acid sequence
- `preprocess_cyclic_peptide_data` - Data cleaning and preprocessing

### ⚡ Submit API (Long-running jobs)
- `submit_comprehensive_structure_analysis` - 3D structure prediction
- `submit_batch_property_calculation` - Batch molecular properties
- `submit_batch_sequence_conversion` - Batch sequence conversion
- `submit_batch_data_preprocessing` - Batch data processing

### 📊 Job Management
- `get_job_status` - Check job status
- `get_job_result` - Retrieve job results
- `get_job_log` - View job execution logs
- `cancel_job` - Cancel running jobs
- `list_jobs` - List all jobs

## Example Prompts

### Basic Property Calculation
```
"Calculate molecular properties for the cyclic peptide SMILES: CC(=O)NC1CCCC1C(=O)O"
```

### Sequence to Structure
```
"Convert the peptide sequence 'GRGDSP' to a cyclic peptide SMILES structure"
```

### Drug-likeness Assessment
```
"Assess the drug-likeness of cyclo(Pro-Leu-Gly-Phe-Ala):
- Calculate molecular weight, logP, and TPSA
- Check if it meets cyclic peptide drug criteria"
```

### Batch Analysis
```
"Calculate properties for these cyclic peptides:
cyclo(GRGDSP), cyclo(RGDFV), cyclo(YIGSR)"
```

### Complete Workflow
```
"For the cyclic peptide sequence GRGDSP:
1. Convert to cyclic SMILES
2. Calculate molecular properties
3. Submit 3D structure prediction
Summarize all results."
```

### Job Management
```
"Submit structure analysis for cyclo(GRGDSP), then check the job status"

"List all my completed jobs"

"Show me the logs for job abc12345"
```

## Expected Response Format

### Successful Property Calculation
```json
{
  "status": "success",
  "results": [{
    "SMILES": "CC(=O)NC1CCCC1C(=O)O",
    "Molecular_Weight": 171.09,
    "Crippen_LogP": 0.38,
    "Topological_Polar_Surface_Area": 66.40,
    "Rule_of_Five": true,
    ...
  }],
  "metadata": {
    "total_structures": 1,
    "successful": 1,
    "failed": 0
  }
}
```

### Job Submission
```json
{
  "status": "submitted",
  "job_id": "abc12345",
  "message": "Job submitted successfully"
}
```

### Job Status
```json
{
  "job_id": "abc12345",
  "status": "running",
  "submitted_at": "2025-12-31T10:00:00",
  "started_at": "2025-12-31T10:00:05"
}
```

## Input Data Formats

### SMILES Strings
- Valid: `CC(=O)NC1CCCC1C(=O)O`
- Cyclic peptides: `CCC1NC(=O)CNC(=O)C(C)NC1=O`

### Sequences
- Single letter: `GRGDSP`, `RGDFV`, `YIGSR`
- Three letter: `Gly-Arg-Gly-Asp-Ser-Pro`

### File Inputs
- CSV files with SMILES column
- Text files with one SMILES/sequence per line
- Use relative paths from MCP directory

## Common Issues & Solutions

### 1. Server Not Connected
**Problem**: `claude mcp list` shows server as disconnected
**Solution**:
```bash
# Remove and re-add server
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

### 2. Tools Not Appearing
**Problem**: Claude Code doesn't see MCP tools
**Solution**: Restart Claude Code session

### 3. Invalid SMILES Warning
**Problem**: RDKit warnings for invalid SMILES
**Status**: Expected - warnings help identify invalid structures
**Note**: Future version will return proper error status

### 4. Job Logs Not Found
**Problem**: "Log not found" for job logs
**Cause**: Job hasn't started execution yet (still pending)
**Solution**: Wait for job to start, then check logs

## Performance Guidelines

### Response Times
- Property calculation: < 30 seconds
- Sequence conversion: < 15 seconds
- Job submission: < 5 seconds
- Status checks: < 2 seconds

### Input Limits
- Single SMILES: No practical limit
- Batch operations: Recommended < 100 structures for responsive UI
- File sizes: < 10MB for best performance

## Troubleshooting Commands

### Check Server Health
```bash
claude mcp list
```

### Restart MCP Server
```bash
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

### Test Server Directly
```bash
./env/bin/fastmcp dev src/server.py
# Visit http://localhost:6274 for MCP inspector
```

### View Configuration
```bash
cat ~/.claude.json | grep -A10 cycpep-tools
```

## Advanced Usage

### Custom Property Selection
```
"Calculate only molecular weight and logP for cyclo(GRGDSP)"
```

### File-based Analysis
```
"Process the peptide data in examples/data/example_peptides.csv and calculate properties for all valid SMILES"
```

### Concurrent Jobs
```
"Submit structure predictions for cyclo(GRGDSP), cyclo(RGDFV), and cyclo(YIGSR) simultaneously, then check status of all jobs"
```

---

## Support

- **Test Results**: See `reports/step7_integration_test_results.md`
- **Full Test Suite**: Run `./env/bin/python tests/run_integration_tests.py src/server.py ./env`
- **MCP Inspector**: Use `./env/bin/fastmcp dev src/server.py` for debugging

*Last updated: 2025-12-31*
*Server version: Tested and verified*
*Claude Code compatibility: ✅ Confirmed*