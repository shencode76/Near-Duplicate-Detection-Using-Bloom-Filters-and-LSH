import csv
import re
import hashlib
import time
import tracemalloc
import logging


def read_tsv(file_path: str):
    """
    Reads a TSV file and returns a list of rows as dictionaries.
    :param file_path: Path to the TSV file.
    :return: List of rows as dictionaries.
    """
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            data.append(row)
    return data

def write_tsv(file_path: str, data, fieldnames):
    """
    Writes data to a TSV file.
    :param file_path: Path to the TSV file.
    :param data: List of dictionaries to write.
    :param fieldnames: List of fieldnames for the TSV file.
    """
    with open(file_path, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, delimiter='\t', fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def clean_and_normalize(text: str) -> str:
    """
    Cleans and normalizes document text.
    :param text: Raw document text.
    :return: Cleaned and normalized text.
    """
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    return text.strip()

# shingles
def generate_shingles(document, k=3):
    words = clean_and_normalize(document).split()
    shingles = [tuple(words[i:i + k]) for i in range(len(words) - k + 1)]
    return shingles

from nltk.util import ngrams  # If you use the nltk library for n-grams

def create_ngrams(text, n):
    words = text.split()
    return [' '.join(ngram) for ngram in ngrams(words, n)]

def hash_shingle(shingle, seed):
    h = hashlib.md5(str(shingle).encode('utf-8') + str(seed).encode('utf-8'))
    return int(h.hexdigest(), 16)

def generate_minhash_signature(shingles, num_hashes=100):
    signature = []
    for i in range(num_hashes):
        min_hash = min([hash_shingle(shingle, i) for shingle in shingles])
        signature.append(min_hash)
    return signature

def minhash_signature(text: str, num_permutations: int) -> list:
    """
    Generate a minhash signature for the given text.
    :param text: The document text.
    :param num_permutations: Number of hash functions to simulate (i.e., number of permutations).
    :return: A list of integers representing the minhash signature.
    """
    # Split the text into shingles (e.g., words)
    shingles = text.split()  # You may want to use n-grams instead of words
    
    # Initialize the signature with a very large number
    signature = [float('inf')] * num_permutations
    
    for shingle in shingles:
        for i in range(num_permutations):
            # Generate hash using the shingle and the i-th permutation (seed)
            hashed_value = hash_function(shingle, i)
            # Keep the minimum hash value for this permutation
            signature[i] = min(signature[i], hashed_value)
    
    return signature

def hash_function(value: str, seed: int) -> int:
    """
    Hashes a value using MD5, incorporating a seed, and returns an integer.
    :param value: String to hash.
    :param seed: Seed value to introduce variations in the hash.
    :return: Hashed integer.
    """
    # Combine the value and seed to produce a variation
    combined_value = f"{value}_{seed}"
    return int(hashlib.md5(combined_value.encode()).hexdigest(), 16)


def jaccard_similarity(set1: set, set2: set) -> float:
    """
    Computes the Jaccard similarity between two sets.
    :param set1: First set.
    :param set2: Second set.
    :return: Jaccard similarity as a float.
    """
    set1, set2 = set(set1), set(set2)
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0.0


def track_memory_and_time(func):
    """
    Decorator to track the memory usage and execution time of a function.
    """
    def wrapper(*args, **kwargs):
        logging.info(f"Starting '{func.__name__}' with memory and time tracking.")
        
        # Start tracking memory and time
        tracemalloc.start()
        start_time = time.time()
        
        # Execute the function
        result = func(*args, **kwargs)
        
        # Stop tracking memory and time
        current, peak = tracemalloc.get_traced_memory()
        end_time = time.time()
        tracemalloc.stop()
        
        # Calculate time and memory usage
        elapsed_time = end_time - start_time
        peak_memory = peak / (1024 * 1024)  # Convert to MB
        
        logging.info(f"'{func.__name__}' took {elapsed_time:.2f} seconds and used {peak_memory:.2f} MB of memory.")
        
        return result

    return wrapper

import hashlib
import numpy as np

def lsh_hash(signature, bands, rows):
    """
    Applies LSH using the banding technique.
    :param signature: Minhash signature.
    :param bands: Number of bands.
    :param rows: Number of rows per band.
    :return: List of LSH hashes.
    """
    band_hashes = []
    for i in range(bands):
        band = tuple(signature[i*rows:(i+1)*rows])
        band_hash = hash_function(str(band), i)  # Pass the band index as the seed
        band_hashes.append(band_hash)
    return band_hashes


def hash_function(value: str) -> int:
    """
    Hashes a value using MD5 and returns an integer.
    :param value: String to hash.
    :return: Hashed integer.
    """
    return int(hashlib.md5(value.encode()).hexdigest(), 16)


# LSH banding 
def lsh_banding(signatures, num_bands, rows_per_band):
    band_buckets = {}
    candidates = set()

    for doc_id, signature in enumerate(signatures):
        for band in range(num_bands):
            band_signature = tuple(signature[band * rows_per_band:(band + 1) * rows_per_band])
            # print(f"Document {doc_id}, Band {band}, Band Signature: {band_signature}")

            if band_signature in band_buckets:
                candidates.add((band_buckets[band_signature], doc_id))
            else:
                band_buckets[band_signature] = doc_id

    return candidates

def find_candidate_pairs(band_hashes):
    """
    Finds candidate document pairs based on LSH hash buckets.
    :param band_hashes: List of LSH hashes for documents.
    :return: Set of candidate document pairs.
    """
    buckets = {}
    candidate_pairs = set()
    
    for doc_id, hash_list in enumerate(band_hashes):
        for band_id, band_hash in enumerate(hash_list):
            if (band_id, band_hash) not in buckets:
                buckets[(band_id, band_hash)] = []
            for candidate_doc_id in buckets[(band_id, band_hash)]:
                candidate_pairs.add((min(doc_id, candidate_doc_id), max(doc_id, candidate_doc_id)))
            buckets[(band_id, band_hash)].append(doc_id)
    
    return candidate_pairs

# combine lsh and union find
# def lsh_with_union_find(documents, num_hashes=100, num_bands=20, rows_per_band=5):
#     all_signatures = []
#     for doc in documents:
#         shingles = generate_shingles(doc)
#         signature = minhash_signature(shingles, num_hashes)
#         all_signatures.append(signature)

#     candidates = lsh_banding(all_signatures, num_bands, rows_per_band)

#     num_docs = len(documents)
#     uf = UnionFind(num_docs)

#     for doc1, doc2 in candidates:
#         uf.union(doc1, doc2)

#     clusters = {}
#     for doc_id in range(num_docs):
#         root = uf.find(doc_id)
#         if root not in clusters:
#             clusters[root] = []
#         clusters[root].append(doc_id)

#     return list(clusters.values())

# Union-Find, not using networkx
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, p):
        if self.parent[p] != p:
            self.parent[p] = self.find(self.parent[p])
        return self.parent[p]

    def union(self, p, q):
        rootP = self.find(p)
        rootQ = self.find(q)
        if rootP != rootQ:
            if self.rank[rootP] > self.rank[rootQ]:
                self.parent[rootQ] = rootP
            elif self.rank[rootP] < self.rank[rootQ]:
                self.parent[rootP] = rootQ
            else:
                self.parent[rootQ] = rootP
                self.rank[rootP] += 1

