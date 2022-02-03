from functools import wraps
from time import time
import random

def timing(cases, capacity):
    def timing_with_cases(f):
        @wraps(f)
        def wrap(*args, **kw):
            ts = time()
            result = f(*args, **kw)
            te = time()
            cache = args[0]
            name = f'{cache.__class__.__name__:<10}(cap={capacity})'
            print(
                f'{name:<30}\ttotal puts:{cases},\tper put time (ns):{(te - ts) * 1000 * 1000 / cases:.4f},\treplacement_counter:{cache._replacement_counter},\tper replacement time (ns):{((te - ts) * 1000 * 1000 / cache._replacement_counter) if cache._replacement_counter else 0.0 :.4f}')
            return result

        return wrap

    return timing_with_cases


class SimpleCache:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._data = dict()  # key -> value
        self._replacement_counter = 0

    def put(self, key, value):
        if key in self._data:
            self._data[key] = value
        elif len(self._data) == self._capacity:
            self._replace(key, value)
        else:
            self._data[key] = value

    def get(self, key):
        return self._data[key]

    def delete(self, key):
        del self._data[key]

    def _replace(self, key, value):
        random_idx = random.randint(0, self._capacity - 1)
        random_key = list(self._data.keys())[random_idx]
        del self._data[random_key]
        self.put(key, value)
        self._replacement_counter += 1

    def __str__(self):
        return str(self._data)


class OptimizedCache(SimpleCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._data = dict()  # key -> (value, idx)
        self._available_idxes = set(range(0, capacity))  # {idx}
        self._used_idxes = dict()  # idx -> key

    def put(self, key, value):
        if key in self._data:
            self._data[key] = (value, self._data[key][0])
        else:
            if self._available_idxes:
                idx = self._available_idxes.pop()
                self._data[key] = (value, idx)
                self._used_idxes[idx] = key
            else:
                self._replace(key, value)

    def get(self, key):
        value, _ = self._data[key]
        return value

    def delete(self, key):
        _, idx = self._data[key]
        self._delete_key(key)
        self._delete_idx(idx)

    def _replace(self, key, value):
        random_idx = random.randint(0, self._capacity - 1)
        random_key = self._used_idxes[random_idx]
        self._delete_idx(random_idx)
        self._delete_key(random_key)
        self.put(key, value)
        self._replacement_counter += 1

    def _delete_idx(self, idx: int):
        del self._used_idxes[idx]
        self._available_idxes.add(idx)

    def _delete_key(self, key):
        del self._data[key]


class OptimizedCache2(SimpleCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._data = dict()  # key -> (value, idx)
        self._available_idxes = list(range(0, capacity))  # [idx3]
        self._used_idxes = [None for _ in range(capacity)]  # [key1, key2, None]

    def put(self, key, value):
        if key in self._data:
            self._data[key] = (value, self._data[key][0])
        else:
            if self._available_idxes:
                idx = self._available_idxes.pop()
                self._data[key] = (value, idx)
                self._used_idxes[idx] = key
            else:
                self._replace(key, value)

    def get(self, key):
        value, _ = self._data[key]
        return value

    def delete(self, key):
        _, idx = self._data[key]
        self._delete_key(key)
        self._delete_idx(idx)

    def _replace(self, key, value):
        random_idx = random.randint(0, self._capacity - 1)
        random_key = self._used_idxes[random_idx]
        self._delete_idx(random_idx)
        self._delete_key(random_key)
        self.put(key, value)
        self._replacement_counter += 1

    def _delete_idx(self, idx: int):
        self._used_idxes[idx] = None
        self._available_idxes.append(idx)

    def _delete_key(self, key):
        del self._data[key]


class OptimizedCache3(SimpleCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._data = [(None, None) for _ in range(capacity)]  # [(key1, value1), (key2, value2), (None, None)]
        self._available_idxes = list(range(0, capacity))  # [idx3]
        self._used_idxes = dict()  # key -> idx

    def put(self, key, value):
        if key in self._used_idxes:
            self._data[self._used_idxes[key]] = (key, value)
        else:
            if self._available_idxes:
                idx = self._available_idxes.pop()
                self._data[idx] = (key, value)
                self._used_idxes[key] = idx
            else:
                self._replace(key, value)

    def get(self, key):
        return self._data[self._used_idxes[key]][1]

    def delete(self, key):
        idx = self._used_idxes[key]
        self._delete_key(key)
        self._delete_idx(idx)

    def _replace(self, key, value):

        random_idx = random.randint(0, self._capacity - 1)
        random_key, _ = self._data[random_idx]
        self._delete_idx(random_idx)
        self._delete_key(random_key)
        self.put(key, value)
        self._replacement_counter += 1

    def _delete_idx(self, idx: int):
        self._data[idx] = (None, None)
        self._available_idxes.append(idx)

    def _delete_key(self, key):
        del self._used_idxes[key]

    def __str__(self):
        return str({k: v for k, v in self._data if k is not None})


if __name__ == '__main__':
    # correctness check:

    o = OptimizedCache3(3)
    o.put(1, 1)
    o.put(2, 2)
    o.put(3, 3)
    o.put(4, 4)
    o.put(5, 5)
    print(o)
    print(o.get(5))
    o.delete(5)
    print(o)
    # print(o._available_idxes)
    # print(o._used_idxes)
    o.put(6, 6)
    print(o)
    # print(o._available_idxes)
    # print(o._used_idxes)
    print(o.get(6))

    # performance

    capacity = 100000
    for exp_c in range(3, 6):
        capacity = 10 ** exp_c
        for exp in range(12, 20):
            cases = 2 ** exp
            simple_c = SimpleCache(capacity)
            optimized_c = OptimizedCache(capacity)
            optimized2_c = OptimizedCache2(capacity)
            optimized3_c = OptimizedCache3(capacity)


            @timing(cases, capacity)
            def ordered_inputs(c):
                for i in range(cases):
                    c.put(i, i)


            ordered_inputs(simple_c)
            ordered_inputs(optimized_c)
            ordered_inputs(optimized2_c)
            ordered_inputs(optimized3_c)

            print("-------------------------------------------------------------------------\n")
        print("\n\n\n==================================================================\n")
