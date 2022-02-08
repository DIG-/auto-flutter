from abc import ABC
from typing import Callable, Dict, List, Optional, TypeVar


class _Dict(ABC):
    K = TypeVar("K")
    V = TypeVar("V")

    def get_or_none(input: Dict[K, V], key: K) -> Optional[V]:
        return None if not key in input else input[key]

    def get_or_default(input: Dict[K, V], key: K, fallback: Callable[[], V]) -> V:
        return fallback() if not key in input else input[key]

    def merge(a: Dict[K, V], b: Optional[Dict[K, V]]) -> Dict[K, V]:
        if b is None:
            return a
        c = a.copy()
        for k, v in b.items():
            c[k] = v
        return c

    def merge_append(
        a: Dict[K, List[V]], b: Optional[Dict[K, List[V]]]
    ) -> Dict[K, List[V]]:
        if b is None:
            return a
        c = a.copy()
        for k, v in b.items():
            if k in c:
                c[k].extend(v)
            else:
                c[k] = v
        return c
