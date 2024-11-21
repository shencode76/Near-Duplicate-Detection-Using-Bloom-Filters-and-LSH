# bloomfilter1_cli.py

from .bloomfilter1 import BloomFilter
import argparse
import sys
import logging
import os

logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) < 4:
        logging.error("""Usage: 
                      python -m bloomfilter1_cli.py --init --n <number_of_elements> --f <falsepositive_rate> --insert-file <insert_file_path> --query-file <query_file_path> 
                      """)
        sys.exit(1)
    parser = argparse.ArgumentParser(description="Bloom Filter CLI")
    parser.add_argument("--init", action="store_true", help="Initialize the Bloom Filter")
    parser.add_argument("--n", type=int, help="Number of elements (required for init)")
    parser.add_argument("--f", type=float, help="False positive rate (required for init)")
    parser.add_argument("--insert-file", type=str, help="Path to the file to be inserted")
    parser.add_argument("--query-file", type=str, help="Path to the file to query")

    args = parser.parse_args()

    bloom_filter = None

    # Initialize Bloom Filter if --init is provided
    if args.init:
        if args.n is None or args.f is None:
            logging.error("Error: Please provide both --n and --f for initialization.")
            return
        bloom_filter = BloomFilter(args.n, args.f)
        logging.info(f"Bloom filter initialized with parameters: n = {bloom_filter.n}, f = {bloom_filter.f}, m = {bloom_filter.m}, k = {bloom_filter.k}")

    # Check if the Bloom Filter has been initialized before proceeding
    if bloom_filter is None:
        logging.error("Error: Bloom Filter not initialized. Run with --init first.")
        return

    # Insert Items from the specified file
    if args.insert_file:
        try:
            with open(args.insert_file, 'r') as f:
                content = f.read().strip().splitlines()
                for line in content:
                    document = line.strip()
                    bloom_filter.insert_txt(document)  # Add document to Bloom filter
            logging.info(f"Inserted items from file: {args.insert_file}")
        except FileNotFoundError:
            logging.error(f"Error: The file {args.insert_file} does not exist.")
            return
    else:
        logging.error("Please provide a valid path to the file for insertion using --insert-file")

    # Query Items from the specified file
    if args.query_file:
        try:
            result = 0
            with open(args.query_file, 'r') as f:
                content = f.read().strip().splitlines()
                for line in content:
                    document = line.strip()
                    if bloom_filter.query_txt(document):
                        result += 1
            if result > 0: 
                logging.info(f"There are {result} items in {args.query_file} possibly in the filter.")
            else: 
                logging.info(f"Nothing in {args.query_file} in the filter.")
        except FileNotFoundError:
            logging.error(f"Error: The file {args.query_file} does not exist.")
            return
    else:
        logging.info("Please provide a valid path to the file for querying using --query-file")


if __name__ == "__main__":
    main()



