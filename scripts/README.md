# MCP Scripts for Cyclic Peptide Analysis

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (rdkit, numpy, pandas)
2. **Self-Contained**: Functions inlined where possible to minimize repo dependencies
3. **Configurable**: Parameters externalized to config files, not hardcoded
4. **MCP-Ready**: Each script exports a main function ready for MCP wrapping

## Scripts Overview

| Script | Description | Repo Dependent | Config | Tested |
|--------|-------------|----------------|--------|--------|
| `sequence_to_structure.py` | Convert amino acid sequences to cyclic peptide SMILES | No | `configs/sequence_to_structure_config.json` | ✅ |
| `structure_to_sequence.py` | Convert SMILES structures to amino acid sequences | No | `configs/structure_to_sequence_config.json` | ✅ |
| `calculate_properties.py` | Calculate molecular properties and descriptors | No | `configs/calculate_properties_config.json` | ✅ |
| `preprocess_data.py` | Data preprocessing and standardization | No | `configs/preprocess_data_config.json` | ✅ |
| `analyze_structure.py` | Generate comprehensive structure analysis reports | No | `configs/analyze_structure_config.json` | ✅ |

## Quick Start

```bash
# Activate environment (prefer mamba over conda)
mamba activate ./env  # or: conda activate ./env

# Run a script with default settings
python scripts/sequence_to_structure.py --sequence APG --output results/apg.smi

# Run with custom config
python scripts/calculate_properties.py --smiles "SMILES_STRING" --config configs/my_config.json

# Batch processing
python scripts/preprocess_data.py --input data.csv --output cleaned_data.csv
```

## Detailed Usage

### 1. Sequence to Structure Conversion

Converts amino acid sequences to cyclic peptide SMILES representations.

**Features:**
- Supports standard 20 amino acids (1-letter and 3-letter codes)
- Generates cyclic or linear peptides
- Creates structure visualizations (SVG)
- Quality assessment and validation

**Usage:**
```bash
# Single sequence
python scripts/sequence_to_structure.py --sequence APG --visualize --output results/

# Batch from file
python scripts/sequence_to_structure.py --input sequences.txt --output results/

# Linear peptide
python scripts/sequence_to_structure.py --sequence GFPVFP --linear --output linear.smi
```

**Example Output:**
```
Sequence: APG
SMILES: C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O
Type: cyclic
Quality Score: 100/100
```

### 2. Structure to Sequence Conversion

Converts SMILES structures back to amino acid sequences.

**Features:**
- Pattern-based amino acid recognition
- Molecular composition analysis
- Peptide bond detection
- Confidence scoring

**Usage:**
```bash
# Single SMILES
python scripts/structure_to_sequence.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O"

# Batch from file
python scripts/structure_to_sequence.py --input smiles.txt --format csv --output results.csv
```

**Example Output:**
```
SMILES: C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O
Detected Sequence: APG
Molecular Weight: 225.11
Is Cyclic: True
Quality Score: 98/100
```

### 3. Property Calculation

Calculates comprehensive molecular properties and drug-likeness rules.

**Features:**
- 50+ molecular descriptors
- Multiple fingerprint types
- Drug-likeness rules (Lipinski, Veber, Ghose)
- Quality assessment

**Usage:**
```bash
# Basic properties
python scripts/calculate_properties.py --smiles "SMILES" --format csv

# Skip fingerprints for faster processing
python scripts/calculate_properties.py --smiles "SMILES" --no-fingerprints

# Batch processing with visualization
python scripts/calculate_properties.py --input smiles_file.txt --visualize --format json
```

**Key Properties Calculated:**
- Molecular weight, LogP, TPSA
- H-bond donors/acceptors
- Rotatable bonds, ring count
- Rule of 5 compliance
- Morgan, RDKit, MACCS fingerprints

### 4. Data Preprocessing

Standardizes and cleans cyclic peptide datasets.

**Features:**
- Auto-detects column types (SMILES/sequences)
- SMILES canonicalization
- Sequence format normalization
- Quality scoring and filtering
- Duplicate removal

**Usage:**
```bash
# Basic preprocessing
python scripts/preprocess_data.py --input data.csv --output cleaned.csv

# With quality filtering
python scripts/preprocess_data.py --input data.csv --min-quality 60 --remove-duplicates

# Custom config
python scripts/preprocess_data.py --input data.csv --config my_preprocess_config.json
```

**Processing Features:**
- Validates SMILES and sequences
- Adds standardized columns
- Quality scores (0-100)
- Processing summary report

### 5. Structure Analysis

Generates comprehensive HTML reports analyzing cyclic peptide structures.

**Features:**
- Complete molecular analysis
- Sequence detection and composition
- Drug-likeness assessment
- Interactive visualizations
- Publication-quality reports

