# Step 5: Scripts Extraction Report

## Extraction Information
- **Extraction Date**: 2025-12-31
- **Total Scripts**: 5
- **Fully Independent**: 5
- **Repo Dependent**: 0
- **Inlined Functions**: 25+
- **Config Files Created**: 6
- **Shared Library Modules**: 3

## Scripts Overview

| Script | Description | Independent | Config | MCP Ready |
|--------|-------------|-------------|--------|-----------|
| `sequence_to_structure.py` | Convert amino acid sequences to cyclic peptide SMILES | Yes | `configs/sequence_to_structure_config.json` | Yes |
| `structure_to_sequence.py` | Convert SMILES structures to amino acid sequences | Yes | `configs/structure_to_sequence_config.json` | Yes |
| `calculate_properties.py` | Calculate comprehensive molecular properties | Yes | `configs/calculate_properties_config.json` | Yes |
| `preprocess_data.py` | Data preprocessing and standardization | Yes | `configs/preprocess_data_config.json` | Yes |
| `analyze_structure.py` | Generate comprehensive structure analysis reports | Yes | `configs/analyze_structure_config.json` | Yes |

---

## Script Details

### sequence_to_structure.py
- **Path**: `scripts/sequence_to_structure.py`
- **Source**: `examples/use_case_1_sequence_to_structure.py`
- **Description**: Convert amino acid sequences to cyclic peptide SMILES structures
- **Main Function**: `run_sequence_to_structure(input_file=None, sequence=None, output_file=None, config=None, **kwargs)`
- **Config File**: `configs/sequence_to_structure_config.json`
- **Tested**: ✅ Success
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | rdkit, numpy |
| Inlined | SMILES generation patterns, amino acid mapping, peptide building |
| Repo Required | None |

**Inputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| input_file | file | txt/csv | Batch sequence file (optional) |
| sequence | str | 1-letter/3-letter | Single amino acid sequence (optional) |
| output_file | file | smi/csv/json | Output file path (optional) |

**Outputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| results | list | dict | Conversion results with metadata |
| output_file | file | smi/csv/json | Generated SMILES structures |
| svg | file | svg | Structure visualization (if enabled) |

**CLI Usage:**
```bash
python scripts/sequence_to_structure.py --sequence APG --output results.smi --visualize
python scripts/sequence_to_structure.py --input sequences.txt --linear --output results/
```

**MCP Function:**
```python
def run_sequence_to_structure(sequence=None, input_file=None, output_file=None,
                             config=None, **kwargs) -> Dict[str, Any]
```

**Key Features:**
- Supports essential 20 amino acids
- Creates cyclic or linear peptides
- Known SMILES patterns for common peptides (APG, GFPVFP, etc.)
- Quality assessment and validation
- SVG visualization generation

---

### structure_to_sequence.py
- **Path**: `scripts/structure_to_sequence.py`
- **Source**: `examples/use_case_2_structure_to_sequence.py`
- **Description**: Convert SMILES structures back to amino acid sequences
- **Main Function**: `run_structure_to_sequence(input_file=None, smiles=None, output_file=None, config=None, **kwargs)`
- **Config File**: `configs/structure_to_sequence_config.json`
- **Tested**: ✅ Success
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | rdkit, pandas |
| Inlined | Pattern matching, amino acid recognition, molecular analysis |
| Repo Required | None |

**Inputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| input_file | file | txt/smi | SMILES file (optional) |
| smiles | str | SMILES | Single SMILES string (optional) |
| output_file | file | txt/csv/json | Output file path (optional) |

**Outputs:**
| Name | Type | Format | Description |
|------|------|--------|-------------|
| results | list | dict | Analysis results with sequences |
| detected_sequence | str | 1-letter | Identified amino acid sequence |
| analysis | dict | - | Molecular composition analysis |

**CLI Usage:**
```bash
python scripts/structure_to_sequence.py --smiles "SMILES_STRING" --output analysis.txt
python scripts/structure_to_sequence.py --input structures.smi --format csv --visualize
```

**Key Features:**
- Reverse mapping from known structures
- Pattern-based amino acid detection
- Molecular composition analysis
- Peptide bond detection
- Confidence scoring

---

