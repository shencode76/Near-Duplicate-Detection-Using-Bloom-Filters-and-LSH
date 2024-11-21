from lsh_case2 import read_tsv_no_headers, remove_exact_duplicates
import matplotlib.pyplot as plt
from lsh import lsh_banding
from utils import generate_shingles, generate_minhash_signature, jaccard_similarity
from itertools import combinations
def plot_document_count_vs_exact_matches():
    """
    Reads TSV files, removes exact duplicates, and plots Document Count vs. Exact Matches.
    """
    file_paths = {
        'data/five.tsv': 5,
        'data/hundred.tsv': 100,
        'data/hundredk.tsv': 100000,
        'data/onek.tsv': 1000,
        'data/tenk.tsv': 10000,
        'data/thirty.tsv': 30,
        'data/thirtyk.tsv': 30000,
        'data/threehundred.tsv': 300,
        'data/threek.tsv': 3000
    }


    document_counts = []
    exact_matches_counts = []

    for file_name, doc_count in sorted(file_paths.items(), key=lambda x: x[1]):
        documents = read_tsv_no_headers(file_name)
        document_counts.append(doc_count)

        _, duplicates = remove_exact_duplicates(documents)
        exact_matches_counts.append(len(duplicates))

    plt.figure(figsize=(10, 6))
    plt.plot(document_counts, exact_matches_counts, marker='o', linestyle='-', color='b')
    plt.xlabel('Document Count')
    plt.ylabel('Exact Matches')
    plt.title('Document Count vs. Exact Matches')
    plt.xscale('log')  # Use logarithmic scale for better visualization if counts vary greatly
    plt.grid(True)
    plt.savefig("data/result/exact.png")
    plt.show()

def generate_ground_truth(unique_docs, threshold=0.7):
    """
    Generates ground truth for approximate duplicates based on Jaccard similarity.

    :param unique_docs: List of unique document dictionaries with 'id' and 'text'.
    :param threshold: Jaccard similarity threshold to consider as approximate duplicate.
    :return: Set of tuples representing pairs of document IDs that are approximate duplicates.
    """
    ground_truth = set()

    # Convert each document's text into shingles
    doc_shingles = {doc['id']: generate_shingles(doc['text']) for doc in unique_docs}

    # Compare each unique pair of documents
    for (doc1_id, shingles1), (doc2_id, shingles2) in combinations(doc_shingles.items(), 2):
        # Calculate Jaccard similarity
        similarity = jaccard_similarity(shingles1, shingles2)
        
        # If similarity is above threshold, consider them approximate duplicates
        if similarity >= threshold:
            ground_truth.add((doc1_id, doc2_id))

    return ground_truth

def evaluate_candidates(candidates, ground_truth):
    """Evaluates the precision, recall, and F1-score of candidate pairs."""
    formatted_candidates = {tuple(sorted(map(int, pair))) for pair in candidates}
    formatted_ground_truth = {tuple(sorted(map(int, pair))) for pair in ground_truth}
    # print('Candidates:')
    # print(formatted_candidates)
    # print('\nground truth:')
    # print(formatted_ground_truth)
    tp = len(formatted_candidates.intersection(formatted_ground_truth))
    fp = len(formatted_candidates - formatted_ground_truth)
    fn = len(formatted_ground_truth - formatted_candidates)

    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    return precision, recall, f1_score

# Function for tuning configurations
def tune_lsh_configuration(signatures, ground_truth, fixed_rows_per_band=10):
    num_bands_list = [5, 10, 15, 20, 25, 30]  
    results = []

    for num_bands in num_bands_list:
        candidates = lsh_banding(signatures, num_bands, fixed_rows_per_band)
        print(f"Generated {len(candidates)} candidate pairs")
        precision, recall, f1_score = evaluate_candidates(candidates, ground_truth)
        print(f"Configuration (Bands={num_bands}, Rows={fixed_rows_per_band}) has F1 Score: {f1_score}")
        
        results.append({
            'num_bands': num_bands,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        })
    
    return results


def tune_lsh_rows(signatures, ground_truth, num_bands=10):
    rows_list = [i for i in range(3,10)] 
    results = []

    for num_rows in rows_list:
        candidates = lsh_banding(signatures, num_bands, num_rows)
        print(f"Generated {len(candidates)} candidate pairs")
        precision, recall, f1_score = evaluate_candidates(candidates, ground_truth)
        print(f"Configuration (Bands={num_bands}, Rows={num_rows}) has F1 Score: {f1_score}")
        
        results.append({
            'num_rows': num_rows,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        })
    
    return results

def plot_num_bands(results):
    bands = [r['num_bands'] for r in results]
    precisions = [r['precision'] for r in results]
    recalls = [r['recall'] for r in results]
    f1_scores = [r['f1_score'] for r in results]

    plt.figure(figsize=(10, 6))
    plt.plot(bands, recalls, label='Recall')
    plt.plot(bands, precisions, label='Precision')
    plt.plot(bands, f1_scores, label='F1 Score')
    plt.xlabel('Number of Bands')
    plt.ylabel('Score')
    plt.title('Precision, Recall, and F1 Score vs Number of Bands')
    plt.legend()
    plt.savefig("data/result/f1_score_vs_bands.png")
    #plt.show()


