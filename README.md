# Near-Duplicate Detection Using Bloom Filters and Locality Sensitive Hashing (LSH)


## Project Description:
This project implements an approach for detecting near-duplicate documents using Bloom Filters and Locality Sensitive Hashing (LSH). The task involves building custom solutions for these algorithms without relying on external duplicate detection libraries. The project consists of:

### Baseline Implementation: Exact duplicate detection using MD5 hashes.
* Bloom Filter: Optimized for efficient space usage in detecting duplicates.
* Locality Sensitive Hashing (LSH): Used for approximate nearest neighbor search and deduplication with banding and Union-Find.
Key aspects include:

### Exploratory Data Analysis on text datasets to understand the baseline and improve performance.
* Experimentation with improvements on Bloom filters and LSH to minimize false positives and optimize for larger datasets.
* GitHub Actions for automated testing and continuous integration, ensuring code quality with unit tests and documentation generation using Sphinx.
### Collaborative Development: Work organized via Git, GitHub Issues, and Pull Requests for effective team collaboration.
The final submission includes results for different document sizes (300, 1000, 10000, and 100000 documents) and an analysis of performance and improvements using visualizations.

## Bloom Filter Summary 

Please see [a2/README.md]([README](https://github.com/DSAN6700-24Fall/assignment-2-chick-fil-a/blob/main/a2/README.md)) for more information about the installation procedures of this problem. 

### Introduction :
In this project, we developed two python scripts for bloom filters, including BloomFilter, StandardBloomFilter, ChunkedBloomFilter, ImprovedBloomFilter. To distinguish the bloom filters to answer exercise 1,2, and 3 in the [page 59 of Algorithms and Data Structures for Massive Datasets](https://ebookcentral-proquest-com.proxy.library.georgetown.edu/lib/georgetown/reader.action?docID=7049417&ppg=64), we seperate the bloom filter classes in two scipts([bloomfilter1.py](https://github.com/DSAN6700-24Fall/assignment-2-chick-fil-a/blob/main/a2/src/a2/bloomfilter1.py) and [bloomfilter3.py](https://github.com/DSAN6700-24Fall/assignment-2-chick-fil-a/blob/main/a2/src/a2/bloomfilter3.py)).


## Baseline Summary 

Please see [a2/README.md]([README](https://github.com/DSAN6700-24Fall/assignment-2-chick-fil-a/blob/main/a2/README.md)) for more information about the installation procedures of this problem. 

## LSH Summary 

This project explores two Locality Sensitive Hashing (LSH) cases for document deduplication and approximate nearest neighbor search, along with an improved LSH variant to enhance the efficiency and accuracy of duplicate detection.

The functions are organized within dedup.py file, including the two improvements.

- Case 1: Collection Deduplication with Basic LSH (lsh_case1.py)
In this case, we apply LSH to detect and cluster near-duplicate documents within a dataset. The process includes text normalization, MinHash signature generation, and LSH-based candidate pair identification, Jaccard Similarity Computation, followed by Union-Find clustering. 

- Case 2: Approximate Nearest Neighbor Search (lsh_case2.py)
This case enables a query-based search for finding documents within a dataset that are most similar to a given input. It combines the basic LSH deduplication process with a tailored search procedure, transforming the query into a hashed representation and identifying similar documents based on hash collisions. 

- Improved LSH with Dynamic Shingle Size and Multi-Probe (lsh_case1_imp.py)
    To further enhance duplicate detection, the improved LSH variant incorporates two key adjustments:

    - Dynamic Shingle Size: Adjusts the shingle (n-gram) size based on document length, allowing finer-grained signature generation for shorter documents and broader representations for longer ones. This approach reduces redundancy in MinHash signatures and improves candidate pair precision.

    - Multi-Probe LSH: Increases candidate recall by probing adjacent buckets, thus capturing high-similarity pairs that may fall near but not within the same bucket. This adjustment decreases the number of missed near-duplicates without heavily impacting precision, offering a more robust and flexible deduplication solution.

This project provides a CLI (cli.py) to run both cases and the improved LSH variant, making it adaptable for different document deduplication and search needs.

Please see [a2/README.md]([README](https://github.com/DSAN6700-24Fall/assignment-2-chick-fil-a/blob/main/a2/README.md)) for more information about the installation procedures of this problem. 

The package is structured using poetry, and we set up the command-line interface (CLI) to enable users to run our code. We documented our code with informative README and function docstrings, and established a CI/CD workflow on GitHub Actions to automate the installation and documentation processes. For more information regarding document processing (how did you tokenize the text or did you run any text normalization beforehand), algorithmic choices (what shingle size did you use or how did you calculate the size of the Bloom filter), please visit the discussion.md.