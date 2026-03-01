# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-31
- **Filter Applied**: Structure2Sequence, Sequence2Structure, GraphAlignment, PropertyAnalysis for cyclic peptides, preprocessing and standardization
- **Python Version**: 3.12.12
- **Environment Strategy**: Single environment (./env)
- **Source Repository**: cyclicpeptide (dfwlab/cyclicpeptide)

## Use Cases Identified and Implemented

### UC-001: Sequence to Structure (Essential Amino Acids)
- **Description**: Convert amino acid sequences to SMILES representations for cyclic peptides using standard 20 amino acids
- **Script Path**: `examples/use_case_1_sequence_to_structure.py`
- **Complexity**: Simple
- **Priority**: High
- **Environment**: `./env`
- **Source**: `repo/cyclicpeptide/Cyclicpeptide_test.ipynb`, `cyclicpeptide/Sequence2Structure.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequence | string | Amino acid sequence (1-letter codes) | --sequence, -s |
| batch_file | file | Multiple sequences file | --batch, -b |
| cyclic | boolean | Create cyclic vs linear peptide | --linear (flag) |
| visualize | boolean | Generate structure visualization | --visualize, -v |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| smiles_file | file | SMILES output (.smi format) |
| svg_file | file | Structure visualization (.svg) |
| summary_file | file | Batch processing summary |

**Example Usage:**
```bash
python examples/use_case_1_sequence_to_structure.py --sequence APG --visualize
python examples/use_case_1_sequence_to_structure.py --batch examples/data/sequences.txt
```

**Example Data**: `examples/data/sequences.txt` (APG, GFPVFP, WAGFP, etc.)

---

### UC-002: Structure to Sequence (Essential Amino Acids)
- **Description**: Convert SMILES structures back to amino acid sequences for peptides containing only standard amino acids
- **Script Path**: `examples/use_case_2_structure_to_sequence.py`
- **Complexity**: Simple
- **Priority**: High
- **Environment**: `./env`
- **Source**: `repo/cyclicpeptide/Cyclicpeptide_test.ipynb`, `cyclicpeptide/Structure2Sequence.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| smiles | string | SMILES representation | --smiles, -s |
| input_file | file | Multiple SMILES file | --input, -i |
| visualize | boolean | Generate structure visualization | --visualize, -v |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| sequence_file | file | Detected amino acid sequence |
| svg_file | file | Structure visualization |
| summary_file | file | Batch processing summary |

**Example Usage:**
```bash
python examples/use_case_2_structure_to_sequence.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --visualize
python examples/use_case_2_structure_to_sequence.py --input examples/data/smiles.txt
```

**Example Data**: `examples/data/smiles.txt` (SMILES for APG, alpha-Amanitine, modified peptides)

---

### UC-003: General Structure Analysis with Custom Monomer Database
- **Description**: Comprehensive structure analysis for any cyclic peptide using custom monomer database, supporting non-standard amino acids and modifications
- **Script Path**: `examples/use_case_3_structure_analysis.py`
- **Complexity**: Medium
- **Priority**: High
- **Environment**: `./env`
- **Source**: `repo/cyclicpeptide/Cyclicpeptide_test.ipynb`, `cyclicpeptide/Structure2Sequence.py#transform`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| smiles | string | SMILES representation | --smiles, -s |
| input_file | file | Multiple SMILES file | --input, -i |
| monomers_path | file | Custom monomer database | --monomers, -m |
| visualize | boolean | Generate structure visualization | --visualize, -v |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| html_report | file | Comprehensive analysis report (.html) |
| svg_file | file | Structure visualization |

**Example Usage:**
```bash
python examples/use_case_3_structure_analysis.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --visualize
python examples/use_case_3_structure_analysis.py --input examples/data/smiles.txt --monomers examples/data/monomer.tsv
```

**Example Data**: `examples/data/monomer.tsv` (546 monomer database), `examples/data/smiles.txt`

---

