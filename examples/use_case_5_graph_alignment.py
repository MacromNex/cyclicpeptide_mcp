#!/usr/bin/env python3
"""
Use Case 5: Graph Alignment with GCN Model

This script performs graph-based similarity analysis using Graph Convolutional Networks (GCN)
to compare cyclic peptide sequences based on their graph representations.
"""

import argparse
import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import cyclicpeptide
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import torch
    import torch.nn.functional as F
    from torch_geometric.nn import GCNConv, global_mean_pool
    from torch_geometric.data import Data, Batch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch and PyTorch Geometric not available. Graph alignment functionality will be limited.")

from cyclicpeptide import GraphAlignment as ga, IOManager

# GCN Model Classes (from the GCN notebook)
if TORCH_AVAILABLE:
    class GCNEmbedding(torch.nn.Module):
        def __init__(self, input_dim, hidden_dim, output_dim):
            super(GCNEmbedding, self).__init__()
            self.conv1 = GCNConv(input_dim, hidden_dim)
            self.conv2 = GCNConv(hidden_dim, output_dim)

        def forward(self, x, edge_index, batch):
            x = F.relu(self.conv1(x, edge_index))
            x = self.conv2(x, edge_index)
            x = global_mean_pool(x, batch)
            return x

    class GraphSimilarityModel(torch.nn.Module):
        def __init__(self, node_feature_dim=29, hidden_dim=64, embedding_dim=32):
            super(GraphSimilarityModel, self).__init__()
            self.gcn = GCNEmbedding(node_feature_dim, hidden_dim, embedding_dim)
            self.fc = torch.nn.Sequential(
                torch.nn.Linear(3 * embedding_dim, hidden_dim),
                torch.nn.ReLU(),
                torch.nn.Linear(hidden_dim, 1),
                torch.nn.Sigmoid()
            )

        def forward(self, data1, data2):
            embedding1 = self.gcn(data1.x, data1.edge_index, data1.batch)
            embedding2 = self.gcn(data2.x, data2.edge_index, data2.batch)
            combined = torch.cat([embedding1, embedding2, torch.abs(embedding1 - embedding2)], dim=1)
            similarity = self.fc(combined)
            return similarity.squeeze()

# Helper functions
def sequence_to_node_edge(sequence):
    """Convert amino acid sequence to graph nodes and edges."""
    import re

    amino_acids = sequence.split('--')
    nodes = []  # Node information: [(0, 'Cys'), (1, 'Cys'), ...]
    edges = []  # Edge information: [(0, 1), (1, 2), ...]
    special_connections = {}

    for i, amino_acid in enumerate(amino_acids):
        # Extract amino acid name and special connection information
        amino_acid_name = re.sub(r"\(\d+\)", "", amino_acid)

        if '-' in amino_acid_name:
            items = [k.strip() for k in amino_acid_name.split('-')]
            for j in range(len(items) - 1):
                nodes.append((str(i) + '_' + str(j), items[j].strip().upper()))
                edges.append((str(i) + '_' + str(j), i))
            amino_acid_name = items[-1]

        nodes.append((i, amino_acid_name.strip().capitalize()))

        # Regular connections
        if i > 0:
            edges.append((i - 1, i))

        # Special connections
        special_conn_ids = re.findall(r"\((\d+)\)", amino_acid)
        for conn_id in special_conn_ids:
            conn_id = int(conn_id) - 1  # Convert to 0-indexed
            if conn_id in special_connections:
                edges.append((special_connections[conn_id], i))
            else:
                special_connections[conn_id] = i

    return nodes, edges

def node2embedding(node):
    """Convert node to feature vector."""
    node_labels = ["Ala", "Arg", "Asn", "Asp", "Cys", "Gln", "Glu", "Gly", "His", "Ile", "Leu", "Lys",
                   "Met", "Phe", "Pro", "Ser", "Thr", "Trp", "Tyr", "Val", "Orn", "Aile", "DL", "D", "Dap", "Athr",
                   "4OH", "OH"]
    if node in node_labels:
        return [1 if i == node else 0 for i in node_labels] + [0]
    else:
        return [0 for i in node_labels] + [1]

