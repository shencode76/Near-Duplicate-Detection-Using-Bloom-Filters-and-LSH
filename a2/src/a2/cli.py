import sys
import logging
#from lsh_case1 import deduplicate_collection as case1
#from lsh_case1_imp import deduplicate_collection as case1_imp
#from lsh_case2 import nearest_neighbor_search as case2
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from .lsh_case1 import deduplicate_collection as case1
from .lsh_case1_imp import deduplicate_collection as case1_imp
from .lsh_case2 import nearest_neighbor_search as case2

logging.basicConfig(level=logging.INFO)

def main():
    if len(sys.argv) < 4:
        logging.error("Usage: python cli.py <case1|case1_imp|case2> <input_file> <output_file>")
        sys.exit(1)
    parser = argparse.ArgumentParser(description="LSH CLI for Case 1 and Case 2")
    parser.add_argument('case', choices=['case1', 'case1_imp', 'case2'], help="Specify which case to run (case1 or case2)")
    parser.add_argument('input_file', help="Path to the input file")
    parser.add_argument('output_file', help="Path to the output file")
    parser.add_argument('--query', help="Query text for case2 (only needed for case2)", default=None)

    args = parser.parse_args()

    if args.case == 'case1':
        logging.info("Running LSH Case 1 Deduplication...")
        case1(args.input_file, args.output_file)
    elif args.case == 'case1_imp':
        logging.info("Running LSH Case 1 (improved) Collection Deduplication...")
        case1_imp(args.input_file, args.output_file)
    elif args.case == 'case2':
        if args.query is None:
            logging.error("Query is required for case2")
            sys.exit(1)
        logging.info("Running LSH Case 2 Approximate Nearest Neighbor Search...")
        case2(args.input_file, args.output_file, args.query)
    else:
        logging.error("Invalid case selected. Use 'case1', 'case1_imp' or 'case2'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

# python -m src.a2.cli.py case1 <input_file> <output_file>
# eg:
# python -m src.a2.cli case1 data/five.tsv data/result/sample_result_case1.txt

# python -m src.a2.cli.py case1_imp <input_file> <output_file>
# eg:
# python -m src.a2.cli case1_imp data/five.tsv data/result/sample_result_case1_imp.txt

# python -m src.a2.cli.py case2 <input_file> <output_file> --query "YOUR_QUERY_TEXT"
# eg:
# python -m src.a2.cli case2 data/five.tsv data/result/sample_result_case2.txt --query "cherry garcia ice"
