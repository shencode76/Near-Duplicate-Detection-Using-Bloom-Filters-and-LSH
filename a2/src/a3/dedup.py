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

def hash_shingle(shingle, seed):
    h = hashlib.md5(str(shingle).encode('utf-8') + str(seed).encode('utf-8'))
    return int(h.hexdigest(), 16)

def generate_minhash_signature(shingles, num_hashes=100):
    signature = []
    for i in range(num_hashes):
        min_hash = min([hash_shingle(shingle, i) for shingle in shingles])
        signature.append(min_hash)
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
