# 🧠 Lightweight LRU & TTL Cache for Python

A tiny, type-safe utility that provides:

- 🔁 **LRU (Least Recently Used) cache**
- ⏱️ **TTL (Time-To-Live) cache**

Fully typed with support for Python `typing`, `generics`, and `collections.abc.MutableMapping`. No external dependencies.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/Inexplicable-YL/LRU-TTLCache.git
```

---

## 🚀 Quick Start

```python
from cache import LRUCache, TTLCache  # cache.py is the file in this repo

# Create an LRU cache with max size of 3
cache = LRUCache[int, str](max_size=3)
cache[1] = "a"
cache[2] = "b"
cache[3] = "c"
cache[4] = "d"  # Evicts 1, as it is least recently used

print(cache)  # Output: {2: 'b', 3: 'c', 4: 'd'}

# Create a TTL cache where each item lives for 5 seconds
ttl_cache = TTLCache[str, int](ttl=5)
ttl_cache["a"] = 123

# After 5 seconds...
print("a" in ttl_cache)  # False (expired)
```

---

## 📚 Classes & Usage

### `LRUCache[K, V]`

Evicts the **least recently used** item when full.

```python
LRUCache(max_size=100)
```

- `__getitem__` marks the key as recently used
- Oldest items are evicted when new ones are inserted

---

### `TTLCache[K, V]`

Evicts items automatically after **`ttl` seconds**.

```python
TTLCache(ttl=60.0)
```

- Items expire after `ttl` seconds (per key)
- Auto-removal happens on access / iteration

---

## 🛠 Public Methods

Both `LRUCache` and `TTLCache` support the full `MutableMapping` interface:

| Method              | Description                           |
|---------------------|---------------------------------------|
| `__getitem__(key)`  | Get value, update recency (LRU)       |
| `__setitem__(key, value)` | Set value and timestamp          |
| `__delitem__(key)`  | Delete key                            |
| `get(key, default)` | Safe access with fallback             |
| `__contains__(key)` | Check existence (and TTL validity)    |
| `__len__()`         | Number of valid entries               |
| `__iter__()`        | Iterate over keys                     |
| `__repr__()`        | Nicely formatted string               |

---

## 🔎 Type Hints & Compatibility

- ✅ Fully supports `Generic[_K, _V]`
- ✅ Compatible with Pyright, Pylance, MyPy
- ✅ Supports Python `3.10+` (uses type union `|` and modern type hints)

---

## 🧠 Design Tips

- `LRUCache` uses `OrderedDict` internally for O(1) operations
- `TTLCache` lazily expires items on access or iteration
- For high-concurrency use cases, consider using locks or wrapping with `functools.lru_cache` for thread safety

---

## 💡 Example: Building a Function Memoizer

```python
memo = LRUCache[int, str](max_size=100)

def expensive_compute(x: int) -> str:
    if x in memo:
        return memo[x]
    result = str(x ** 2)  # simulate computation
    memo[x] = result
    return result
```
