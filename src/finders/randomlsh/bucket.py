
import random
from typing import Generic, TypeVar

T = TypeVar('T')
class LSHBucket(Generic[T]):
    key_indexes: list[int]
    signature: list[bool]
    bucket: list[T]
    def __init__(self, key_indexes: list[int]):
        self.key_indexes = key_indexes
        self.signature = [random.choice([True, False]) for _ in range(len(key_indexes))]
        self.bucket = []
    def get_key_similarity(self, bin_val: list[bool]) -> int:
        """
            val should look like [True, False, True, False, False]
        """
        similarity = 0
        for i, ki in enumerate(self.key_indexes):
            if bin_val[ki] == self.signature[i]:
                similarity += 1
        return similarity
