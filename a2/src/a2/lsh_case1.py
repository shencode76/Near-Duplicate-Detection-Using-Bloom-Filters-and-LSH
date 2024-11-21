import sys
import csv
import logging
from .dedup import write_tsv, clean_and_normalize, minhash_signature, jaccard_similarity, track_memory_and_time
from .dedup import lsh_hash, find_candidate_pairs, UnionFind

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_tsv_no_headers(file_path: str):
    """
    Reads a TSV file without headers and assigns the first column as 'id' and the second as 'text'.
    Logs the total number of rows processed and any malformed rows encountered.
    
    :param file_path: Path to the TSV file.
    :return: List of dictionaries with keys 'id' and 'text'.
    """
    data = []
    total_rows = 0  # Track the number of rows encountered
    malformed_rows = 0  # Track malformed or empty rows

    with open(file_path, mode='r', encoding='utf-8') as file:
        for line in file:
            total_rows += 1
            row = line.strip().split('\t')  # Split and strip whitespace

            if len(row) == 2 and all(row):
                data.append({'id': row[0].strip(), 'text': row[1].strip()})
            elif len(row) == 1 and row[0]:  # Single entry, treat as ID-only
                data.append({'id': str(len(data) + 1), 'text': row[0].strip()})
            else:
                malformed_rows += 1  # Count malformed or empty rows
    
    logging.info(f"Processed {total_rows} rows; read {len(data)} documents with {malformed_rows} malformed or empty rows skipped.")
    return data

def remove_exact_duplicates(documents):
    """
    Removes exact duplicate documents from the collection based on document text content.

    :param documents: List of documents, each represented as a dictionary with 'id' and 'text' keys.
    :return: Tuple containing a list of unique documents and a list of duplicates.
    """
    unique_docs = {}
    duplicates = []

    for doc in documents:
        if doc['text'] not in unique_docs:
            unique_docs[doc['text']] = doc
        else:
            duplicates.append(doc)

    logging.info(f"Processed {len(unique_docs)} unique documents and found {len(duplicates)} duplicates.")
    return list(unique_docs.values()), duplicates

def compute_jaccard_similarity(cluster):
    """
    Compute the Jaccard similarity for all pairs of documents in a given cluster.

    :param cluster: List of documents in a cluster, each represented as a dictionary.
    :return: List of tuples containing the document IDs and their Jaccard similarity score.
    """
    similarities = []
    for i in range(len(cluster)):
        for j in range(i + 1, len(cluster)):
            doc1_shingles = set(cluster[i]['text'].split())
            doc2_shingles = set(cluster[j]['text'].split())
            similarity = jaccard_similarity(doc1_shingles, doc2_shingles)
            similarities.append((cluster[i]['id'], cluster[j]['id'], similarity))
    return similarities

@track_memory_and_time
def deduplicate_collection(file_path, output_path, num_permutations=100, bands=20):
    """
    Main function to deduplicate a collection of documents using basic LSH and clustering.
    Saves deduplicated clusters and exact duplicates in a `.txt` format.
    """
    logging.info("Starting deduplication process...")

    # Step 1: Read documents
    documents = read_tsv_no_headers(file_path)

    # Step 2: Remove exact duplicates
    unique_docs, removed_duplicates = remove_exact_duplicates(documents)
    logging.info(f"Removed {len(removed_duplicates)} exact duplicates.")

    # Step 3: Clean and normalize document text
    for doc in unique_docs:
        doc['text'] = clean_and_normalize(doc['text'])

    # Step 4: Compute Minhash signatures
    logging.info("Computing Minhash signatures...")
    for doc in unique_docs:
        doc['minhash'] = minhash_signature(doc['text'], num_permutations)

    # Step 5: LSH to find candidate pairs
    signatures = [doc['minhash'] for doc in unique_docs]
    rows = num_permutations // bands
    lsh_hashes = [lsh_hash(signature, bands, rows) for signature in signatures]
    candidate_pairs = find_candidate_pairs(lsh_hashes)
    logging.info(f"Found {len(candidate_pairs)} candidate pairs.")

    # Step 6: Cluster documents using Union-Find
    uf = UnionFind(len(unique_docs))
    for doc1, doc2 in candidate_pairs:
        uf.union(doc1, doc2)

    clusters = {}
    for idx, doc in enumerate(unique_docs):
        root = uf.find(idx)
        if root not in clusters:
            clusters[root] = []
        clusters[root].append(doc['id'])

    logging.info(f"Formed {len(clusters)} clusters after deduplication.")

    for root, cluster in clusters.items():
        # Convert each item in cluster to a document ID if cluster items are just strings (IDs)
        if isinstance(cluster[0], str):  # Check if cluster contains only document IDs
            logging.info(f"Cluster {root} contains document IDs: " + ", ".join(cluster))
            # Retrieve full document objects for similarity calculation based on IDs
            cluster_docs = [doc for doc in unique_docs if doc['id'] in cluster]
        else:
            logging.info(f"Cluster {root} contains document IDs: " + ", ".join(doc['id'] for doc in cluster))
            cluster_docs = cluster  # Cluster already contains full document objects
        
        # Compute Jaccard similarity if there are multiple documents in the cluster
        similarities = compute_jaccard_similarity(cluster_docs)
        if similarities:
            for doc1_id, doc2_id, similarity in similarities:
                logging.info(f"Jaccard similarity between {doc1_id} and {doc2_id}: {similarity:.3f}")
        else:
            logging.info("No similarities to compute (only one document in cluster).")


    # Step 7: Save deduplicated document IDs in the `.txt` format
    with open(output_path, 'w') as file:
        for cluster_ids in clusters.values():
            file.write(" ".join(cluster_ids) + "\n")

        if removed_duplicates:
            for dup in removed_duplicates:
                file.write(dup['id'] + "\n")
    
    logging.info(f"Saved deduplicated clusters and exact duplicates to {output_path} in the required format.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.error("Usage: python lsh_case1.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    deduplicate_collection(input_file, output_file)

# export PYTHONPATH=$PYTHONPATH:$(pwd)
# python src/a2/lsh_case1.py data/five.tsv data/sample_result.txt
# direct to a2 to run this. Be mindful that the there is printed output and output saved within data/result.tsv

#300 rows
#'deduplicate_collection' took 49.08 seconds and used 3.67 MB of memory.

#1000
#'deduplicate_collection' took 177.80 seconds and used 12.24 MB of memory.

#10000
#'deduplicate_collection' took 1666.23 seconds and used 120.65 MB of memory.

#100000
#'deduplicate_collection' took 18063.46 seconds and used 1330.74 MB of memory.