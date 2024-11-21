# a2

A2 for bloom filter and LSH and baseline

## Installation

To implement, you'll need Python 3.9 or later. You can install the necessary dependencies using `pip` or your preferred package manager. Here’s how to get started:

1. Clone the repository:
```bash
git clone https://github.com/DSAN6700-24Fall/assignment-2-chick-fil-a.git
pip install a2
```
## Work Directory Tree

```markdown
.
├── README.md
└── a2
    ├── CHANGELOG.md
    ├── LICENSE
    ├── README.md
    ├── data
    │   ├── five.tsv
    │   ├── hundred.tsv
    │   ├── hundredk.tsv
    │   ├── onek.tsv
    │   ├── result
    │   │   ├── 3_bloom_filters_comparision.png
    │   │   ├── bloomfilter_falsepositiverate.png
    │   │   ├── case2_onek.txt
    │   │   ├── case2_threehundred.txt
    │   │   ├── empirical_s_curve.png
    │   │   ├── exact.png
    │   │   ├── f1_score_vs_bands.png
    │   │   └── f1_score_vs_rows.png
    │   ├── tenk.tsv
    │   ├── thirty.tsv
    │   ├── thirtyk.tsv
    │   ├── threehundred.tsv
    │   └── threek.tsv
    ├── discussion.md
    ├── docs
    │   ├── Makefile
    │   ├── changelog.md
    │   ├── conf.py
    │   ├── example.ipynb
    │   ├── index.md
    │   ├── make.bat
    │   └── requirements.txt
    ├── expected
    │   ├── five-md5.txt
    │   ├── five-shingle.txt
    │   ├── five-wordfreq.txt
    │   ├── thirty-md5.txt
    │   ├── thirty-shingle.txt
    │   └── thirty-wordfreq.txt
    ├── poetry.lock
    ├── pyproject.toml
    ├── results
    │   ├── hundredk-Shingle.txt
    │   ├── hundredk-WordFreq.txt
    │   ├── hundredk-lsh-imp.txt
    │   ├── hundredk-lsh.txt
    │   ├── hundredk-md5.txt
    │   ├── onek-Shingle.txt
    │   ├── onek-WordFreq.txt
    │   ├── onek-lsh-imp.txt
    │   ├── onek-lsh.txt
    │   ├── onek-md5.txt
    │   ├── tenk-Shingle.txt
    │   ├── tenk-WordFreq.txt
    │   ├── tenk-lsh-imp.txt
    │   ├── tenk-lsh.txt
    │   ├── tenk-md5.txt
    │   ├── threehundred-Shingle.txt
    │   ├── threehundred-WordFreq.txt
    │   ├── threehundred-lsh-imp.txt
    │   ├── threehundred-lsh.txt
    │   └── threehundred-md5.txt
    ├── src
    │   └── a2
    │       ├── __init__.py
    │       ├── a2.py
    │       ├── baseline.py
    │       ├── bloomfilter1.py
    │       ├── bloomfilter1_cli.py
    │       ├── bloomfilter3.py
    │       ├── bloomfilter3_cli.py
    │       ├── cli.py
    │       ├── dedup.py
    │       ├── eda-baseline.py
    │       ├── lsh_case1.py
    │       ├── lsh_case1_imp.py
    │       ├── lsh_case2.py
    │       └── utils.py
    ├── test_output
    │   ├── five-md5.txt
    │   ├── five-shingle.txt
    │   ├── five-wordfreq.txt
    │   ├── thirty-md5.txt
    │   ├── thirty-shingle.txt
    │   └── thirty-wordfreq.txt
    └── tests
        ├── five.tsv
        ├── hundred.tsv
        ├── short_sent.tsv
        ├── test_a2.py
        ├── test_baseline.py
        ├── test_bloomfilter.py
        └── test_lsh.py
 
 ```

 
### Baseline 

The baseline of this problem contain 3 methods: md5 hashes, word frequency dictionary, and shingling.

The following files or directories are related with baseline method:

* a2/data: All the data needed for baseline methods.
* a2/expected: Expected output for five.tsv and thirty.tsv used for pytest.
* a2/results: Contain results for 3 baseline methods on 300, 1000, 10000, and 100000 datasets.
* a2/test_output: The folder to put output during pytest.
* tests/test_baseline.py: The code used for pytest.
* src/a2: eda-baseline.py and baseline.py used for exploratory data analysis and implementing the code.