def graph2data(nodes, edges):
    """Convert graph nodes and edges to PyTorch Geometric Data."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch and PyTorch Geometric required for graph data conversion")

    # Node index mapping
    node_index_map = {node[0]: i for i, node in enumerate(nodes)}
    x = torch.tensor([node2embedding(node[1]) for node in nodes], dtype=torch.float)

    # Convert edges to indices
    edge_index = torch.tensor([[node_index_map[edge[0]], node_index_map[edge[1]]] for edge in edges],
                             dtype=torch.long).t().contiguous()

    # Create PyTorch Geometric data
    data = Data(x=x, edge_index=edge_index)
    return data

def load_ga_gcn(model_path):
    """Load pre-trained GCN model."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch required for loading GCN model")

    model = GraphSimilarityModel(node_feature_dim=29)
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=False))
    model.eval()
    return model

def ga_prediction(model, seq1, seq2):
    """Predict graph alignment similarity between two sequences."""
    if not TORCH_AVAILABLE:
        raise ImportError("PyTorch required for GCN predictions")

    nodes1, edges1 = sequence_to_node_edge(seq1)
    nodes2, edges2 = sequence_to_node_edge(seq2)
    data1, data2 = graph2data(nodes1, edges1), graph2data(nodes2, edges2)

    with torch.no_grad():
        similarity = model(data1, data2)

    return similarity.detach().numpy()