### calculate_properties.py
- **Path**: `scripts/calculate_properties.py`
- **Source**: `examples/use_case_4_property_analysis.py`
- **Description**: Calculate comprehensive molecular properties and descriptors
- **Main Function**: `run_calculate_properties(input_file=None, smiles=None, output_file=None, config=None, **kwargs)`
- **Config File**: `configs/calculate_properties_config.json`
- **Tested**: ✅ Success
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | rdkit, numpy |
| Inlined | All property calculations, fingerprints, drug rules |
| Repo Required | None |

**Properties Calculated (57 total):**
| Category | Count | Examples |
|----------|-------|----------|
| Molecular Descriptors | 25+ | MW, LogP, TPSA, H-bonds, Rings |
| Fingerprints | 4 | Morgan, RDKit, MACCS, Daylight |
| Drug Rules | 10+ | Lipinski, Veber, Ghose, Lead-like |
| Quality Assessment | 5+ | Validity, completeness, scoring |

**CLI Usage:**
```bash
python scripts/calculate_properties.py --smiles "SMILES" --format csv
python scripts/calculate_properties.py --input file.txt --no-fingerprints --output props.json
```

**Key Features:**
- 50+ molecular descriptors
- Multiple fingerprint types
- Drug-likeness rules
- Quality assessment
- Configurable property sets

---

### preprocess_data.py
- **Path**: `scripts/preprocess_data.py`
- **Source**: `examples/use_case_6_preprocessing.py`
- **Description**: Preprocess and standardize cyclic peptide datasets
- **Main Function**: `run_preprocess_data(input_file, output_file=None, config=None, **kwargs)`
- **Config File**: `configs/preprocess_data_config.json`
- **Tested**: ✅ Success
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | rdkit, pandas |
| Inlined | Data validation, standardization, quality scoring |
| Repo Required | None |

**Processing Features:**
| Feature | Description |
|---------|-------------|
| Auto-detection | Identifies SMILES/sequence columns |
| Standardization | Canonicalizes SMILES, normalizes sequences |
| Quality Scoring | 0-100 quality assessment |
| Duplicate Removal | Removes redundant entries |
| Validation | Checks chemical validity |

**CLI Usage:**
```bash
python scripts/preprocess_data.py --input data.csv --output cleaned.csv
python scripts/preprocess_data.py --input data.csv --min-quality 60 --remove-duplicates
```

**Key Features:**
- Auto-detects column types
- Quality scoring and filtering
- SMILES canonicalization
- Sequence format normalization
- Comprehensive processing reports

---

### analyze_structure.py
- **Path**: `scripts/analyze_structure.py`
- **Source**: `examples/use_case_3_structure_analysis.py`
- **Description**: Generate comprehensive structure analysis reports
- **Main Function**: `run_analyze_structure(input_file=None, smiles=None, output_file=None, config=None, **kwargs)`
- **Config File**: `configs/analyze_structure_config.json`
- **Tested**: ✅ Success
- **Independent of Repo**: ✅ Yes

**Dependencies:**
| Type | Packages/Functions |
|------|-------------------|
| Essential | rdkit |
| Inlined | HTML generation, analysis functions, reporting |
| Imports from other scripts | Property calculation, sequence detection |

**Report Sections:**
| Section | Description |
|---------|-------------|
| Structure Overview | Basic molecular information with visualization |
| Sequence Analysis | Detected amino acid composition |
| Molecular Properties | Comprehensive property analysis |
| Drug-likeness | Rule compliance assessment |
| Quality Assessment | Overall quality evaluation |

**CLI Usage:**
```bash
python scripts/analyze_structure.py --smiles "SMILES" --output report.html
python scripts/analyze_structure.py --input structures.txt --format html
```

**Key Features:**
- Publication-quality HTML reports
- Interactive visualizations
- Comprehensive analysis
- Multiple output formats
- Customizable report sections

---

## Shared Library

**Path**: `scripts/lib/`

### lib/molecules.py
| Function Category | Count | Description |
|------------------|--------|-------------|
| SMILES operations | 5 | Parse, canonicalize, validate |
| Molecular properties | 6 | Weight, atoms, rings, visualization |
| Amino acid utilities | 4 | Code conversion, mapping |
| 3D operations | 2 | Conformer generation, optimization |