#### EDA

Before we start working on the methods, we need to look at the average length of the lines, and the top frequent words.

cd to the following directory: ./a2/src/a2, and run the following command :

```bash
python eda-baseline.py ../../data/thirty.tsv
```

and you can have the summary of line length and word frequency printed in the terminal:  

Exploratory Data Analysis Results

**Sentence Length Statistics:**  
Average Word Count: 712.9333333333333
Average Char Count: 4123.533333333334
Max Word Count: 1898
Min Word Count: 296
Max Char Count: 10085
Min Char Count: 2178

**Top 10 Most Common Words:** 
the: 1086
and: 663
to: 628
of: 464
a: 459
in: 406
on: 247
that: 241
is: 221
for: 210

For small files like five.tsv, we can manually check the duplicates:

|  number  | line | 
|----------|----------|
|   1  |   TWO CHERRY PUMPKIN TARTS| 
| 2 |  CHERRY GARCIA ICE CREAM |  
| 3  | TWO CHERRY PUMPKIN TARTS  | 
| 4|   CHEESEBURGERS IN PARADISE |  
| 5 | CHEESEBURGER IN PARADISE | 

1 and 3 are exact duplicates, and 4 and 5 are near duplicates.

#### Three baseline methods

As the simple baseline of the deduplication problem, we decided to use the following three methods:

* MD5 hashes: Compute the MD5 hash for each line of text and use the hash value as an identifier to compare with hashes of other lines. If two lines had the same hash, they were considered duplicates.

* Word frequency dictionary: Convert each line into a frequency dictionary, counting the words in the line and their respective frequencies. If two lines have matching frequency dictionaries, they were considered duplicates.
  
* Shingling: Generate a set of overlapping substrings (shingles) for each line and convert this shingle set to an immutable frozenset. Compare these sets across lines to determine duplicates.

The code for the three methods are in the src/a2 folder, the data used is in the data folder, and the results should be printed to the result folder.  

cd to the following directory: ./a2/src/a2, and run the following command :

```bash
python baseline.py ../../data/hundred.tsv ../../results
```
The hundred.tsv could be replaced by any .tsv files that you would like to run, but note that running hundredk.tsv file or larger may take hours, to test the code, it is suggested to run onek.tsv or smaller.

The time and memory the process use will be printed in the terminal, and the output files can be seen in the results folder.

Now the results folder already have the results for all three methods on threehundred.tsv, onek.tsv, tenk.tsv, and hundredk.tsv. The time and memory cost is as below:

time:

|  method  | threehundred | onek | tenk | hundredk |
|----------|----------|----------|----------|----------|
|   md5  |    0.0046s | 0.0142s   |  0.1171s  |  1.1590s  |
| wordfreq|   0.4551s |  3.2142s  |  250.2766s  |   42413.9304s |
| shingling  | 0.3551s   | 1.1611s  | 12.2582s  |  155.1292s |


memory:


|  method  |  threehundred | onek | tenk | hundredk |
|----------|----------|----------|----------|----------|
|   md5  |   111.75KB |   334.89KB | 3074.35KB   |   33514.21KB |
| wordfreq|  16880.80KB  |  54282.52KB  |  537376.51KB  | 5312240.56KB   |
| shingling  |  38182.32KB  | 129228.10KB  | 1260272.68KB  |  12490973.33KB |

see more details in the discussion.md.

#### pytest

To test the code, we can compare the output with expected output.

cd to the following directoty: ./a2, and run the following command :

```bash
python tests/test_baseline.py
```
This will generate test output in the test_output folder for you to check manually, and the code also tests automatically, if the output matches the expectation, it will print "Test passed for {input_file}", or it will print the expected and actual results in the terminal. This process can also be done through the workflow.

### Bloom Filter
**Bloom Filter** is a probabilistic data structure that efficiently tests whether an element is a member of a set. Bloom Filters allow for fast membership testing with a configurable false positive rate, making them ideal for applications where space efficiency and quick queries are essential.

#### Features

- **Space Efficient**: Uses hash functions and bit arrays to reduce memory usage compared to traditional data structures.
- **Fast Query Times**: Provides constant time complexity for membership queries.
- **Configurable False Positive Rate**: Allows users to adjust the false positive probability based on their needs.

