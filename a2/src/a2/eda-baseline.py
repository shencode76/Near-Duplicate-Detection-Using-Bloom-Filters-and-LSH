import argparse
import re
from collections import Counter
import pandas as pd

# Clean and normalize text 
def clean_and_normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  
    text = re.sub(r'\s+', ' ', text)        
    return text.strip()

# Remove leading numbers 
def remove_leading_numbers(line: str) -> str:
    return re.sub(r'^\d+\s*', '', line)

def eda_analysis(input_file):
    data = pd.read_csv(input_file, sep='\t', header=None, names=["text"])

    # Apply text processing
    data['cleaned_text'] = data['text'].apply(remove_leading_numbers).apply(clean_and_normalize)

    # Calculate sentence lengths
    data['word_count'] = data['cleaned_text'].apply(lambda x: len(x.split()))
    data['char_count'] = data['cleaned_text'].apply(len)

    # Basic statistics for sentence lengths
    sentence_length_stats = {
        'Average Word Count': data['word_count'].mean(),
        'Average Char Count': data['char_count'].mean(),
        'Max Word Count': data['word_count'].max(),
        'Min Word Count': data['word_count'].min(),
        'Max Char Count': data['char_count'].max(),
        'Min Char Count': data['char_count'].min()
    }

    # Unique word frequency distribution
    all_words = ' '.join(data['cleaned_text']).split()
    word_freq = Counter(all_words)
    common_words = word_freq.most_common(10)


    print("\nExploratory Data Analysis Results\n")
    
    print("Sentence Length Statistics:")
    for stat, value in sentence_length_stats.items():
        print(f"{stat}: {value}")
    
    print("\nTop 10 Most Common Words:")
    for word, freq in common_words:
        print(f"{word}: {freq}")

def main():
    parser = argparse.ArgumentParser(description="Perform EDA on a text file for deduplication insights.")
    parser.add_argument("input_file", help="Path to the input TSV file")
    args = parser.parse_args()

    eda_analysis(args.input_file)

if __name__ == "__main__":
    main()
