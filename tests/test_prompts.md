# Cyclic Peptide MCP Server Test Prompts

## Tool Discovery Tests

### Test 1: List All Tools
**Prompt**: "What MCP tools are available for cyclic peptides? Give me a brief description of each."
**Expected**: List of 13 tools with descriptions
**Category**: Tool Discovery

### Test 2: Tool Details
**Prompt**: "Explain how to use the calculate_cyclic_peptide_properties tool, including all parameters."
**Expected**: Detailed explanation of tool parameters and usage
**Category**: Tool Discovery

## Sync Tool Tests (Fast Operations < 10 min)

### Test 3: Property Calculation - Valid SMILES
**Prompt**: "Calculate properties for this cyclic peptide SMILES: cyclo(GRGDSP)"
**Expected**: Molecular properties (MW, logP, TPSA, etc.) returned within 30s
**Category**: Sync Tools
**Test Data**: cyclo(GRGDSP)

### Test 4: Property Calculation - Simple SMILES
**Prompt**: "Calculate molecular weight, logP and TPSA for SMILES: CC(=O)NC1CCCC1C(=O)O"
**Expected**: Properties calculated successfully
**Category**: Sync Tools
**Test Data**: CC(=O)NC1CCCC1C(=O)O

### Test 5: Sequence Conversion
**Prompt**: "Convert the peptide sequence 'GRGDSP' to a cyclic peptide SMILES with head-to-tail cyclization"
**Expected**: Valid cyclic peptide SMILES structure
**Category**: Sync Tools
**Test Data**: GRGDSP

### Test 6: Structure to Sequence Conversion
**Prompt**: "Convert this cyclic peptide SMILES back to amino acid sequence: CC(=O)NC1CCCC1C(=O)O"
**Expected**: Amino acid sequence or conversion result
**Category**: Sync Tools

### Test 7: Data Preprocessing
**Prompt**: "Preprocess this peptide data file for analysis: examples/data/sample_peptides.csv"
**Expected**: Preprocessed data output or error if file doesn't exist
**Category**: Sync Tools

### Test 8: Error Handling - Invalid SMILES
**Prompt**: "Calculate properties for an invalid SMILES string 'not_a_smiles_123'"
**Expected**: Clear error message explaining invalid SMILES
**Category**: Error Handling
**Test Data**: not_a_smiles_123

### Test 9: Error Handling - Empty Input
**Prompt**: "Calculate properties for empty SMILES string ''"
**Expected**: Clear error message about empty input
**Category**: Error Handling

## Submit API Tests (Long-Running Tasks)

### Test 10: Submit Structure Prediction
**Prompt**: "Submit a 3D structure prediction job for the cyclic peptide SMILES: cyclo(Ala-Gly-Pro-Phe)"
**Expected**: Job submission confirmation with job_id
**Category**: Submit API
**Test Data**: cyclo(Ala-Gly-Pro-Phe)

### Test 11: Submit with Simple SMILES
**Prompt**: "Submit comprehensive structure analysis for SMILES: CC(=O)NC1CCCC1C(=O)O"
**Expected**: Job submission successful
**Category**: Submit API
**Test Data**: CC(=O)NC1CCCC1C(=O)O

### Test 12: Check Job Status
**Prompt**: "Check the status of job {job_id}"
**Expected**: Job status (pending/running/completed/failed) with metadata
**Category**: Job Management
**Note**: Replace {job_id} with actual job ID from previous test

### Test 13: Get Job Results
**Prompt**: "Get the results for job {job_id}"
**Expected**: Job results if completed, or status message
**Category**: Job Management

### Test 14: View Job Logs
**Prompt**: "Show me the last 30 lines of logs for job {job_id}"
**Expected**: Log entries from job execution
**Category**: Job Management

### Test 15: List All Jobs
**Prompt**: "List all submitted jobs and their current status"
**Expected**: List of all jobs with status information
**Category**: Job Management

### Test 16: List Completed Jobs Only
**Prompt**: "List all jobs with status 'completed'"
**Expected**: Filtered list of completed jobs
**Category**: Job Management

### Test 17: Cancel Running Job
**Prompt**: "Cancel the job {job_id}"
**Expected**: Job cancellation confirmation or error if not cancellable
**Category**: Job Management

## Batch Processing Tests

### Test 18: Batch Property Calculation
**Prompt**: "Calculate properties for these cyclic peptides in batch: cyclo(GRGDSP), cyclo(RGDFV), cyclo(YIGSR)"
**Expected**: Batch job submission or individual results
**Category**: Batch Processing
**Test Data**: Multiple SMILES

### Test 19: Batch Sequence Conversion
**Prompt**: "Convert these sequences to cyclic peptide SMILES: GRGDSP, RGDFV, YIGSR"
**Expected**: Multiple SMILES conversions
**Category**: Batch Processing