**Usage:**
```bash
# Full analysis report
python scripts/analyze_structure.py --smiles "SMILES" --output report.html

# Skip certain sections
python scripts/analyze_structure.py --smiles "SMILES" --no-visualization --no-drug-rules

# Batch analysis
python scripts/analyze_structure.py --input smiles.txt --format html
```

**Report Sections:**
- Structure overview with visualization
- Sequence analysis and composition
- Molecular properties
- Drug-likeness assessment
- Quality evaluation

## Shared Library

Common functions are in `scripts/lib/`:

### `lib/molecules.py`
- Molecular manipulation utilities
- RDKit wrapper functions
- SMILES/sequence conversion
- Visualization generation

### `lib/io.py`
- File loading/saving utilities
- Format auto-detection
- Batch processing helpers
- Summary report generation

### `lib/validation.py`
- Input validation functions
- Quality assessment
- Data integrity checks
- Error handling

## Configuration

All scripts support JSON configuration files for customizable behavior:

### Example Config (`configs/sequence_to_structure_config.json`):
```json
{
  "cyclic": true,
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

### Global Defaults (`configs/default_config.json`):
```json
{
  "global": {
    "validate_inputs": true,
    "error_handling": "continue",
    "verbose": true
  },
  "visualization": {
    "enabled": false,
    "width": 400,
    "height": 400
  }
}
```

## MCP Integration

Each script exports a main function ready for MCP wrapping:

```python
# Example MCP tool wrapper
from scripts.sequence_to_structure import run_sequence_to_structure
from scripts.calculate_properties import run_calculate_properties

@mcp.tool()
def convert_sequence_to_structure(sequence: str, cyclic: bool = True) -> dict:
    """Convert amino acid sequence to cyclic peptide SMILES structure."""
    return run_sequence_to_structure(sequence=sequence, config={"cyclic": cyclic})

@mcp.tool()
def calculate_peptide_properties(smiles: str) -> dict:
    """Calculate comprehensive properties for a cyclic peptide."""
    return run_calculate_properties(smiles=smiles)
```

## Dependencies

### Required Packages:
- **RDKit** (2025.09.3+) - Core chemistry operations
- **NumPy** - Numerical operations
- **Pandas** - Data manipulation
- **Pathlib** - Path handling

### Optional:
- **Matplotlib** - Enhanced visualizations
- **IPython** - Notebook support

## Testing

All scripts have been tested with example data:

```bash
# Test sequence conversion
python scripts/sequence_to_structure.py --sequence APG --output test.smi --visualize

# Test property calculation
python scripts/calculate_properties.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --format csv

# Test preprocessing
python scripts/preprocess_data.py --input examples/data/example_peptides.csv --output test.csv
```

## Error Handling

Scripts include robust error handling:

- **Input validation**: Invalid SMILES/sequences are detected and flagged
- **Graceful degradation**: Processing continues despite individual failures
- **Quality assessment**: All outputs include quality scores
- **Detailed logging**: Comprehensive error messages and warnings

## Performance

Optimized for MCP use:

- **Fast startup**: Minimal imports and lazy loading
- **Memory efficient**: Streaming processing for large datasets
- **Configurable**: Skip expensive operations when not needed
- **Batch optimized**: Efficient processing of multiple inputs

## File Formats

### Supported Input Formats:
- **CSV**: Structured data with headers
- **TXT**: Plain text, one item per line
- **SMI**: SMILES format files
- **JSON**: Structured JSON data

### Output Formats:
- **CSV**: Tabular data
- **JSON**: Structured results
- **TXT**: Plain text reports
- **HTML**: Rich analysis reports
- **SVG**: Structure visualizations

## Known Limitations

1. **Sequence Detection**: Complex modifications may not be recognized
2. **Non-standard AA**: Only standard 20 amino acids supported
3. **Large Molecules**: Very large peptides may have performance issues
4. **3D Properties**: Some descriptors require 3D coordinates

## Troubleshooting

### Common Issues:

**ImportError with RDKit:**
```bash
# Ensure RDKit is properly installed
mamba install -c conda-forge rdkit

# Check import
python -c "from rdkit import Chem; print('RDKit OK')"
```

**"Module not found" errors:**
```bash
# Run from the project root directory
cd /path/to/cyclicpeptide_mcp
python scripts/script_name.py
```

**Memory issues with large datasets:**
```bash
# Use batch processing or reduce fingerprint calculations
python scripts/calculate_properties.py --no-fingerprints --input large_file.csv
```

## Future Enhancements

Potential improvements for MCP integration:

1. **Parallel Processing**: Multi-threading support for large batches
2. **Custom AA Support**: Extended amino acid library
3. **3D Structure Generation**: Conformer generation and optimization
4. **Machine Learning**: Predictive models for properties
5. **Visualization**: Interactive molecular viewers
6. **Validation**: Enhanced chemical structure validation

## Support

For issues with the scripts:
1. Check the configuration files
2. Verify input data formats
3. Review error messages and logs
4. Test with simple examples first
5. Check RDKit installation and environment