#### Usage
##### Basic Bloom Filter
Firstly, please make sure you are within a2 directory as in "assignment-2-chick-fil-a/a2"

```python
# Importing the BloomFilter class from the a2.bloomfilter1 module.
from a2.bloomfilter1 import BloomFilter

# Initializing a Bloom filter with an estimated capacity of n (10 million elements)
# and a desired false positive rate of f (2%). This setup optimizes the Bloom filter's
# size and performance based on the specified parameters.
n = 10**7  # Estimated number of elements in the Bloom filter
f = 0.02   # Desired false positive rate (2%)
bf = BloomFilter(n, f)  # Create a Bloom filter instance with the given parameters
```

We have already set up a command-line interface (CLI) to run our code of Bloom Filter. See example below:
command template: `python -m src.a2.bloomfilter1_cli --init --n <number_of_elements> --f <false_positive_rate> --insert-file <path_to_file_to_be_inserted> --query-file <path_to_file_to_be_queried>`

```bash
# usage example:
cd a2 #(if you are in the root position(ASSIGNMENT-2-CHICK-FIL-A))

python -m src.a2.bloomfilter1_cli --init --n 10000000 --f 0.02 --insert-file ./data/thirty.tsv --query-file ./data/five.tsv
```
This command reads a file (thirty.tsv) of documents, performs duplication-search for results in ./data/five.tsv

##### StandardBloomFilter, ChunkedBloomFilter, ImprovedBloomFilter

```python
# Importing the BloomFilter class from the a2.bloomfilter3 module.
from a2.bloomfilter3 import StandardBloomFilter, ChunkedBloomFilter, ImprovedBloomFilter

# For the default setting,  n  equals the length of the test file imported, and  p  equals the desired false positive rate (which I have set to 0.2, quite loose here). The function calculate_bloom_filter_size will help calculate  m  and  k  accordingly.
n = len(lines)
p = 0.2
m, k = calculate_bloom_filter_size(n, p)

# For the chunked Bloom Filter, the number of parts set here is 5; for the Improved Bloom Filter, the method used is Kirsch-Mitzenmacher.
standard_bloom = StandardBloomFilter(m, k)
chunked_bloom = ChunkedBloomFilter(m, k, 5)
improved_bloom = ImprovedBloomFilter(m, k, method='kirsch-mitzenmacher')

```

Just like mentioned before, please see example below: 
- for standard bloom filter: `python -m src.a2.bloomfilter3_cli --init --n <number_of_elements> --f <false_positive_rate> --insert-file <path_to_file_to_be_inserted> --query-file <path_to_file_to_be_queried>`
- for chunked bloom filter:`python -m src.a2.bloomfilter3_cli --init --type <Type of Bloom Filter to initialize> --n <number_of_elements> --f <false_positive_rate> --chunks <Number of chunks (required for chunked Bloom Filter)> --insert-file <path_to_file_to_be_inserted> --query-file <path_to_file_to_be_queried>`
- for improved bloom filter:`python -m src.a2.bloomfilter3_cli --init --type <Type of Bloom Filter to initialize> --n <number_of_elements> --f <false_positive_rate> --method <Hashing method to use for improved Bloom Filter> --insert-file <path_to_file_to_be_inserted> --query-file <path_to_file_to_be_queried>`

```bash
# usage example:
cd a2 #(if you are in the root position(ASSIGNMENT-2-CHICK-FIL-A))

# start with python or python3, based on your system
python -m src.a2.bloomfilter3_cli --init --n 10000000 --f 0.02 --insert-file ./data/thirty.tsv --query-file ./data/five.tsv
python -m src.a2.bloomfilter3_cli --init --type 'chunked' --n 10000 --f 0.02 --chunks 5 --insert-file ./data/thirty.tsv --query-file ./data/five.tsv                                    
python -m src.a2.bloomfilter3_cli --init --type 'improved' --n 100000 --f 0.02 --method 'kirsch-mitzenmacher' --insert-file ./data/thirty.tsv --query-file ./data/five.tsv
```

#### How It Works

A Bloom Filter consists of:

- A bit array of size `m`, initialized to all zeros.
- `k` independent hash functions that map elements to `m` positions in the bit array.