def find_candidate_pairs_multi_probe(band_hashes, num_probes=2):
    """
    Finds candidate document pairs using Multi-Probe LSH.
    :param band_hashes: List of LSH hashes for documents.
    :param num_probes: Number of nearby buckets to probe for potential candidates.
    :return: Set of candidate document pairs.
    """
    buckets = {}
    candidate_pairs = set()
    
    for doc_id, hash_list in enumerate(band_hashes):
        for band_id, band_hash in enumerate(hash_list):
            # Main bucket
            if (band_id, band_hash) not in buckets:
                buckets[(band_id, band_hash)] = []
            for candidate_doc_id in buckets[(band_id, band_hash)]:
                candidate_pairs.add((min(doc_id, candidate_doc_id), max(doc_id, candidate_doc_id)))
            buckets[(band_id, band_hash)].append(doc_id)
            
            # Probe nearby buckets
            for probe in range(1, num_probes + 1):
                nearby_hash = band_hash + probe
                if (band_id, nearby_hash) in buckets:
                    for candidate_doc_id in buckets[(band_id, nearby_hash)]:
                        candidate_pairs.add((min(doc_id, candidate_doc_id), max(doc_id, candidate_doc_id)))
    
    return candidate_pairs

import hashlib

def hash_function(value: str, seed: int) -> int:
    """
    Hashes a value using MD5, incorporating a seed, and returns an integer.
    :param value: String to hash.
    :param seed: Seed value to introduce variations in the hash.
    :return: Hashed integer.
    """
    # Combine the value and seed to produce a variation
    combined_value = f"{value}_{seed}"
    return int(hashlib.md5(combined_value.encode()).hexdigest(), 16)


def get_dynamic_shingle_size(text: str, min_k=3, max_k=5) -> int:
    """
    Dynamically adjusts shingle size (k) based on the length of the text.
    :param text: The document text.
    :param min_k: Minimum shingle size.
    :param max_k: Maximum shingle size.
    :return: The appropriate shingle size for the given document.
    """
    text_length = len(text.split())
    if text_length < 10:
        return min_k
    elif text_length < 100:
        return min_k + 1
    else:
        return max_k

def minhash_signature_dynamic(text: str, num_permutations: int) -> list:
    """
    Generate a minhash signature for the given text using a dynamic shingle size.
    :param text: The document text.
    :param num_permutations: Number of hash functions to simulate (i.e., number of permutations).
    :return: A list of integers representing the minhash signature.
    """
    k = get_dynamic_shingle_size(text)  # Get dynamic shingle size based on document length
    shingles = [text[i:i+k] for i in range(len(text) - k + 1)]  # Create k-shingles
    signature = [float('inf')] * num_permutations
    
    for shingle in shingles:
        for i in range(num_permutations):
            hashed_value = hash_function(shingle, i)
            signature[i] = min(signature[i], hashed_value)
    
    return signature

def evaluate_candidates(candidates, ground_truth):
    tp = len(candidates.intersection(ground_truth))
    fp = len(candidates - ground_truth)
    fn = len(ground_truth - candidates)
    
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0
    
    return precision, recall, f1_score


def tune_parameters(min_band, max_band, step_band, min_row, max_row, step_row, signatures):
    best_parameters = None
    best_score = 0
    for num_bands in range(min_band, max_band, step_band):
        for rows_per_band in range(min_row, max_row, step_row):
            candidates = lsh_banding(signatures, num_bands, rows_per_band)
            score = evaluate_candidates(candidates) 
            if score > best_score:
                best_score = score
                best_parameters = (num_bands, rows_per_band)
    return best_parameters


import matplotlib.pyplot as plt

def plot_evaluation_results(results):
    bands = [r['num_bands'] for r in results]
    recalls = [r['recall'] for r in results]
    precisions = [r['precision'] for r in results]
    
    plt.plot(bands, recalls, label="Recall")
    plt.plot(bands, precisions, label="Precision")
    plt.xlabel("Number of Bands")
    plt.ylabel("Score")
    plt.legend()
    plt.show()

