"""Implements two simple LRU and TTL dictionaries with generic type annotations."""


import time
from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
from typing import Generic, TypeVar
from typing_extensions import override

_K = TypeVar("_K")  # Key type
_V = TypeVar("_V")  # Value type


class LRUCache(MutableMapping[_K, _V], Generic[_K, _V]):
    """LRU (Least Recently Used) cache with type annotations.

    Maintains key-value pairs and evicts the least recently used key when the maximum capacity is exceeded.
    """

    __slots__ = ("data", "max_size")

    def __init__(self, max_size: int = 100) -> None:
        """Initialize the LRU cache.

        Args:
            max_size: Maximum cache size. When exceeded, the least recently used item will be evicted.
        """
        self.max_size = max_size
        self.data: OrderedDict[_K, tuple[_V, float]] = OrderedDict()

    @override
    def __setitem__(self, key: _K, value: _V) -> None:
        """Set a key-value pair and update its usage.

        Args:
            key: Key to be set.
            value: Value to be set.
        """
        if key in self.data:
            self.data.move_to_end(key)
        elif len(self.data) >= self.max_size:
            self.data.popitem(last=False)
        self.data[key] = (value, time.time())

    @override
    def __getitem__(self, key: _K) -> _V:
        """Retrieve a value by key and update its usage.

        Args:
            key: Key to retrieve.

        Returns:
            The corresponding value.

        Raises:
            KeyError: If the key does not exist.
        """
        if key in self.data:
            value, _ = self.data.pop(key)
            self[key] = value
            return value
        raise KeyError(f"{key} does not exist")

    @override
    def get(self, key: _K, default: _V | None = None) -> _V | None:
        """Retrieve a value by key, or return default if key does not exist.

        Args:
            key: Key to retrieve.
            default: Default value to return if the key does not exist.

        Returns:
            Value associated with the key or the default.
        """
        try:
            return self[key]
        except KeyError:
            return default

    @override
    def __delitem__(self, key: _K) -> None:
        """Delete a key from the cache.

        Args:
            key: Key to delete.

        Raises:
            KeyError: If the key does not exist.
        """
        if key in self.data:
            del self.data[key]
        else:
            raise KeyError(f"{key} does not exist")

    @override
    def __contains__(self, key: object) -> bool:
        """Check whether a key exists.

        Args:
            key: Key to check.

        Returns:
            Whether the key exists.
        """
        return key in self.data

    @override
    def __len__(self) -> int:
        """Get the current size of the cache.

        Returns:
            Number of key-value pairs in the cache.
        """
        return len(self.data)

    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over the keys.

        Returns:
            An iterable object.
        """
        return iter(self.data)

    @override
    def __repr__(self) -> str:
        """Get a human-readable representation of the cache.

        Returns:
            String representation.
        """
        return f"{self.__class__.__name__}({{ {', '.join(f'{k!r}: {v[0]!r}' for k, v in self.data.items())} }})"


class TTLCache(MutableMapping[_K, _V], Generic[_K, _V]):
    """TTL (Time To Live) cache. Key-value pairs automatically expire after a specified duration."""

    __slots__ = ("_data", "_ttl")

    def __init__(self, ttl: float = 60.0) -> None:
        """Initialize the TTL cache.

        Args:
            ttl: Time to live (in seconds) for each key-value pair.
        """
        self._ttl = ttl
        self._data: dict[_K, tuple[_V, float]] = {}

    @override
    def __setitem__(self, key: _K, value: _V) -> None:
        """Set a key-value pair and record the insertion time.

        Args:
            key: Key to be set.
            value: Value to be set.
        """
        self._data[key] = (value, time.time())

    @override
    def __getitem__(self, key: object) -> _V:
        """Retrieve a value by key. If expired, delete the key and raise KeyError.

        Args:
            key: Key to retrieve.

        Returns:
            The corresponding value.

        Raises:
            KeyError: If the key does not exist or has expired.
        """
        if key in self._data:
            value, timestamp = self._data[key]  # type: ignore
            if time.time() - timestamp <= self._ttl:
                return value
            del self._data[key]  # type: ignore
        raise KeyError(f"{key} does not exist or has expired")

    @override
    def get(self, key: _K, default: _V | None = None) -> _V | None:
        """Retrieve a value by key, or return default if key does not exist or has expired.

        Args:
            key: Key to retrieve.
            default: Default value to return if the key does not exist or has expired.

        Returns:
            Value associated with the key or the default.
        """
        try:
            return self[key]
        except KeyError:
            return default

    @override
    def __delitem__(self, key: _K) -> None:
        """Delete a key from the cache.

        Args:
            key: Key to delete.

        Raises:
            KeyError: If the key does not exist.
        """
        if key in self._data:
            del self._data[key]
        else:
            raise KeyError(f"{key} does not exist")

    @override
    def __contains__(self, key: object) -> bool:
        """Check whether a key exists and has not expired.

        Args:
            key: Key to check.

        Returns:
            Whether the key exists and has not expired.
        """
        if key in self._data:
            _, timestamp = self._data[key]  # type: ignore
            if time.time() - timestamp <= self._ttl:
                return True
            del self._data[key]  # type: ignore
        return False

    @override
    def __len__(self) -> int:
        """Get the number of non-expired keys.

        Returns:
            The number of valid keys in the cache.
        """
        self._expire_all()
        return len(self._data)

    @override
    def __iter__(self) -> Iterator[_K]:
        """Return an iterator over non-expired keys.

        Returns:
            An iterable object.
        """
        self._expire_all()
        return iter(self._data)

    @override
    def __repr__(self) -> str:
        """Get a human-readable representation of the cache.

        Returns:
            String representation.
        """
        self._expire_all()
        return f"{self.__class__.__name__}({{ {', '.join(f'{k!r}: {v[0]!r}' for k, v in self._data.items())} }})"

    def _expire_all(self) -> None:
        """Internal method: remove all expired entries."""
        now = time.time()
        keys_to_remove = [
            k for k, (_, ts) in self._data.items() if now - ts > self._ttl
        ]
        for k in keys_to_remove:
            del self._data[k]
