import hashlib
import re
import time
import tracemalloc
from collections import defaultdict, Counter
from typing import List, Set
import argparse
import os


# Clean and normalize text 
def clean_and_normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# MD5 
def compute_md5(text):
    return hashlib.md5(text.encode()).hexdigest()

# Remove leading numbers 
def remove_leading_numbers(line):
    return re.sub(r'^\d+\s*', '', line)

# Generate word frequency dictionary
def generate_word_frequency(document: str) -> Counter:
    words = clean_and_normalize(document).split()
    return Counter(words)

# Generate shingles
def generate_shingles(document, k=3):
    words = clean_and_normalize(document).split()
    shingles = {tuple(words[i:i + k]) for i in range(len(words) - k + 1)}
    return shingles

# Deduplication 
def deduplicate_file(file_path):
    md5_hashes = defaultdict(set)
    word_freq_duplicates = defaultdict(set)
    exact_shingle_duplicates = defaultdict(set)
    
    # Read file
    with open(file_path, 'r') as file:
        file_content = file.readlines()
    
    # MD5-based deduplication (Exact Duplicate Detection)
    tracemalloc.start()
    start_time = time.time()
    for i, line in enumerate(file_content, 1):
        clean_line = remove_leading_numbers(line.strip())
        line_md5 = compute_md5(clean_line)
        md5_hashes[line_md5].add(i)
    md5_duration = time.time() - start_time
    md5_memory = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    # Word frequency-based deduplication
    tracemalloc.start()
    start_time = time.time()
    word_freq_sets = []
    for i, line in enumerate(file_content, 1):
        clean_line = remove_leading_numbers(line.strip())
        word_freq = generate_word_frequency(clean_line)
        word_freq_sets.append((i, word_freq))

        # Compare with previous lines' word frequencies 
        for j in range(i):
            _, previous_word_freq = word_freq_sets[j]
            if word_freq == previous_word_freq:
                word_freq_duplicates[frozenset(word_freq.items())].update({i, j + 1})
    word_freq_duration = time.time() - start_time
    word_freq_memory = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

     # Exact Shingle-based Deduplication (Exact Shingles Matches)
    shingle_sets = []
    tracemalloc.start()
    start_time = time.time()
    for i, line in enumerate(file_content, 1):
        clean_line = remove_leading_numbers(line.strip())
        shingles = generate_shingles(clean_line, k=3)
        shingle_sets.append((i, shingles))


    exact_shingle_sets = defaultdict(set)
    for i, (line_num, shingles) in enumerate(shingle_sets):
        exact_shingle_sets[frozenset(shingles)].add(line_num)
    exact_shingle_duration = time.time() - start_time
    exact_shingle_memory = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()


    return (
        md5_hashes, word_freq_duplicates, exact_shingle_sets,
        (md5_duration, word_freq_duration, exact_shingle_duration),
        (md5_memory, word_freq_memory, exact_shingle_memory)
    )


def format_output_unique(hashes):
    output = []
    seen_lines = set()  

    for _, line_numbers in hashes.items():
        unique_line_numbers = [line for line in sorted(line_numbers) if line not in seen_lines]
        if unique_line_numbers:
            output.append(" ".join(map(str, unique_line_numbers)))
            seen_lines.update(unique_line_numbers)  # Mark these lines as seen

    return output

def main():
    parser = argparse.ArgumentParser(description="Deduplicate text file based on MD5, word frequency, and exact shingle methods.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("output_dir", help="Directory to save output files")
    args = parser.parse_args()

    # Paths
    input_file = args.input_file
    output_dir = args.output_dir
    
    # Extract the base name of the input file (e.g., "hundred" from "hundred.tsv")
    input_filename = os.path.splitext(os.path.basename(input_file))[0]

    md5_hashes, word_freq_duplicates, exact_shingle_duplicates, durations, memories = deduplicate_file(input_file)

    # Write results to output files with dynamic names
    with open(f"{output_dir}/{input_filename}-md5.txt", 'w', newline='\n') as f:
        f.write("MD5 Deduplication (Exact Matches):\n")
        for result in format_output_unique(md5_hashes):
            f.write(result + '\n')

    with open(f"{output_dir}/{input_filename}-wordfreq.txt", 'w', newline='\n') as f:
        f.write("Word Frequency-based Deduplication:\n")
        for result in format_output_unique(word_freq_duplicates):
            f.write(result + '\n')

    with open(f"{output_dir}/{input_filename}-shingle.txt", 'w', newline='\n') as f:
        f.write("Exact Shingle-based Deduplication (Exact Shingles Matches):\n")
        for result in format_output_unique(exact_shingle_duplicates):
            f.write(result + '\n')

    # Print timing and memory usage results
    print("\nPerformance Summary:")
    print(f"MD5 Deduplication - Time: {durations[0]:.4f}s, Memory: {memories[0] / 1024:.2f} KB")
    print(f"Word Frequency-based Deduplication - Time: {durations[1]:.4f}s, Memory: {memories[1] / 1024:.2f} KB")
    print(f"Exact Shingle-based Deduplication - Time: {durations[2]:.4f}s, Memory: {memories[2] / 1024:.2f} KB")

if __name__ == "__main__":
    main()
