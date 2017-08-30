# data\_profiler

The data\_profiler module extends the standard CPython profiler by recording
the functions' signatures. For NumPy array types this includes
the ``dtype`` attribute and the array's shape.

It also adds functionality to visualise the augmented profile table in
snakeviz.

This module is a direct port of `Accelerate.profiler` available in [Anaconda
Accelerate](https://docs.continuum.io/accelerate/profiling).

Documentation is located [here](http://data-profiler.readthedocs.io/en/latest/)

## Installing

The easiest way to install data\_profiler and get updates is by using the
[Anaconda Distribution](https://www.anaconda.com/download)

```
#> conda install data_profiler
```

To compile, test and run from source, it is recommended to create a conda
environment containing the following:

 * numpy
 * numba >=0.26.0
 * snakeviz
 * jupyter
 * pytest

for instructions on how to do this see the [conda](https://conda.io/docs/)
documentation, specifically the section on [managing
environments](https://conda.io/docs/using/envs.html#managing-environments).

Once a suitable environment is activated, installation achieved simply by
running:

```
#> python setup.py install
```

and the installation can be tested with:

```
#> pytest
```

## Documentation

Documentation is located [here](http://data-profiler.readthedocs.io/en/latest/).

### Building Documentation

It is also possible to build a local copy of the documentation from source.
This requires GNU Make and sphinx (available via conda).


Documentation is stored in the `doc` folder, and should be built with:

```
#> make SPHINXOPTS=-Wn clean html
```

This ensures that the documentation renders without errors. If errors occur,
they can all be seen at once by building with:

```
#> make SPHINXOPTS=-n clean html
```

However, these errors should all be fixed so that building with `-Wn` is
possible prior to merging any documentation changes or updates.

## Continuous Integration
Continuous integration is provided by [Travis CI](https://travis-ci.org/), the
current build state is available [here](LINK_TO_TRAVIS_BUILD).