def analyze_graph_alignment(sequences, model_path, output_dir="output", query_sequence=None):
    """
    Analyze graph alignment between sequences.

    Args:
        sequences (list): List of amino acid sequences
        model_path (str): Path to pre-trained GCN model
        output_dir (str): Directory to save outputs
        query_sequence (str): Optional query sequence to compare against all others

    Returns:
        dict: Results of the alignment analysis
    """
    print(f"Analyzing graph alignment for {len(sequences)} sequences")
    print(f"Model path: {model_path}")

    if not TORCH_AVAILABLE:
        print("Error: PyTorch and PyTorch Geometric are required for graph alignment")
        return None

    try:
        # Check if model file exists
        if not os.path.exists(model_path):
            # Try to find it in the examples/data directory
            alt_path = os.path.join("examples", "data", os.path.basename(model_path))
            if os.path.exists(alt_path):
                model_path = alt_path
            else:
                print(f"Error: Model file not found at {model_path}")
                print("Please provide the path to GA_GCN.pth model file")
                return None

        # Load model
        model = load_ga_gcn(model_path)
        print("Model loaded successfully")

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        if query_sequence:
            # Compare query against all sequences
            print(f"Comparing query sequence '{query_sequence}' against {len(sequences)} reference sequences")

            similarities = []
            for i, ref_seq in enumerate(sequences):
                try:
                    similarity = ga_prediction(model, query_sequence, ref_seq)
                    similarities.append(float(similarity))
                    print(f"  {i+1}/{len(sequences)}: {similarity:.6f}")
                except Exception as e:
                    print(f"  Error processing sequence {i+1}: {e}")
                    similarities.append(0.0)

            # Save results
            results_df = pd.DataFrame({
                'Reference_Sequence': sequences,
                'Similarity': similarities
            })
            results_df = results_df.sort_values('Similarity', ascending=False)

            output_file = os.path.join(output_dir, "graph_alignment_results.csv")
            results_df.to_csv(output_file, index=False)
            print(f"Results saved to: {output_file}")

            # Print top matches
            print(f"\nTop 5 similar sequences to query '{query_sequence}':")
            for i, row in results_df.head().iterrows():
                print(f"  {row['Similarity']:.6f}: {row['Reference_Sequence']}")

            return {
                'query_sequence': query_sequence,
                'similarities': similarities,
                'results_df': results_df
            }

        else:
            # All-vs-all comparison
            print("Performing all-vs-all sequence comparison")

            similarity_matrix = np.zeros((len(sequences), len(sequences)))

            for i in range(len(sequences)):
                for j in range(len(sequences)):
                    if i <= j:  # Only calculate upper triangle (symmetric matrix)
                        try:
                            similarity = ga_prediction(model, sequences[i], sequences[j])
                            similarity_matrix[i, j] = float(similarity)
                            similarity_matrix[j, i] = float(similarity)
                        except Exception as e:
                            print(f"Error comparing sequences {i} and {j}: {e}")
                            similarity_matrix[i, j] = 0.0
                            similarity_matrix[j, i] = 0.0

                print(f"Processed row {i+1}/{len(sequences)}")

            # Save similarity matrix
            similarity_df = pd.DataFrame(similarity_matrix,
                                       index=[f"Seq_{i}" for i in range(len(sequences))],
                                       columns=[f"Seq_{i}" for i in range(len(sequences))])

            matrix_file = os.path.join(output_dir, "similarity_matrix.csv")
            similarity_df.to_csv(matrix_file)
            print(f"Similarity matrix saved to: {matrix_file}")

            # Save sequence mapping
            seq_mapping_df = pd.DataFrame({
                'Sequence_ID': [f"Seq_{i}" for i in range(len(sequences))],
                'Sequence': sequences
            })
            mapping_file = os.path.join(output_dir, "sequence_mapping.csv")
            seq_mapping_df.to_csv(mapping_file, index=False)
            print(f"Sequence mapping saved to: {mapping_file}")

            return {
                'similarity_matrix': similarity_matrix,
                'sequences': sequences,
                'similarity_df': similarity_df
            }

    except Exception as e:
        print(f"Error during graph alignment analysis: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Graph-based alignment analysis for cyclic peptide sequences')
    parser.add_argument('--sequences', '-s', nargs='+',
                       help='List of sequences to analyze')
    parser.add_argument('--input', '-i', type=str,
                       help='File containing sequences (one per line)')
    parser.add_argument('--query', '-q', type=str,
                       help='Query sequence to compare against all others')
    parser.add_argument('--model', '-m', type=str, default='examples/data/GA_GCN.pth',
                       help='Path to pre-trained GCN model (default: examples/data/GA_GCN.pth)')
    parser.add_argument('--output', '-o', type=str, default='output',
                       help='Output directory (default: output)')

    args = parser.parse_args()

    # Get sequences
    if args.input:
        try:
            with open(args.input, 'r') as f:
                sequences = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(sequences)} sequences from {args.input}")
        except FileNotFoundError:
            print(f"Error: File {args.input} not found")
            return 1
    elif args.sequences:
        sequences = args.sequences
        print(f"Using {len(sequences)} sequences from command line")
    else:
        # Use default example sequences
        sequences = [
            'Ala(1)--Ala--Gly--Phe--Pro--Val--Phe--Phe(1)',
            'Pro(1)--Val--Phe--Phe--Ala--Ala--Gly--Phe(1)',
            'Gly(1)--Phe--Pro--Val--Phe--Phe--Ala--Ala(1)'
        ]
        print("Using default example sequences")

    if not sequences:
        print("Error: No sequences provided")
        return 1

    # Perform analysis
    results = analyze_graph_alignment(sequences, args.model, args.output, args.query)

    if results is None:
        return 1

    print("Graph alignment analysis completed successfully!")
    return 0

if __name__ == "__main__":
    # Example usage when run directly
    if len(sys.argv) == 1:
        print("Example usage:")
        print("  python use_case_5_graph_alignment.py --query 'Ala(1)--Ala--Gly--Phe--Pro--Val--Phe--Phe(1)' --input examples/data/sequences.txt")
        print("  python use_case_5_graph_alignment.py --sequences 'Ala(1)--Ala--Gly--Phe--Pro--Val--Phe--Phe(1)' 'Pro(1)--Val--Phe--Phe--Ala--Ala--Gly--Phe(1)'")
        print()

        if not TORCH_AVAILABLE:
            print("Note: PyTorch not available. Please install PyTorch and PyTorch Geometric for full functionality.")
            print("  pip install torch torch-geometric")

        print("Running default example...")
        sys.argv = [sys.argv[0], '--query', 'Ala(1)--Ala--Gly--Phe--Pro--Val--Phe--Phe(1)']

    sys.exit(main())