### Test 20: Batch Structure Analysis
**Prompt**: "Submit batch structure analysis for multiple peptides from file examples/data/test_peptides.txt"
**Expected**: Batch job submission
**Category**: Batch Processing

## End-to-End Workflow Tests

### Test 21: Full Cyclic Peptide Workflow
**Prompt**: "For the cyclic peptide sequence GRGDSP:
1. Convert to SMILES with head-to-tail cyclization
2. Calculate molecular properties
3. Submit 3D structure prediction
Summarize all results."
**Expected**: Complete workflow execution
**Category**: End-to-End
**Test Data**: GRGDSP

### Test 22: Drug-likeness Assessment
**Prompt**: "Assess the drug-likeness of cyclic peptide cyclo(Pro-Leu-Gly-Phe-Ala):
- Calculate molecular weight, logP, and TPSA
- Check if it meets cyclic peptide drug criteria (MW < 2000, logP < 5)"
**Expected**: Properties calculated and drug-likeness assessment
**Category**: End-to-End
**Test Data**: cyclo(Pro-Leu-Gly-Phe-Ala)

### Test 23: Virtual Screening Workflow
**Prompt**: "Screen this small library of cyclic peptides for drug-like properties:
1. cyclo(GRGDSP) - integrin binding
2. cyclo(RGDFV) - shorter integrin binder
3. cyclo(YIGSR) - laminin binding
Calculate properties and identify the most drug-like candidate."
**Expected**: Properties for all peptides and comparison
**Category**: Virtual Screening

### Test 24: Structure Optimization Workflow
**Prompt**: "Submit conformational sampling for cyclo(GRGDSP) and while it's running, check the progress, then show me the results when complete."
**Expected**: Job submission -> status checking -> results retrieval
**Category**: End-to-End

### Test 25: Permeability Assessment
**Prompt**: "Assess membrane permeability potential for cyclo(Pro-Leu-Gly-Phe-Ala) by calculating relevant molecular descriptors"
**Expected**: Permeability-related properties calculated
**Category**: Drug Discovery

## Performance and Reliability Tests

### Test 26: Concurrent Jobs
**Prompt**: "Submit 3 different structure prediction jobs simultaneously for: cyclo(GRGDSP), cyclo(RGDFV), and cyclo(YIGSR)"
**Expected**: Multiple job submissions handled correctly
**Category**: Performance

### Test 27: Large SMILES Input
**Prompt**: "Calculate properties for this large cyclic peptide: [insert long SMILES string]"
**Expected**: Successful processing or appropriate error handling
**Category**: Performance

### Test 28: Invalid File Path
**Prompt**: "Process data from file 'non_existent_file.csv'"
**Expected**: Clear file not found error
**Category**: Error Handling

### Test 29: Malformed Sequence
**Prompt**: "Convert sequence 'XYZABC123' to SMILES"
**Expected**: Clear error about invalid amino acids
**Category**: Error Handling

### Test 30: Memory Stress Test
**Prompt**: "Submit batch processing for 100 identical peptides: cyclo(GRGDSP)"
**Expected**: Efficient batch handling or appropriate resource management
**Category**: Performance

## Integration Edge Cases

### Test 31: Mixed Valid/Invalid Batch
**Prompt**: "Calculate properties for: cyclo(GRGDSP), invalid_smiles_123, cyclo(RGDFV)"
**Expected**: Results for valid entries, errors for invalid ones
**Category**: Edge Cases

### Test 32: Special Characters in Input
**Prompt**: "Calculate properties for SMILES with special characters: 'cyclo(GRGDSP)@#$'"
**Expected**: Appropriate error handling
**Category**: Edge Cases

### Test 33: Empty Job Queue
**Prompt**: "List all jobs when no jobs have been submitted"
**Expected**: Empty job list or appropriate message
**Category**: Edge Cases

## Test Data Validation

### Required Test Files:
- examples/data/sample_peptides.csv (if exists)
- examples/data/test_peptides.txt (if exists)

### Expected SMILES for Testing:
- Valid cyclic peptides: cyclo(GRGDSP), cyclo(RGDFV), cyclo(YIGSR)
- Simple test molecule: CC(=O)NC1CCCC1C(=O)O
- Invalid SMILES: not_a_smiles_123, empty string

### Expected Sequences:
- GRGDSP, RGDFV, YIGSR
- Invalid: XYZABC123

## Success Criteria Per Test:
1. **Response Time**: Sync tools < 30s, Submit API < 5s for submission
2. **Error Handling**: Clear, informative error messages
3. **Data Format**: Structured JSON responses
4. **Job Management**: Proper status tracking and log access
5. **Batch Processing**: Handles multiple inputs efficiently
6. **Edge Cases**: Graceful handling of invalid inputs