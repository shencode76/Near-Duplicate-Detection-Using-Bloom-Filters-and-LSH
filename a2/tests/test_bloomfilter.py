# The test file for Bloom Filters
import pytest
from a2.bloomfilter1 import BloomFilter # type: ignore
from a2.bloomfilter3 import StandardBloomFilter, ChunkedBloomFilter, ImprovedBloomFilter
import math
import zipfile
import random
import time

def test_example():
    """test task ensure the test file exist
    """
    number = 42
    assert number > 0

    number = -42
    assert number < 0

def test_bloomF_funcs():
    """testing construction of Bloom Filter and functions(insert and query)
    """
    n = 10**7
    f = 0.02
    bf = BloomFilter(n, f)
    bf.insert("1")
    bf.insert("2")
    bf.insert("5")
    bf.insert("7")
    bf.insert("142")

    assert True == bf.query("1")
    assert True == bf.query("2")
    assert False == bf.query("!")
    assert True == bf.query("5")    
    assert False == bf.query("6")
    assert True == bf.query("7")
    assert False == bf.query("42")
    assert True == bf.query("142")
    assert False == bf.query("idk")

def test_bloomF_construction_m():
    """ testing the construction part of Bloom Filter, ensure it will correctly calculate m 
    """
    n = 10**7
    f = 0.02
    m_answer = int(-math.log(f) * n / (math.log(2) ** 2))
    bf = BloomFilter(n, f)
    assert False == (bf.m == 0)
    assert True == (bf.m == m_answer)

def test_bloomF_construction_k():
    """ testing the construction part of Bloom Filter, ensure it will correctly calculate k
    """
    n = 10**5
    f = 0.01
    m_answer = int(-math.log(f) * n / (math.log(2) ** 2))
    k_answer = int(m_answer * math.log(2) / n)
    bf = BloomFilter(n, f)
    assert False == (bf.k == 0)
    assert True == (bf.k == k_answer)

def test_bloomF_withText_near():
    """Testing Bloom filter with larger size
    """
    n = 10**7
    f = 0.02
    bf = BloomFilter(n, f)
    results = []
    time_records = []
    
    with open('./tests/hundred.tsv', 'r') as file:
        content = file.read().strip().splitlines()
        for line in content:
            document = line.strip() 
            bf.insert_txt(document) 
        # Randomly select a sample of documents
        sample_documents = random.sample(content, min(3, len(content))) 
        fake_documents = ["Sailing across the tranquil sea", "Echoes of forgotten memories", 
                            "In the heart of the bustling city, where skyscrapers pierced the sky and the streets were alive with the sounds of honking cars and chattering pedestrians, a small café nestled between two towering buildings offered a quiet refuge for those seeking a moment of tranquility amidst the chaos."]  
        combined_documents = sample_documents + fake_documents

        for doc in combined_documents:
            strt = time.time()

            if bf.query_txt(doc):
                results.append(doc)

            end = time.time()
            time_records.append(round(end-strt,2))
                
        print("time in seconds: ", time_records, "\n")
    expected_found_count = sample_documents   
    assert results == expected_found_count, f"Expected {expected_found_count}, but found {results}"
    assert len(results) != len(combined_documents) 

def test_bloomF_withText_5():
    """Testing Bloom filter with small size
    """
    n = 10**7
    f = 0.02
    bf = BloomFilter(n, f)
    results = [] # store query results 
    sample_sentence = []
    with open('./tests/short_sent.tsv', 'r') as file:
        sample_sentence = file.read().strip().splitlines()
        sample_sentence = [i.strip() for i in sample_sentence]

    expected_outputs = ["CHEESEBURGERS IN PARADISE",
                    "CHERRY TARTS"]

    with open('./tests/five.tsv', 'r') as file:
        content = file.read().strip().splitlines()
        for line in content:
            document = line.strip()
            bf.insert_txt(document)  # Add document to Bloom filter

        for sent in sample_sentence:
            if bf.query_txt(sent):
                results.append(sent)
        
    
    assert results == expected_outputs, f"Expected {len(expected_outputs)} findings, but found {len(results)}"

## StandardBloomFilter test

def test_StandardBloomFilter_withText_5():
    """Testing Bloom filter with small size
    """
    m = 50
    k = 1
    bf = StandardBloomFilter(m, k)
    results = [] # store query results 
    sample_sentence = []
    with open('./tests/short_sent.tsv', 'r') as file:
        sample_sentence = file.read().strip().splitlines()
        sample_sentence = [i.strip() for i in sample_sentence]
    expected_outputs = ["CHEESEBURGERS IN PARADISE",
                    "CHERRY TARTS"]

    with open('./tests/five.tsv', 'r') as file:
        content = file.read().strip().splitlines()
        for line in content:
            document = line.strip()
            bf.add(document)  # Add document to Bloom filter

        for sent in sample_sentence:
            if bf.check(sent):
                results.append(sent)
        
    
    assert results == expected_outputs, f"Expected {len(expected_outputs)} findings, but found {len(results)}"

## ChunckedBloomFilter test

def test_ChunckedBloomFilter_withText_5():
    """Testing Bloom filter with small size
    """
    m = 40
    k = 1
    bf = ChunkedBloomFilter(m, k, 5)
    results = [] # store query results 
    sample_sentence = []
    with open('./tests/short_sent.tsv', 'r') as file:
        sample_sentence = file.read().strip().splitlines()
        sample_sentence = [i.strip() for i in sample_sentence]
    expected_outputs = ["CHEESEBURGERS IN PARADISE",
                    "CHERRY TARTS"]

    with open('./tests/five.tsv', 'r') as file:
        content = file.read().strip().splitlines()
        for line in content:
            document = line.strip()
            bf.add(document)  # Add document to Bloom filter

        for sent in sample_sentence:
            if bf.check(sent):
                results.append(sent)
        
    
    assert f"Expected {len(expected_outputs)} findings, but found {len(results)}"

## ImprovedBloomFilter test

def test_ImprovedBloomFilter_withText_5():
    """Testing Bloom filter with small size
    """
    m = 50
    k = 1
    bf = ImprovedBloomFilter(m, k, method='kirsch-mitzenmacher')
    results = [] # store query results 
    sample_sentence = []
    with open('./tests/short_sent.tsv', 'r') as file:
        sample_sentence = file.read().strip().splitlines()
        sample_sentence = [i.strip() for i in sample_sentence]
    expected_outputs = ["CHEESEBURGERS IN PARADISE",
                    "CHERRY TARTS"]

    with open('./tests/five.tsv', 'r') as file:
        content = file.read().strip().splitlines()
        for line in content:
            document = line.strip()
            bf.add(document)  # Add document to Bloom filter

        for sent in sample_sentence:
            if bf.check(sent):
                results.append(sent)
        
    
    assert results == expected_outputs, f"Expected {len(expected_outputs)} findings, but found {len(results)}"