def plot_num_rows(results):
    rows = [r['num_rows'] for r in results]
    precisions = [r['precision'] for r in results]
    recalls = [r['recall'] for r in results]
    f1_scores = [r['f1_score'] for r in results]

    plt.figure(figsize=(10, 6))
    plt.plot(rows, recalls, label='Recall')
    plt.plot(rows, precisions, label='Precision')
    plt.plot(rows, f1_scores, label='F1 Score')
    plt.xlabel('Number of Rows per Band')
    plt.ylabel('Score')
    plt.title('Precision, Recall, and F1 Score vs Number of Rows per Band')
    plt.legend()
    plt.savefig("data/result/f1_score_vs_rows.png")
    #plt.show()

import numpy as np

def generate_empirical_s_curve(signatures, b_values, r_values):
    jaccard_values = np.linspace(0, 1, 100)
    results = []

    for b, r in zip(b_values, r_values):
        candidates = lsh_banding(signatures, b, r)
        
        detection_rates = []
        for threshold in jaccard_values:
            similar_pairs = set()
            for (idx1, sig1), (idx2, sig2) in combinations(enumerate(signatures), 2):
                if jaccard_similarity(sig1, sig2) >= threshold:
                    similar_pairs.add((idx1, idx2))
            
            detected_pairs = similar_pairs.intersection(candidates)
            detection_rate = len(detected_pairs) / len(similar_pairs) if similar_pairs else 0
            detection_rates.append(detection_rate)
        
        results.append((b, r, jaccard_values, detection_rates))

    return results

def plot_empirical_s_curve(results):
    plt.figure(figsize=(10, 6))
    for b, r, jaccard_values, detection_rates in results:
        plt.plot(jaccard_values, detection_rates, label=f'b={b}, r={r}')
    plt.xlabel('Jaccard Similarity')
    plt.ylabel('Detection Rate')
    plt.title('Empirical S-Curve for Different b and r Values')
    plt.legend()
    plt.savefig("data/result/empirical_s_curve.png")
    # plt.show()


def eda2():
    # Load and preprocess data
    file_path = 'data/threehundred.tsv' 
    documents = read_tsv_no_headers(file_path)
    unique_docs, duplicates = remove_exact_duplicates(documents)
    ground_truth = generate_ground_truth(unique_docs, threshold=0.8)
    #print(ground_truth)

    # Generate MinHash signatures
    num_hashes = 100
    signatures = [generate_minhash_signature(doc['text'], num_hashes) for doc in unique_docs]

    # Tune configurations and plot results
    results = tune_lsh_configuration(signatures, ground_truth)
    plot_num_bands(results)
    res = tune_lsh_rows(signatures, ground_truth)
    plot_num_rows(res)

    b_values = [5, 10, 20]  
    r_values = [5, 10, 15]  

    re_curve= generate_empirical_s_curve(signatures, b_values, r_values)
    plot_empirical_s_curve(re_curve)


if __name__ == "__main__":
    #plot_document_count_vs_exact_matches()
    # Output: 
    # Processed 4 unique documents and found 1 duplicates.
    # Processed 29 unique documents and found 1 duplicates.
    # Processed 82 unique documents and found 18 duplicates.
    # Processed 273 unique documents and found 16 duplicates.
    # Processed 909 unique documents and found 87 duplicates.
    # Processed 2686 unique documents and found 312 duplicates.
    # Processed 8936 unique documents and found 1059 duplicates.
    # Processed 26716 unique documents and found 3278 duplicates.
    # Processed 89249 unique documents and found 10736 duplicates.


    eda2()

    # png file saved in data/result/...png 
    # Output for bands
    # Generated 938 candidate pairs
    # Configuration (Bands=5, Rows=10) has F1 Score: 0
    # Generated 1544 candidate pairs
    # Configuration (Bands=10, Rows=10) has F1 Score: 0.0012468827930174563
    # Generated 1632 candidate pairs
    # Configuration (Bands=15, Rows=10) has F1 Score: 0.0011820330969267137
    # Generated 1632 candidate pairs
    # Configuration (Bands=20, Rows=10) has F1 Score: 0.0011820330969267137
    # Generated 1632 candidate pairs
    # Configuration (Bands=25, Rows=10) has F1 Score: 0.0011820330969267137
    # Generated 1632 candidate pairs
    # Configuration (Bands=30, Rows=10) has F1 Score: 0.0011820330969267137


    # Output for rows per band 
    # Generated 1199 candidate pairs
    # Configuration (Bands=10, Rows=3) has F1 Score: 0
    # Generated 1259 candidate pairs
    # Configuration (Bands=10, Rows=4) has F1 Score: 0.001516300227445034
    # Generated 1345 candidate pairs
    # Configuration (Bands=10, Rows=5) has F1 Score: 0.0014234875444839856
    # Generated 1390 candidate pairs
    # Configuration (Bands=10, Rows=6) has F1 Score: 0
    # Generated 1507 candidate pairs
    # Configuration (Bands=10, Rows=7) has F1 Score: 0
    # Generated 1581 candidate pairs
    # Configuration (Bands=10, Rows=8) has F1 Score: 0.001218769043266301
    # Generated 1580 candidate pairs
    # Configuration (Bands=10, Rows=9) has F1 Score: 0.0012195121951219512

