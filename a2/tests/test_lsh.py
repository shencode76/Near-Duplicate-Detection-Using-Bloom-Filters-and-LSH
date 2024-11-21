import unittest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Import basic LSH and Union-Find methods
from src.a2.dedup import lsh_hash
from src.a2.dedup import minhash_signature
from src.a2.dedup import UnionFind

class TestMinhashSignature(unittest.TestCase):
    
    def test_minhash_signature_consistency(self):
        # Sample text and parameters
        text = "This is a sample document for testing"
        num_permutations = 100
        
        # Run minhash signature computation multiple times
        signature1 = minhash_signature(text, num_permutations)
        signature2 = minhash_signature(text, num_permutations)
        
        # Verify that the signatures are identical for consistent hashing
        self.assertEqual(signature1, signature2, "Minhash signatures should be consistent across identical inputs.")
    
    def test_minhash_signature_length(self):
        text = "Another document for testing"
        num_permutations = 100
        signature = minhash_signature(text, num_permutations)
        
        # Verify the length of the signature matches the number of permutations
        self.assertEqual(len(signature), num_permutations, "Signature length should match num_permutations.")

class TestLSHBanding(unittest.TestCase):
    
    def test_lsh_hash_band_consistency(self):
        # Simulated minhash signatures for two identical documents
        signature1 = [1, 2, 3, 4, 5] * 20  # Repeated to create a 100-length signature
        signature2 = [1, 2, 3, 4, 5] * 20
        
        bands = 20
        rows = len(signature1) // bands
        
        band_hashes1 = lsh_hash(signature1, bands, rows)
        band_hashes2 = lsh_hash(signature2, bands, rows)
        
        # Verify that band hashes for identical signatures are equal
        self.assertEqual(band_hashes1, band_hashes2, "Band hashes should be identical for identical signatures.")

    def test_lsh_hash_band_count(self):
        signature = [1, 2, 3, 4, 5] * 20
        bands = 20
        rows = len(signature) // bands
        
        band_hashes = lsh_hash(signature, bands, rows)
        
        # Verify that the number of band hashes matches the number of bands
        self.assertEqual(len(band_hashes), bands, "Number of band hashes should match the number of bands.")

class TestUnionFind(unittest.TestCase):
    
    def test_union_find_single_cluster(self):
        uf = UnionFind(5)
        uf.union(0, 1)
        uf.union(1, 2)
        uf.union(2, 3)
        uf.union(3, 4)
        
        # Verify that all elements are in the same cluster
        root = uf.find(0)
        for i in range(1, 5):
            self.assertEqual(uf.find(i), root, "All elements should be in the same cluster.")

    def test_union_find_multiple_clusters(self):
        uf = UnionFind(5)
        uf.union(0, 1)
        uf.union(2, 3)
        
        # Verify that 0 and 1 are in one cluster, 2 and 3 in another, and 4 is separate
        self.assertEqual(uf.find(0), uf.find(1), "0 and 1 should be in the same cluster.")
        self.assertEqual(uf.find(2), uf.find(3), "2 and 3 should be in the same cluster.")
        self.assertNotEqual(uf.find(0), uf.find(4), "0 and 4 should not be in the same cluster.")
        self.assertNotEqual(uf.find(2), uf.find(4), "2 and 4 should not be in the same cluster.")

if __name__ == "__main__":
    unittest.main()