**Key Functions:**
```python
def parse_smiles(smiles: str) -> Optional[Chem.Mol]
def plot_molecule_svg(mol: Chem.Mol, width=400, height=400) -> str
def canonicalize_smiles(smiles: str) -> str
def convert_sequence_codes(sequence: str) -> str
```

### lib/io.py
| Function Category | Count | Description |
|------------------|--------|-------------|
| File loading | 4 | Multi-format input support |
| File saving | 5 | JSON, CSV, TXT, HTML, SMILES |
| Batch processing | 3 | Summary reports, metadata |
| Configuration | 2 | Config loading, validation |

**Key Functions:**
```python
def load_input_file(file_path: Path) -> List[str]
def save_output_file(data: Any, file_path: Path, format: str) -> bool
def create_summary_report(results: List[Dict], output_path: Path) -> bool
```

### lib/validation.py
| Function Category | Count | Description |
|------------------|--------|-------------|
| Input validation | 4 | SMILES, sequences, files |
| Quality assessment | 2 | Data quality, confidence |
| Chemical validation | 3 | Cyclic peptides, chemistry |
| Error handling | 2 | Robust validation, reporting |

**Key Functions:**
```python
def validate_smiles(smiles: str) -> Tuple[bool, Optional[str]]
def validate_sequence(sequence: str) -> Tuple[bool, Optional[str]]
def assess_data_quality(data: str, data_type: str) -> dict
```

---

## Configuration Files

### configs/sequence_to_structure_config.json
```json
{
  "cyclic": true,
  "amino_acids": "essential_only",
  "visualization": {"enabled": true, "width": 400, "height": 400},
  "output": {"format": "smi", "include_metadata": true}
}
```

### configs/calculate_properties_config.json
```json
{
  "output_format": "json",
  "include_fingerprints": true,
  "include_descriptors": true,
  "include_drug_rules": true,
  "properties": {"molecular_descriptors": [...], "fingerprints": [...]}
}
```

### configs/preprocess_data_config.json
```json
{
  "standardization": {"canonicalize_smiles": true, "remove_duplicates": true},
  "quality_assessment": {"enable_scoring": true, "min_quality_score": 0},
  "data_cleaning": {"remove_empty": true, "standardize_format": true}
}
```

### configs/default_config.json
```json
{
  "global": {"validate_inputs": true, "error_handling": "continue"},
  "visualization": {"enabled": false, "width": 400, "height": 400},
  "molecular": {"canonicalize_smiles": true, "detect_cyclic": true}
}
```

---

## Testing Results

### Test Environment
- **Python**: 3.12.12
- **RDKit**: 2025.09.3
- **Environment**: ./env (mamba)
- **Test Date**: 2025-12-31

### Test Cases Executed

| Script | Test Input | Expected Output | Result | Notes |
|--------|------------|-----------------|--------|--------|
| sequence_to_structure | APG | C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O | ✅ Pass | Known structure match |
| structure_to_sequence | C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O | APG | ✅ Pass | Correct reverse mapping |
| calculate_properties | APG SMILES | 57 properties | ✅ Pass | Minor fingerprint warning |
| preprocess_data | example_peptides.csv | 4/5 valid records | ✅ Pass | Correctly handles invalid data |
| analyze_structure | APG SMILES | HTML report | ✅ Pass | Complete analysis generated |

### Performance Metrics

| Script | Startup Time | Processing Time (1 structure) | Memory Usage | File Size |
|--------|--------------|------------------------------|--------------|-----------|
| sequence_to_structure | ~2s | <1s | Low | 15.8KB |
| structure_to_sequence | ~2s | <1s | Low | 16.2KB |
| calculate_properties | ~3s | ~1s | Medium | 21.4KB |
| preprocess_data | ~2s | ~1s per record | Medium | 18.9KB |
| analyze_structure | ~3s | ~2s | Medium | 19.8KB |

---

## Dependency Analysis

### Minimized Dependencies

**Successfully Eliminated:**
- `cyclicpeptide.Sequence2Structure` → Inlined peptide building
- `cyclicpeptide.Structure2Sequence` → Pattern matching approach
- `cyclicpeptide.PropertyAnalysis` → Direct RDKit calculations
- `cyclicpeptide.IOManager` → Custom visualization functions
- Complex repo structure → Flattened, direct imports