When an element is added to the Bloom Filter, the hash functions calculate `k` indices, and the bits at those indices are set to 1. To check for membership, the same hash functions are applied to the element, and the bits at the computed indices are checked. If all bits are 1, the element may be in the set; if any bit is 0, the element is definitely not in the set.

For the Chunked Bloom Filter, it has an additional parameter called `num_chunks`, which specifies the number of parts you want. Also, for the Improved Bloom Filter, it has another parameter called `method`, which allows you to choose different hashing strategies to meet varying performance requirements and reduce the probability of false positives.

**False Positive Rate**

- Bloom Filters can return false positives (indicating that an element is in the set when it is not). The rate of false positives depends on the size of the bit array, the number of elements, and the number of hash functions used.

##### Run Bloom Filter Pytest using: 
- direct to a2 folder as in "/assignment-2-chick-fil-a/a2"
- run "pytest ./tests/test_bloomfilter.py"

### Locality Sensitive Hashing (LSH)

Locality Sensitive Hashing (LSH) is a technique used to efficiently find approximate or near-duplicate items in large datasets. Unlike traditional hashing, which aims to distribute items uniformly, LSH is designed so that similar items hash to the same or similar "buckets" with high probability. This makes it particularly useful in applications like near-duplicate detection, image similarity, and recommendation systems, where exact matches aren't required, but finding approximate matches quickly is essential.


#### Features
- **Approximate Matching**: LSH is designed for finding near-duplicates or approximate matches, making it ideal for similarity search tasks where some flexibility is acceptable.

- **Efficiency and Scalability**: By reducing the number of pairwise comparisons, LSH is much faster than brute-force similarity searches and scales well with large datasets.

- **Buckets Based on Similarity**: Similar items are hashed into the same or nearby buckets with high probability, enabling quick retrieval of likely matches.

- **Parameter Flexibility**: LSH allows tuning parameters like the number of hash functions and bands, allowing control over the trade-off between precision and recall.

#### Usage 

##### Basic Case1 Run
The basic Case1 involves running LSH without improvements. To execute this:

Firstly, please make sure you are within a2 directory as in "assignment-2-chick-fil-a/a2"

```bash
python -m src.a2.cli case1 <input_file> <output_file>
```
Example:

```bash
python -m src.a2.cli case1 data/five.tsv data/result/sample_result.txt
```

This command reads a file (five.tsv) of documents, performs deduplication using the basic LSH algorithm, and outputs results to result/basic_result.txt.

##### Improved Case1 Run
The improved deduplication includes multi-probe LSH and dynamic shingle sizing. To run this:

Firstly, please make sure you are within a2 directory as in "assignment-2-chick-fil-a/a2"

```bash
python -m src.a2.cli case1_imp <input_file> <output_file>
```

Example:

```bash
python -m src.a2.cli case1_imp data/five.tsv data/result/improved_result.txt
```

##### Case2 Run
This is the case2. To run this:

Firstly, please make sure you are within a2 directory as in "assignment-2-chick-fil-a/a2"

```bash
python -m src.a2.cli.py case2 <input_file> <output_file> --query "YOUR_QUERY_TEXT"
```

Example:

```bash
python -m src.a2.cli case2 data/five.tsv data/result/sample_result_case2.txt --query "cherry garcia ice"
```

##### Run LSH Pytest:
- direct to a2 folder as in "/assignment-2-chick-fil-a/a2"
- run "pytest tests/test_lsh.py"

##### How-To Guides
###### Running Deduplication
- Place your input file in the data/ directory. Ensure it is a TSV file with two columns (id and text).
- Run the desired script using either the basic or improved method.
- Results are saved in the data/result/ directory, with each line showing clusters of near-duplicate document IDs.

##### Interpreting Output Files
- Output Format: Each line represents a cluster of near-duplicate document IDs.
- Exact Duplicates: At the end of the output file, any exact duplicates are listed line by line.

## Contributing

Interested in contributing? Check out the contributing guidelines. 

Clone and set up the repository with

```bash
git clone TODO && cd a2
pip install -e ".[dev]"
```

Install pre-commit hooks with

```bash
pre-commit install
```

Run tests using

```bash
pytest -v tests
```
  
## License

`a2` was created by team chick-fil-a. It is licensed under the terms of the MIT license.

## Credits

`chick-fil-a/a2` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
