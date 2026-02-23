# cyclicpeptide MCP

> Comprehensive MCP tools for cyclic peptide computational analysis and virtual screening

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

This MCP server provides comprehensive tools for cyclic peptide computational analysis, including structure prediction, property calculation, sequence analysis, and data preprocessing. Built on the cyclicpeptide library, it enables drug discovery workflows through both fast synchronous operations and background batch processing.

### Features
- **Sequence-Structure Interconversion** - Convert between amino acid sequences and SMILES representations
- **Molecular Property Calculation** - Calculate 57+ molecular descriptors, fingerprints, and drug-likeness rules
- **Structure Analysis** - Generate comprehensive HTML reports with molecular properties and visualizations
- **Data Preprocessing** - Clean, validate, and standardize cyclic peptide datasets
- **Batch Processing** - Handle large-scale virtual screening and library enumeration
- **Job Management** - Track long-running computations with status monitoring

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   └── server.py           # MCP server with 13 tools
├── scripts/
│   ├── sequence_to_structure.py      # Sequence to SMILES conversion
│   ├── structure_to_sequence.py      # SMILES to sequence conversion
│   ├── calculate_properties.py       # Molecular property calculation
│   ├── preprocess_data.py            # Data preprocessing and standardization
│   ├── analyze_structure.py          # Comprehensive structure analysis
│   └── lib/                          # Shared utilities
├── examples/
│   └── data/               # Demo data
│       ├── sequences.txt   # Sample cyclic peptide sequences (APG, GFPVFP, etc.)
│       ├── smiles.txt      # Sample SMILES structures
│       ├── monomer.tsv     # 546 monomer database
│       └── models/         # Pre-trained models for graph alignment
├── configs/                # Configuration files
│   ├── sequence_to_structure_config.json
│   ├── calculate_properties_config.json
│   └── preprocess_data_config.json
└── repo/                   # Original repository
```

---

## Installation

### Quick Setup

Run the automated setup script:

```bash
./quick_setup.sh
```

This will create the environment and install all dependencies automatically.

### Manual Setup (Advanced)

For manual installation or customization, follow these steps.

#### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- RDKit (installed automatically)

#### Create Environment

Following the procedure from `reports/step3_environment.md`:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicpeptide_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.12 -y
# or: conda create -p ./env python=3.12 -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install Dependencies
mamba install -c conda-forge rdkit=2025.09.3 matplotlib=3.10.8 networkx=3.6.1 pandas=2.3.3 numpy=2.4.0 scipy=1.16.3 loguru=0.7.3 click=8.3.1 tqdm=4.67.1 -y

# Install Python packages
pip install fastmcp==2.14.1 ipython==9.8.0 --force-reinstall

# Install cyclicpeptide package (manual installation)
cp -r repo/cyclicpeptide/cyclicpeptide env/lib/python3.12/site-packages/
cp -r repo/cyclicpeptide/states env/lib/python3.12/site-packages/cyclicpeptide/
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/sequence_to_structure.py` | Convert amino acid sequences to cyclic peptide SMILES | See below |
| `scripts/structure_to_sequence.py` | Convert SMILES structures back to amino acid sequences | See below |
| `scripts/calculate_properties.py` | Calculate comprehensive molecular properties | See below |
| `scripts/preprocess_data.py` | Preprocess and standardize peptide datasets | See below |
| `scripts/analyze_structure.py` | Generate comprehensive HTML analysis reports | See below |

### Script Examples

#### Convert Sequence to Structure

```bash
# Activate environment
mamba activate ./env

# Convert single sequence to SMILES
python scripts/sequence_to_structure.py \
  --sequence "GRGDSP" \
  --output results/grgdsp.smi \
  --visualize

# Batch conversion from file
python scripts/sequence_to_structure.py \
  --input examples/data/sequences.txt \
  --output results/structures.smi
```

**Parameters:**
- `--sequence, -s`: Amino acid sequence (1-letter codes) (required for single)
- `--input, -i`: Input file with multiple sequences (for batch)
- `--output, -o`: Output file path (default: results/)
- `--visualize, -v`: Generate SVG structure visualization
- `--linear`: Create linear peptide instead of cyclic

#### Calculate Properties

```bash
python scripts/calculate_properties.py \
  --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" \
  --format csv \
  --output properties.csv \
  --include-fingerprints
```

**Parameters:**
- `--smiles, -s`: SMILES string (required for single)
- `--input, -i`: Input file with multiple SMILES (for batch)
- `--format, -f`: Output format (json/csv/txt)
- `--include-fingerprints`: Include molecular fingerprints
- `--output, -o`: Output file path

#### Preprocess Data

