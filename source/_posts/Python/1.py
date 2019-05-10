from memory_profiler import profile
import sys

class Stream(object):
    """A lazily computed recursive list."""
    def __init__(self, first, compute_rest, empty=False):
        self.first = first
        self._compute_rest = compute_rest
        self.empty = empty
        self._rest = None
        self._computed = False

    @property
    @profile
    def rest(self):
        """Return the rest of the stream, computing it if necessary."""
        assert not self.empty, 'Empty streams have no rest.'
        if not self._computed:
            self._rest = self._compute_rest(self.first)
            self._computed = True
        return self._rest

    def __repr__(self):
        if self.empty:
            return '<empty stream>'
        if self._rest:
            return 'Stream({0}, \n{1})'.format(repr(self.first), repr(self._rest))
        else:
            return 'Stream({0}, \n{1})'.format(repr(self.first), repr(self._compute_rest))

Stream.empty = Stream(None, None, True)


def make_next_integer(first):
    print("{} -> lazy computing -> {}".format(first, first+1))
    return Stream(first+1, make_next_integer)


def map_stream(fn, s):
    if s.empty:
        return s
    def compute_rest(first):
        return map_stream(fn, s._compute_rest(first))
    new_val = fn(s.first)
    return Stream(new_val, compute_rest)



def filter_stream(fn, s):
    if s.empty:
        return s
    def compute_rest(first):
        return filter_stream(fn, s._compute_rest(first))
    if fn(s.first):
        return Stream(s.first, compute_rest)
    else:
        return compute_rest(s.first)


def primes(pos_stream):
    def not_divible(x):
        if x % pos_stream.first != 0:
            return True
        else:
            print(x, "%", pos_stream.first, "!=0")
            return False
    def compute_rest(first):
        return primes(filter_stream(not_divible, pos_stream.rest))
    return Stream(pos_stream.first, compute_rest)


if __name__ == "__main__":
    pos = Stream(2, make_next_integer)
    p = primes(pos)
    print(p.rest)
