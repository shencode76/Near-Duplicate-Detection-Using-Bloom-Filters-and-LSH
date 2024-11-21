# 3.1 - textbook

import hashlib
from bitarray import bitarray

class StandardBloomFilter:
    """
    A standard Bloom Filter implementation that provides methods to add items and check if an item exists in the set.
    
    Attributes:
        size (int): The total number of bits in the bit array.
        num_hashes (int): The number of hash functions to use.
        bits (bitarray): A bit array to store the elements.
    """
    
    def __init__(self, size, num_hashes):
        """
        Initializes the Bloom Filter with a specific size and number of hash functions.
        
        Parameters:
            size (int): The size of the bit array.
            num_hashes (int): The number of hash functions to use.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bits = bitarray(size)
        self.bits.setall(0)

    def _hash(self, item, seed):
        """
        Generates a hash for the given item using a specific seed.
        
        Parameters:
            item: The item to hash.
            seed (int): The seed used to provide a unique hash function.
        
        Returns:
            int: A hash index within the bounds of the bit array.
        """
        hash_result = hashlib.sha256((str(item) + str(seed)).encode()).hexdigest()
        return int(hash_result, 16) % self.size

    def add(self, item):
        """
        Adds an item to the Bloom Filter.
        
        Parameters:
            item: The item to be added to the Bloom Filter.
        """
        for i in range(self.num_hashes):
            index = self._hash(item, i)
            self.bits[index] = True

    def check(self, item):
        """
        Checks whether an item might be in the Bloom Filter.
        
        Parameters:
            item: The item to check in the Bloom Filter.
        
        Returns:
            bool: False if the item is definitely not in the filter, True if it might be.
        """
        for i in range(self.num_hashes):
            index = self._hash(item, i)
            if not self.bits[index]:
                return False
        return True

class ChunkedBloomFilter:
    """
    A chunked Bloom Filter implementation that divides the bit array into chunks. This structure can be useful for reducing memory footprint or improving cache efficiency.
    
    Attributes:
        size (int): The total number of bits across all chunks in the Bloom Filter.
        num_hashes (int): The number of hash functions to use.
        num_chunks (int): The number of chunks the Bloom Filter is divided into.
        chunk_size (int): The size of each chunk in bits.
        bits (list[bitarray]): A list of bit arrays representing each chunk.
    """
    
    def __init__(self, size, num_hashes, num_chunks):
        """
        Initializes the Chunked Bloom Filter with specific total size, number of hash functions, and number of chunks.
        
        Parameters:
            size (int): The total size of the bit array.
            num_hashes (int): The number of hash functions to use.
            num_chunks (int): The number of chunks.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.num_chunks = num_chunks
        self.chunk_size = size // num_chunks
        self.bits = [bitarray(self.chunk_size) for _ in range(num_chunks)]
        for b in self.bits:
            b.setall(0)

    def _hash(self, item, seed):
        """
        Generates a hash index for a given item using a specific seed, mapped to the size of a chunk.
        
        Parameters:
            item: The item to hash.
            seed (int): The seed used to provide a unique hash function for the item.
        
        Returns:
            int: A hash index within the bounds of a chunk.
        """
        hash_result = hashlib.sha256((str(item) + str(seed)).encode()).hexdigest()
        return int(hash_result, 16) % self.chunk_size

    def add(self, item):
        """
        Adds an item to the Bloom Filter. Each hash function corresponds to a different chunk.
        
        Parameters:
            item: The item to be added to the Bloom Filter.
        """
        for i in range(self.num_hashes):
            chunk_index = i % self.num_chunks
            index = self._hash(item, i)
            self.bits[chunk_index][index] = True

    def check(self, item):
        """
        Checks whether an item might be in the Bloom Filter. An item is only considered potentially present if all corresponding bits in each chunk are set to True.
        
        Parameters:
            item: The item to check in the Bloom Filter.
        
        Returns:
            bool: False if the item is definitely not in the filter, True if it might be.
        """
        for i in range(self.num_hashes):
            chunk_index = i % self.num_chunks
            index = self._hash(item, i)
            if not self.bits[chunk_index][index]:
                return False
        return True


# 3.2 - according to a2.pdf

class ImprovedBloomFilter:
    """
    An improved Bloom Filter implementation that supports multiple hashing methods including standard and Kirsch-Mitzenmacher double hashing.

    Attributes:
        size (int): The total number of bits in the bit array.
        num_hashes (int): The number of hash functions to use.
        bits (bitarray): A bit array to store the elements.
        method (str): The method of hashing used in the Bloom Filter ('standard' or 'kirsch-mitzenmacher').
    """
    
    def __init__(self, size, num_hashes, method='standard'):
        """
        Initializes the Bloom Filter with a specific size, number of hash functions, and a hashing method.
        
        Parameters:
            size (int): The size of the bit array.
            num_hashes (int): The number of hash functions to use.
            method (str, optional): The hashing method to use ('standard' or 'kirsch-mitzenmacher'). Defaults to 'standard'.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bits = bitarray(size)
        self.bits.setall(0)
        self.method = method
        if method == 'kirsch-mitzenmacher':
            self.hash1 = self._generate_hash_function()
            self.hash2 = self._generate_hash_function()

    def _generate_hash_function(self):
        """
        Generates a hash function using SHA-256.
        
        Returns:
            function: A lambda function that takes an item and a seed, and returns a hash index.
        """
        return lambda item, seed: int(hashlib.sha256((str(item) + str(seed)).encode()).hexdigest(), 16) % self.size

    def add(self, item):
        """
        Adds an item to the Bloom Filter using the specified hashing method.
        
        Parameters:
            item: The item to be added to the Bloom Filter.
        """
        if self.method == 'standard':
            for i in range(self.num_hashes):
                index = self._hash(item, i)
                self.bits[index] = True
        elif self.method == 'kirsch-mitzenmacher':
            index1 = self.hash1(item, 0)
            index2 = self.hash2(item, 1)
            for i in range(self.num_hashes):
                index = (index1 + i * index2) % self.size
                self.bits[index] = True

    def _hash(self, item, seed):
        """
        Computes a hash index for a given item and seed.
        
        Parameters:
            item: The item to hash.
            seed (int): The seed used to generate the hash.
        
        Returns:
            int: The computed hash index.
        """
        return self._generate_hash_function()(item, seed)

    def check(self, item):
        """
        Checks whether an item might be in the Bloom Filter by checking the bits corresponding to the hash indices.
        
        Parameters:
            item: The item to check in the Bloom Filter.
        
        Returns:
            bool: False if the item is definitely not in the filter, True if it might be.
        """
        for i in range(self.num_hashes):
            if self.method == 'standard':
                index = self._hash(item, i)
            elif self.method == 'kirsch-mitzenmacher':
                index1 = self.hash1(item, 0)
                index2 = self.hash2(item, 1)
                index = (index1 + i * index2) % self.size
            if not self.bits[index]:
                return False
        return True