### UC-004: Property Analysis
- **Description**: Calculate comprehensive chemical and physical properties including molecular descriptors, fingerprints, and drug-likeness rules
- **Script Path**: `examples/use_case_4_property_analysis.py`
- **Complexity**: Medium
- **Priority**: High
- **Environment**: `./env`
- **Source**: `cyclicpeptide/PropertyAnalysis.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| smiles | string | SMILES representation | --smiles, -s |
| input_file | file | Multiple SMILES file | --input, -i |
| output_format | string | Output format (json/csv/txt) | --format, -f |
| visualize | boolean | Generate structure visualization | --visualize, -v |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| properties_file | file | Calculated properties (json/csv/txt) |
| summary_file | file | Batch processing summary |
| svg_file | file | Structure visualization |

**Properties Calculated:**
- Molecular descriptors (MW, LogP, TPSA, etc.)
- Drug-likeness rules (Lipinski, Veber, Ghose)
- Molecular fingerprints (RDKit, Morgan, MACCS)

**Example Usage:**
```bash
python examples/use_case_4_property_analysis.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --format csv --visualize
python examples/use_case_4_property_analysis.py --input examples/data/smiles.txt --format json
```

**Example Data**: `examples/data/smiles.txt`, `examples/data/Chemical_P.csv` (reference properties)

---

### UC-005: Graph Alignment with GCN Model
- **Description**: Graph-based similarity analysis using Graph Convolutional Networks to compare cyclic peptide sequences based on their graph representations
- **Script Path**: `examples/use_case_5_graph_alignment.py`
- **Complexity**: Complex
- **Priority**: Medium (requires PyTorch)
- **Environment**: `./env` (with optional PyTorch installation)
- **Source**: `repo/cyclicpeptide/GCN/GA_GCN_usage.ipynb`, `cyclicpeptide/GraphAlignment.py`

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| sequences | list | List of cyclic peptide sequences | --sequences, -s |
| input_file | file | Sequences file | --input, -i |
| query_sequence | string | Query sequence for comparison | --query, -q |
| model_path | file | Pre-trained GCN model | --model, -m |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| similarity_results | file | Similarity scores (.csv) |
| similarity_matrix | file | All-vs-all similarity matrix |
| sequence_mapping | file | Sequence ID mappings |

**Example Usage:**
```bash
python examples/use_case_5_graph_alignment.py --query "Ala(1)--Ala--Gly--Phe--Pro--Val--Phe--Phe(1)" --input examples/data/cyclic_sequences.txt
python examples/use_case_5_graph_alignment.py --sequences "Ala(1)--Ala--Gly--Phe(1)" "Pro(1)--Val--Phe--Ala(1)"
```

**Example Data**: `examples/data/cyclic_sequences.txt`, `examples/data/models/GA_GCN.pth` (44KB pre-trained model)

**Note**: Requires PyTorch and PyTorch Geometric for full functionality

---

### UC-006: Preprocessing and Standardization
- **Description**: Preprocess and standardize cyclic peptide data including SMILES canonicalization, sequence validation, and data cleaning
- **Script Path**: `examples/use_case_6_preprocessing.py`
- **Complexity**: Medium
- **Priority**: Medium
- **Environment**: `./env`
- **Source**: Custom implementation using RDKit and cyclicpeptide validation functions

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | file | Raw peptide data (CSV/JSON/TXT) | --input, -i |
| output_format | string | Output format (csv/json) | --format, -f |
| column_mapping | string | Column name mappings | --smiles-col, --sequence-col, etc. |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| standardized_data | file | Clean, validated data |
| invalid_records | file | Records that failed validation |
| summary_report | file | Data quality summary |

**Validation Features:**
- SMILES canonicalization
- Sequence format validation
- Data quality scoring
- Error identification and reporting

**Example Usage:**
```bash
python examples/use_case_6_preprocessing.py --input examples/data/example_peptides.csv --format csv
python examples/use_case_6_preprocessing.py --input examples/data/smiles.txt --format json
```

**Example Data**: `examples/data/example_peptides.csv` (mixed quality data for testing)

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total Use Cases Found | 6 |
| Scripts Created | 6 |
| High Priority | 4 |
| Medium Priority | 2 |
| Low Priority | 0 |
| Demo Data Files Created | 8+ |
| Simple Complexity | 2 |
| Medium Complexity | 3 |
| Complex Complexity | 1 |

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/cyclicpeptide/states/monomer.tsv` | `examples/data/monomer.tsv` | 546 monomer database for extended AA |
| `repo/cyclicpeptide/states/aa_smiles.txt` | `examples/data/aa_smiles.txt` | Amino acid SMILES mappings |
| `repo/cyclicpeptide/states/Chemical_P.csv` | `examples/data/Chemical_P.csv` | Chemical properties reference |
| `repo/cyclicpeptide/states/AminoAcids.txt` | `examples/data/AminoAcids.txt` | Amino acid reference data |
| `repo/cyclicpeptide/GCN/GA_GCN.pth` | `examples/data/models/GA_GCN.pth` | Pre-trained GCN model (44KB) |
| Created | `examples/data/sequences.txt` | Sample essential AA sequences |
| Created | `examples/data/smiles.txt` | Sample SMILES strings |
| Created | `examples/data/cyclic_sequences.txt` | Sample cyclic peptide sequences |
| Created | `examples/data/example_peptides.csv` | Mixed dataset for preprocessing |

## Functional Verification

All use cases have been implemented as standalone Python scripts with comprehensive error handling, help text, and example usage. Each script includes:

1. **Argument parsing** with sensible defaults
2. **Input validation** and error handling
3. **Batch processing** capabilities where applicable
4. **Multiple output formats** (CSV, JSON, TXT, HTML, SVG)
5. **Example usage** when run without arguments
6. **Comprehensive documentation** and help text

The scripts are designed to be easily convertible into MCP tools with clear input/output specifications and standardized interfaces.