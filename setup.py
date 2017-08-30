#!/usr/bin/env python
#
#

from distutils.core import setup
from distutils.util import get_platform
from distutils.dir_util import mkpath
from distutils.extension import Extension
from distutils.sysconfig import get_python_lib
from distutils.ccompiler import new_compiler
from distutils.command import build
from distutils.spawn import spawn
from os.path import join
import sys
import versioneer


class build_doc(build.build):
    description = "build documentation"

    def run(self):
        spawn(['make', '-C', 'doc', 'html'])

packages = [
    'data_profiler',
]

WIN32 = sys.platform == 'win32'

if WIN32:
    mkl_include_dir = join(sys.prefix, 'Library', 'include')
    mkl_library_dir = join(sys.prefix, 'Library', 'lib')
else:
    mkl_include_dir = join(sys.prefix, 'include')
    mkl_library_dir = join(sys.prefix, 'lib')


# Profile module (an augmented clone from _lsprof)
prof_module = Extension(
    name = "data_profiler.prof",
    sources = [sys.version_info.major > 2 and "data_profiler/prof.c" or "data_profiler/prof2.c",
               "data_profiler/rotatingtree.c"],
    include_dirs = [join(sys.prefix, 'include')],
    library_dirs = [join(sys.prefix, 'libs' if WIN32 else 'lib')]
)

cmdclass = versioneer.get_cmdclass()
cmdclass['build_doc'] = build_doc

package_data={}
package_data['data_profiler'] = ['snakeviz/template.jinja',
                                 'snakeviz/style.css']

ext_modules = [prof_module]

if __name__ == '__main__':
    setup(
        name='data_profiler',
        description='Data Profiler',
        author='Anaconda, Inc.',
        author_email='support@anaconda.com',
        url='https://anaconda.com',
        packages=packages,
        package_data=package_data,
        ext_modules=ext_modules,
        scripts=['scripts/profiler'],
        license='proprietary',
        version=versioneer.get_version(),
        cmdclass=cmdclass,
    )
