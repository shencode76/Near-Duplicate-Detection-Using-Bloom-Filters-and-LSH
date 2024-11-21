import math 
import mmh3
import pandas as pd
from bitarray import bitarray
import nltk
from nltk import ngrams

# Construction of Bloom Filter using Bitarray 
class BloomFilter:
    """Implementation of Bloom filter use ppython wrapper for murmurhas, mmh3
    """
    def __init__(self,n, f, m = 0, k = 0) -> None:
        """Initialize a Bloom Filter with given n and false posive rate.
            a bit array [0, m-1] with all slots initially set to 0
            k independent hash functions, each mapping keys uniformly randomly onto a range[0, m-1]

        Args:
            n (int): number of elements, dataset size
            f (numeric): false positive rate
            m (int): number of bits in the Bloom Filter defining its size/space, size of filter
            k (int): number of hash functions
        """
        self.n = n
        self.f = f
        self.m = m if m !=0 else self.calculateM()
        self.k = k if k != 0 else self.calculateK()

        self.bit_array = bitarray(self.m)
        self.bit_array.setall(0) # set all slots to 0 initially
        self.printParameters()

    def calculateM(self) -> int:
        """Calculate M, the number of bits in the Bloom Filter defining its size/space

        Returns:
            integer: the number of bits in the Bloom Filter defining its size/space
        """
        return int(-math.log(self.f) * self.n/(math.log(2)**2))
    
    def calculateK(self) -> int:
        """Calculate K, the number of hash functions

        Returns:
            int: number of hash functions
        """
        return int(self.m*math.log(2)/self.n)
    
    def printParameters(self) -> str:
        """Print the initial parameters: n, f, m, k
        """
        print("Init parameters:")
        print(f"n = {self.n}, f={self.f}, m={self.m}, k={self.k}")

    def insert(self,item) -> None:
        """Insert a representation of the element item into Bloom Filter
        The hash function from mmh3 will map keys to integers

        Args:
            item (Object): a given item to be hashed and added to Bloom Filter
        """
        for i in range(self.k):
            index = mmh3.hash(item, i) % self.m
            self.bit_array[index] = 1

    def query(self, item) -> bool:
        """To see whether some element is in the Bloom Filter, we use this query function to look it up. We use k hashes of x and see if the corresponding bits are turned on.


        Args:
            item (Object): given item to look up 

        Returns:
            Boolean: Boolean value of whether the item is in Bloom Filter
        """
        for i in range(self.k):
            index = mmh3.hash(item, i) % self.m
            if self.bit_array[index] == 0:
                return False
            
        return True
    
    def insert_txt(self, doc_item) -> None:
        """Insert text into Bloom Filter

        Args:
            doc_item (Object): document
        """
        tokens = doc_item.lower().split()
        n_grams = ngrams(tokens, 4)
        for piece in n_grams:
            shingle = ' '.join(piece)
            self.insert(shingle)

    def query_txt(self, doc_item) -> bool:
        """Check if a query is possibly in the Bloom filter by breaking it into n-grams and querying each n-gram.

        Args:
            query_text (str): The text to query.

        Returns:
            bool: True if all n-grams of the query are possibly in the filter, False if any n-gram is definitely not in the filter.
        """
        tokens = doc_item.lower().split()  # Tokenize and convert to lowercase

        n_grams = ngrams(tokens, 4)
        for piece in n_grams:
            search_shingle = ' '.join(piece)
            if not self.query(search_shingle):
                return False  # If any n-gram is not found, return False
    
        return True