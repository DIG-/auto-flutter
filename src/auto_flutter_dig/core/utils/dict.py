from abc import ABC
from typing import Callable, Dict, List, Mapping, Optional, TypeVar


class _Dict(ABC):
    K = TypeVar("K")
    V = TypeVar("V")

    @staticmethod
    def get_or_none(input: Mapping[K, V], key: K) -> Optional[V]:
        return None if not key in input else input[key]

    @staticmethod
    def get_or_default(input: Mapping[K, V], key: K, fallback: Callable[[], V]) -> V:
        return fallback() if not key in input else input[key]

    @staticmethod
    def merge(a: Dict[K, V], b: Optional[Dict[K, V]]) -> Dict[K, V]:
        if b is None:
            return a
        c = a.copy()
        for k, v in b.items():
            c[k] = v
        return c

    @staticmethod
    def merge_append(a: Dict[K, List[V]], b: Optional[Dict[K, List[V]]]) -> Dict[K, List[V]]:
        if b is None:
            return a
        c = a.copy()
        for k, v in b.items():
            if k in c:
                c[k].extend(v)
            else:
                c[k] = v
        return c

    @staticmethod
    def flatten(input: Mapping[K, V]) -> List[V]:
        return list(map(lambda x: x[1], input.items()))