```bash
python scripts/preprocess_data.py \
  --input examples/data/example_peptides.csv \
  --output cleaned_data.csv \
  --min-quality-score 60 \
  --remove-duplicates
```

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name cycpep-tools
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicpeptide_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicpeptide_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from cycpep-tools?
```

#### Property Calculation (Fast)
```
Calculate molecular properties for this cyclic peptide: C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O
```

#### Sequence Conversion
```
Convert the peptide sequence GRGDSP to a cyclic peptide SMILES structure
```

#### Structure Analysis (Submit API)
```
Submit a comprehensive structure analysis job for the cyclic peptide with SMILES: C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O
```

#### Check Job Status
```
Check the status of job abc12345
```

#### Batch Processing
```
Calculate properties for these cyclic peptides in batch using the file @examples/data/smiles.txt
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sequences.txt` | Reference sample peptide sequences |
| `@examples/data/smiles.txt` | Reference sample SMILES structures |
| `@configs/calculate_properties_config.json` | Reference property calculation config |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cycpep-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicpeptide_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicpeptide_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available?
> Calculate properties for cyclic peptide C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `calculate_cyclic_peptide_properties` | Calculate molecular properties (57+ descriptors) | `smiles`, `properties`, `include_fingerprints` |
| `convert_sequence_to_structure` | Convert amino acid sequences to SMILES | `sequence`, `cyclic`, `visualize` |
| `convert_structure_to_sequence` | Convert SMILES to amino acid sequences | `smiles`, `input_file` |
| `preprocess_cyclic_peptide_data` | Clean and standardize peptide datasets | `input_file`, `min_quality_score`, `remove_duplicates` |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_comprehensive_structure_analysis` | Generate detailed HTML analysis reports | `smiles`, `include_visualization` |
| `submit_batch_property_calculation` | Calculate properties for large datasets | `input_file`, `properties`, `include_fingerprints` |
| `submit_batch_sequence_conversion` | Convert multiple sequences to structures | `input_file`, `cyclic`, `visualize` |
| `submit_batch_data_preprocessing` | Process large datasets with quality assessment | `input_file`, `min_quality_score`, `standardize_format` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and status |
| `get_job_result` | Get results when job completed |
| `get_job_log` | View execution logs with tail option |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with optional status filter |

---

## Examples

### Example 1: Quick Property Calculation

**Goal:** Calculate drug-like properties for a cyclic peptide

**Using Script:**
```bash
python scripts/calculate_properties.py \
  --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" \
  --format json \
  --output apg_properties.json
```

**Using MCP (in Claude Code):**
```
Calculate molecular properties for the cyclic peptide C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O including molecular weight, logP, and TPSA
```

**Expected Output:**
- Molecular weight: ~225 Da
- LogP: ~-1.5 (hydrophilic)
- TPSA: ~87 Ų
- Drug-likeness rules (Lipinski, Veber)
- Molecular fingerprints (Morgan, RDKit, MACCS)

### Example 2: Sequence to Structure Conversion

**Goal:** Convert amino acid sequence to cyclic peptide SMILES

**Using Script:**
```bash
python scripts/sequence_to_structure.py \
  --sequence "GRGDSP" \
  --visualize \
  --output grgdsp_structure.smi
```

**Using MCP (in Claude Code):**
```
Convert the peptide sequence GRGDSP to a cyclic peptide SMILES structure with visualization
```

**Expected Output:**
- SMILES: Generated cyclic peptide structure
- SVG visualization
- Quality assessment score
- Molecular metadata

### Example 3: Virtual Screening Pipeline

**Goal:** Screen a library of cyclic peptides for drug-likeness

**Using MCP (in Claude Code):**
```
I want to screen cyclic peptides for oral bioavailability using the file @examples/data/smiles.txt

Calculate properties for all structures and identify which ones have:
- Molecular weight < 1000 Da
- LogP between -2 and 5
- TPSA < 250 Ų
- Lipinski Rule of 5 compliance
```

**Expected Output:**
- Property table for all peptides
- Drug-likeness assessment
- Filtered candidates meeting criteria
- Processing summary

### Example 4: Comprehensive Structure Analysis

**Goal:** Generate detailed analysis report for a cyclic peptide

**Using MCP (in Claude Code):**
```
Submit a comprehensive structure analysis job for the cyclic peptide with SMILES: C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O

Include visualizations and check the job status after submission.
```

