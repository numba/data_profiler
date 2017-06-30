import numpy
import pytest
from numba import jit
from data_profiler import profile, pstats

def dot(a, b):
    sum=0
    for i in range(len(a)):
        sum += a[i]*b[i]
    return sum


class TestProfiler:

    def test_dot(self):

        a = numpy.arange(16, dtype=numpy.float32)
        b = numpy.arange(16, dtype=numpy.float32)
        p = profile.Profile()
        p.enable()
        dot(a, b)
        p.disable()
        stats = pstats.Stats(p).strip_dirs()
        shp = str(a.shape)
        expected = ('test_profiler.py',
                    6,
                    'dot(a:ndarray(dtype=float32, shape={s}), '.format(s=shp)+
                    'b:ndarray(dtype=float32, shape={s}))'.format(s=shp)
                    )
        assert expected in stats.stats

    def test_no_signatures(self):

        a = numpy.arange(16, dtype=numpy.float32)
        b = numpy.arange(16, dtype=numpy.float32)
        p = profile.Profile(signatures=False)
        p.enable()
        dot(a, b)
        p.disable()
        stats = pstats.Stats(p).strip_dirs()
        assert ('test_profiler.py', 6, 'dot') in stats.stats

    def test_jit(self):

        a = numpy.arange(16, dtype=numpy.float32)
        b = numpy.arange(16, dtype=numpy.float32)
        p = profile.Profile()
        cfunc = jit(nopython=True)(dot)
        p.enable()
        cfunc(a, b)
        p.disable()
        stats = pstats.Stats(p).strip_dirs()
        shp = str(a.shape)
        expected = ('test_profiler.py',
                    6,
                    'dot(a:ndarray(dtype=float32, shape={s}), '.format(s=shp)+
                    'b:ndarray(dtype=float32, shape={s}))'.format(s=shp)
                    )
        assert expected in stats.stats

    def test_runctx(self):

        a = numpy.arange(16, dtype=numpy.float32)
        b = numpy.arange(16, dtype=numpy.float32)
        p = profile.Profile(signatures=False)
        p.runctx('dot(a, b)', globals(), locals())
        stats = pstats.Stats(p).strip_dirs()
        assert ('test_profiler.py', 6, 'dot') in stats.stats