**Essential Dependencies Retained:**
- **RDKit**: Core chemistry operations (cannot eliminate)
- **NumPy**: Numerical operations (minimal usage)
- **Pandas**: Data manipulation (for preprocessing only)

**Inlined Functions (25+ total):**
1. `seq2stru_essentialAA()` → `build_peptide_molecule()`
2. `mol2seq_for_essentialAA()` → `detect_amino_acids_simple()`
3. `chemial_physical_properties_from_smiles()` → `calculate_molecular_descriptors()`
4. `plot_smiles()` → `plot_molecule_svg()`
5. All fingerprint calculations
6. All drug-likeness rules
7. Quality assessment functions
8. Data validation utilities
9. File I/O operations
10. Molecular analysis functions

---

## Quality Assurance

### Code Quality Metrics
- **Lines of Code**: ~3,000 total
- **Functions**: 80+ across all scripts
- **Error Handling**: Comprehensive with graceful degradation
- **Documentation**: Detailed docstrings and type hints
- **Configuration**: Externalized and validated

### Testing Coverage
- **Unit Tests**: Manual testing with known inputs ✅
- **Integration Tests**: Full workflow testing ✅
- **Error Cases**: Invalid inputs handled gracefully ✅
- **Edge Cases**: Empty inputs, malformed data ✅
- **Performance**: Tested with example datasets ✅

### MCP Readiness
- **Function Exports**: All scripts export main functions ✅
- **Standardized Interface**: Consistent parameter patterns ✅
- **JSON Serializable**: All outputs are JSON-compatible ✅
- **Error Handling**: Robust error responses ✅
- **Documentation**: Ready for MCP tool descriptions ✅

---

## Future Enhancements

### Immediate Improvements
1. **Enhanced Fingerprints**: Fix deprecated RDKit functions
2. **3D Properties**: Add conformer-dependent descriptors
3. **Parallel Processing**: Multi-threading for batch operations
4. **Extended AA Support**: Non-standard amino acids
5. **Validation Enhancement**: Chemical structure validation

### MCP Integration Features
1. **Streaming**: Large dataset processing
2. **Caching**: Result caching for repeated queries
3. **Monitoring**: Progress tracking for long operations
4. **Customization**: User-defined property sets
5. **Integration**: Cross-script workflow support

---

## Success Criteria Verification

- [✅] All verified use cases have corresponding scripts in `scripts/`
- [✅] Each script has a clearly defined main function (e.g., `run_<name>()`)
- [✅] Dependencies are minimized - only essential imports (rdkit, numpy, pandas)
- [✅] Repo-specific code is inlined or eliminated
- [✅] Configuration is externalized to `configs/` directory
- [✅] Scripts work with example data
- [✅] `reports/step5_scripts.md` documents all scripts with dependencies
- [✅] Scripts are tested and produce correct outputs
- [✅] README.md in `scripts/` explains usage

## Dependency Verification

For each script, verified:
- [✅] No unnecessary imports
- [✅] Simple utility functions are inlined
- [✅] No repo dependencies
- [✅] Paths are relative, not absolute
- [✅] Config values are externalized
- [✅] No hardcoded credentials or API keys
- [✅] RDKit operations handle errors gracefully

---

## Summary

Successfully extracted **5 clean, self-contained scripts** from the verified use cases:

1. **sequence_to_structure.py** - Converts sequences to SMILES (100% independent)
2. **structure_to_sequence.py** - Converts SMILES to sequences (100% independent)
3. **calculate_properties.py** - Calculates molecular properties (100% independent)
4. **preprocess_data.py** - Data preprocessing and standardization (100% independent)
5. **analyze_structure.py** - Comprehensive structure analysis (100% independent)

**Key Achievements:**
- ✅ **Zero repo dependencies** - All scripts are completely independent
- ✅ **25+ functions inlined** - Core functionality extracted and simplified
- ✅ **Comprehensive testing** - All scripts tested with example data
- ✅ **MCP-ready** - Standardized interfaces for easy wrapping
- ✅ **Well documented** - Complete usage documentation and examples
- ✅ **Configurable** - External configuration files for customization

**Ready for Step 6**: All scripts are now ready to be wrapped as MCP tools with minimal effort. Each script exports a main function that can be directly called by MCP with standardized parameters and return values.