**Expected Output:**
- Job submission confirmation with job_id
- HTML report with:
  - Structure visualization
  - Sequence analysis (detected amino acids)
  - Comprehensive molecular properties
  - Drug-likeness assessment
  - Quality evaluation

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Use With |
|------|-------------|----------|
| `sequences.txt` | Sample peptide sequences (APG, GFPVFP, WAGFP, CCGP, FGPP) | `convert_sequence_to_structure` |
| `smiles.txt` | Sample SMILES structures (3 cyclic peptides) | All property tools |
| `monomer.tsv` | 546 monomer database for extended amino acids | Structure analysis |
| `example_peptides.csv` | Mixed quality dataset for preprocessing testing | `preprocess_cyclic_peptide_data` |
| `Chemical_P.csv` | Reference chemical properties | Property validation |
| `models/GA_GCN.pth` | Pre-trained graph neural network model (44KB) | Graph alignment (optional) |

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Parameters |
|--------|-------------|------------|
| `sequence_to_structure_config.json` | Sequence conversion settings | `cyclic`, `visualization`, `output_format` |
| `calculate_properties_config.json` | Property calculation settings | `include_fingerprints`, `properties`, `output_format` |
| `preprocess_data_config.json` | Data preprocessing settings | `standardization`, `quality_assessment`, `data_cleaning` |
| `analyze_structure_config.json` | Structure analysis settings | `include_visualization`, `report_sections` |
| `default_config.json` | Global default settings | `global`, `visualization`, `molecular` |

### Config Example

```json
{
  "cyclic": true,
  "amino_acids": "essential_only",
  "visualization": {
    "enabled": true,
    "width": 400,
    "height": 400
  },
  "output": {
    "format": "smi",
    "include_metadata": true
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.12 -y
mamba activate ./env
pip install fastmcp==2.14.1 --force-reinstall
mamba install -c conda-forge rdkit -y
```

**Problem:** RDKit import errors
```bash
# Install RDKit from conda-forge
mamba install -c conda-forge rdkit -y

# Test import
python -c "from rdkit import Chem; print('RDKit working')"
```

**Problem:** cyclicpeptide import errors
```bash
# Verify installation
cp -r repo/cyclicpeptide/cyclicpeptide env/lib/python3.12/site-packages/
cp -r repo/cyclicpeptide/states env/lib/python3.12/site-packages/cyclicpeptide/

# Test import
python -c "from cyclicpeptide import PropertyAnalysis; print('cyclicpeptide working')"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove cycpep-tools
claude mcp add cycpep-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Invalid SMILES error
```
Ensure your SMILES string is valid for cyclic peptides. Common formats:
- Explicit ring closure: C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O
- Use RDKit canonical SMILES for best results
```

**Problem:** Tools not working
```bash
# Test server directly
./env/bin/python -c "
from src.server import mcp
print(f'Tools available: {len(list(mcp.list_tools()))}')
print(list(mcp.list_tools().keys()))
"
```

### Job Issues

**Problem:** Job stuck in pending
```bash
# Check job directory
ls -la jobs/

# View job log
python -c "from src.jobs.manager import job_manager; print(job_manager.get_job_log('<job_id>', tail=0))"
```

**Problem:** Job failed
```
Use get_job_log tool with job_id and tail=100 to see detailed error information
```

**Problem:** Property calculation warnings
```
RDKit deprecation warnings are expected and do not affect functionality.
Results are still accurate despite fingerprint calculation warnings.
```

### Performance Issues

**Problem:** Slow property calculation
```bash
# Skip fingerprints for faster processing
python scripts/calculate_properties.py --smiles "SMILES" --no-fingerprints
```

**Problem:** Memory issues with large files
```bash
# Process in smaller batches
split -l 100 large_file.txt batch_
for file in batch_*; do python scripts/calculate_properties.py --input $file; done
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Test scripts individually
python scripts/sequence_to_structure.py --sequence APG --output test_output/
python scripts/calculate_properties.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --format json

# Test MCP server
./env/bin/python src/server.py &
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
fastmcp dev src/server.py
```

### Validation Commands

```bash
# Test core functionality
./env/bin/python -c "from cyclicpeptide import PropertyAnalysis, Sequence2Structure, Structure2Sequence; print('All modules imported successfully')"

# Test RDKit
./env/bin/python -c "import rdkit; from rdkit import Chem; print('RDKit working')"

# Test basic functionality
./env/bin/python -c "from cyclicpeptide import Sequence2Structure; smiles, peptide = Sequence2Structure.seq2stru_essentialAA(sequence='APG', cyclic=True); print('SMILES:', smiles)"
```

---

## License

Based on the [cyclicpeptide](https://github.com/dfwlab/cyclicpeptide) repository

## Credits

- **Original Repository**: [dfwlab/cyclicpeptide](https://github.com/dfwlab/cyclicpeptide)
- **MCP Framework**: FastMCP 2.0+
- **Chemical Computing**: RDKit 2025.09.3
- **Integration Testing**: Claude Code with comprehensive validation

