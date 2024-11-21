# bloomfilter3_cli.py

from .bloomfilter3 import StandardBloomFilter, ChunkedBloomFilter, ImprovedBloomFilter
import logging
import sys
import argparse
from bitarray import bitarray
import hashlib
import math

logging.basicConfig(level=logging.INFO)

def calculate_bloom_filter_size(n, f):
    import math
    if f >= 1 or f <= 0:
        logging.error("False positive rate must be between 0 and 1.")
        return None, None
    m = math.ceil((n * math.log(1/f)) / (math.log(2)**2))
    k = math.ceil((m / n) * math.log(2))
    return max(1, m), max(1, k)

def main():
    parser = argparse.ArgumentParser(description="Bloom Filter CLI")
    parser.add_argument("--init", action="store_true", help="Initialize the Bloom Filter")
    parser.add_argument("--type", type=str, choices=['standard', 'chunked', 'improved'], default='standard', help="Type of Bloom Filter to initialize")
    parser.add_argument("--n", type=int, help="Number of elements (required for init)")
    parser.add_argument("--f", type=float, help="False positive rate (required for init)")
    parser.add_argument("--chunks", type=int, help="Number of chunks (required for chunked Bloom Filter)")
    parser.add_argument("--method", type=str, choices=['standard', 'kirsch-mitzenmacher'], default='standard', help="Hashing method to use for improved Bloom Filter")
    parser.add_argument("--insert-file", type=str, help="Path to the file to be inserted")
    parser.add_argument("--query-file", type=str, help="Path to the file to query")

    args = parser.parse_args()

    if not args.init:
        logging.error("Initialization flag (--init) must be set to initialize Bloom Filter.")
        return

    if args.type == 'improved' and (args.n is None or args.f is None):
        logging.error("Please provide --n and --f for initialization of improved Bloom Filter.")
        return

    if args.type == 'chunked' and (args.n is None or args.f is None or args.chunks is None):
        logging.error("Please provide --n, --f, and --chunks for initialization of chunked Bloom Filter.")
        return

    if args.n is None or args.f is None:
        logging.error("Please provide --n and --f for initialization.")
        return

    m, k = calculate_bloom_filter_size(args.n, args.f)
    if args.type == 'standard':
        bloom_filter = StandardBloomFilter(m, k)
    elif args.type == 'chunked':
        bloom_filter = ChunkedBloomFilter(m, k, args.chunks)
    elif args.type == 'improved':
        bloom_filter = ImprovedBloomFilter(m, k, args.method)
    
    logging.info(f"{args.type.capitalize()} bloom filter initialized with size = {m}, number of hash functions = {k}, additional parameters = {args.chunks if args.type == 'chunked' else args.method if args.type == 'improved' else 'None'}")

    # Insert Items from the specified file
    if args.insert_file:
        try:
            with open(args.insert_file, 'r') as f:
                content = f.read().strip().splitlines()
                for line in content:
                    document = line.strip()
                    bloom_filter.add(document)  # Add document to Bloom filter
            logging.info(f"Inserted items from file: {args.insert_file}")
        except FileNotFoundError:
            logging.error(f"Error: The file {args.insert_file} does not exist.")
            return

    # Query Items from the specified file
    if args.query_file:
        try:
            result = 0
            with open(args.query_file, 'r') as f:
                content = f.read().strip().splitlines()
                for line in content:
                    document = line.strip()
                    if bloom_filter.check(document):
                        result += 1
            logging.info(f"There are {result} items in {args.query_file} possibly in the filter.")
        except FileNotFoundError:
            logging.error(f"Error: The file {args.query_file} does not exist.")
            return

if __name__ == "__main__":
    main()