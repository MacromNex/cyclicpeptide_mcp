# Cyclicpeptide MCP - Examples Directory

This directory contains example scripts and demo data for the Cyclicpeptide MCP tool.

## Use Case Scripts

### Use Case 1: Sequence to Structure
**Script**: `use_case_1_sequence_to_structure.py`
**Description**: Convert amino acid sequences to SMILES structures for cyclic peptides (essential amino acids only)

**Example Usage**:
```bash
python use_case_1_sequence_to_structure.py --sequence APG --visualize
python use_case_1_sequence_to_structure.py --batch data/sequences.txt --output results/
```

### Use Case 2: Structure to Sequence
**Script**: `use_case_2_structure_to_sequence.py`
**Description**: Convert SMILES structures back to amino acid sequences (essential amino acids only)

**Example Usage**:
```bash
python use_case_2_structure_to_sequence.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --visualize
python use_case_2_structure_to_sequence.py --input data/smiles.txt --output results/
```

### Use Case 3: Structure Analysis
**Script**: `use_case_3_structure_analysis.py`
**Description**: Comprehensive structure analysis with custom monomer database (supports non-standard amino acids)

**Example Usage**:
```bash
python use_case_3_structure_analysis.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --visualize
python use_case_3_structure_analysis.py --input data/smiles.txt --monomers data/monomer.tsv
```

### Use Case 4: Property Analysis
**Script**: `use_case_4_property_analysis.py`
**Description**: Calculate comprehensive chemical and physical properties including molecular descriptors and drug-likeness rules

**Example Usage**:
```bash
python use_case_4_property_analysis.py --smiles "C[C@@H]1NC(=O)CNC(=O)[C@@H]2CCCN2C1=O" --format csv --visualize
python use_case_4_property_analysis.py --input data/smiles.txt --format json
```

### Use Case 5: Graph Alignment
**Script**: `use_case_5_graph_alignment.py`
**Description**: Graph-based similarity analysis using Graph Convolutional Networks (requires PyTorch)

**Example Usage**:
```bash
python use_case_5_graph_alignment.py --query "Ala(1)--Ala--Gly--Phe--Pro--Val--Phe--Phe(1)" --input data/cyclic_sequences.txt
python use_case_5_graph_alignment.py --sequences "Ala(1)--Ala--Gly--Phe(1)" "Pro(1)--Val--Phe--Ala(1)"
```

### Use Case 6: Preprocessing and Standardization
**Script**: `use_case_6_preprocessing.py`
**Description**: Preprocess and standardize cyclic peptide data including SMILES canonicalization and sequence validation

**Example Usage**:
```bash
python use_case_6_preprocessing.py --input data/example_peptides.csv --format csv
python use_case_6_preprocessing.py --input data/smiles.txt --format json
```

## Demo Data

### Directory Structure
```
data/
├── sequences/          # Sample amino acid sequences
├── structures/         # Sample 3D structures (if any)
├── models/            # Pre-trained models
│   └── GA_GCN.pth     # Graph alignment GCN model
├── sequences.txt      # Sample essential amino acid sequences
├── smiles.txt         # Sample SMILES strings
├── cyclic_sequences.txt # Sample cyclic peptide sequences
├── example_peptides.csv # Mixed dataset for preprocessing
├── monomer.tsv        # Monomer database for structure analysis
├── aa_smiles.txt      # Amino acid SMILES mappings
├── Chemical_P.csv     # Chemical properties reference
└── AminoAcids.txt     # Amino acid reference data
```

### Data File Descriptions

- **sequences.txt**: Simple amino acid sequences using single-letter codes (A, P, G, etc.)
- **smiles.txt**: SMILES representations of cyclic peptides
- **cyclic_sequences.txt**: Sequences in cyclic peptide format with connection indicators
- **example_peptides.csv**: Mixed dataset with SMILES, sequences, names, and IDs for testing preprocessing
- **monomer.tsv**: Extended monomer database including non-standard amino acids
- **GA_GCN.pth**: Pre-trained Graph Convolutional Network model for graph alignment

### Running Examples

1. **Quick Test of All Use Cases**:
   ```bash
   # Run each script without arguments to see examples
   python use_case_1_sequence_to_structure.py
   python use_case_2_structure_to_sequence.py
   python use_case_3_structure_analysis.py
   python use_case_4_property_analysis.py
   python use_case_5_graph_alignment.py
   python use_case_6_preprocessing.py
   ```

2. **Batch Processing**:
   ```bash
   # Process multiple sequences
   python use_case_1_sequence_to_structure.py --batch data/sequences.txt --output results_batch/

   # Process multiple SMILES
   python use_case_4_property_analysis.py --input data/smiles.txt --output results_properties/
   ```

3. **Custom Analysis**:
   ```bash
   # Use custom monomer database
   python use_case_3_structure_analysis.py --input data/smiles.txt --monomers data/monomer.tsv

   # Graph alignment with custom sequences
   python use_case_5_graph_alignment.py --input data/cyclic_sequences.txt --model data/models/GA_GCN.pth
   ```

## Output Formats

- **SMILES**: `.smi` files for molecular structures
- **Sequences**: `.txt` files for amino acid sequences
- **Properties**: `.json`, `.csv`, or `.txt` files for calculated properties
- **Reports**: `.html` files for comprehensive analysis reports
- **Visualizations**: `.svg` files for molecular structure images

## Dependencies

All scripts are designed to work with the conda environment created in the main setup. Key dependencies include:

- RDKit (molecular manipulation)
- pandas (data processing)
- numpy (numerical operations)
- matplotlib (visualization)
- PyTorch & PyTorch Geometric (for graph alignment - optional)

See the main README.md for complete installation instructions.