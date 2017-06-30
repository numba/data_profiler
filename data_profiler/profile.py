"""Python interface for the 'prof' profiler.
   Compatible with the stdlib 'profile' module.
"""

__all__ = ["run", "runctx", "Profile"]

from . import prof
import profile as _pyprofile
import inspect
import numpy
import sys

# ____________________________________________________________
# Simple interface

def _show(prof, filename, sort):
    if filename is not None:
        prof.dump_stats(filename)
    else:
        prof.print_stats(sort)

def run(statement, filename=None, sort=-1):
    prof = Profile()
    try:
        prof.run(statement)
    except SystemExit:
        pass
    finally:
        _show(prof, filename, sort)

def runctx(statement, globals, locals, filename=None, sort=-1):
    prof = Profile()
    try:
        prof.runctx(statement, globals, locals)
    except SystemExit:
        pass
    finally:
        _show(prof, filename, sort)

run.__doc__ = _pyprofile.run.__doc__
runctx.__doc__ = _pyprofile.runctx.__doc__

# ____________________________________________________________

class FunctionCall(object):
    """Stores a function name.
    Behave like a string as far as its handling by pstats is concerned."""

    def __init__(self, frame, name=None):

        self.code = c = frame.f_code
        self.filename = c.co_filename
        self.lineno = c.co_firstlineno
        self.name = name or c.co_name
        # builtin methods report as name <method '...' of '...' objects>
        # Extract their real name from that.
        if self.name.startswith('<method '):
            self.name = self.name.split("'", 3)[1]
        arg_info = inspect.getargvalues(frame)
        args=[]
        # There are cases where we can't generate a signature...
        no_signature=False
        if arg_info:
            for a in arg_info.args:
                # FIXME: There are cases where we don't know how to handle arguments.
                #        If 'a' is a list, we bail out...
                if type(a) is list:
                    no_signature=True
                    break
                else:
                    v = arg_info.locals.get(a, None)
                if type(v) == numpy.ndarray:
                    t = 'ndarray(dtype=%s, shape=%s)'%(v.dtype, v.shape)
                # cython-compiled code doesn't report a locals dict, so 'v' may be None
                elif v is None:
                    t = '<unknown>'
                else:
                    t = str(type(v).__name__)
                args.append((a, t))
        self.args = no_signature and None or tuple(args)

    def __str__(self):
        """Format function calls to include signature."""
        if self.args is None:
            return '%s(<unknown>)'%self.name
        elif len(self.args) and self.args[0][0] == 'self':
            args = self.args[1:]
            if self.name == '__init__':
                name = self.args[0][1]
            else:
                name = '%s.%s'%(self.args[0][1], self.name)
        else:
            name, args = self.name, self.args
        return '%s(%s)'%(name, ', '.join(['%s:%s'%(a[0],a[1]) for a in args]))
        
    def __hash__(self):
        """Needed for it to work as a key."""
        return hash((self.code.co_name, self.args))

    def __eq__(self, other):
        """Needed for it to work as a key."""
        return (self.name, self.args) == (other.name, other.args)

    def __lt__(self, other):
        """Needed for it to be sortable."""
        return (self.name, self.args) < (other.name,other.args)


class Profile(prof.Profiler):
    """Profile(custom_timer=None, time_unit=None, subcalls=True, builtins=True, signatures=True)

    Builds a profiler object using the specified timer function.
    The default timer is a fast built-in one based on real time.
    For custom timer functions returning integers, time_unit can
    be a float specifying a scale (i.e. how long each integer unit
    is, in seconds).
    """

    def _create_function_call(self, frame, name=None):
        return FunctionCall(frame, name)
    
    # Most of the functionality is in the base class.
    # This subclass only adds convenient and backward-compatible methods.

    def print_stats(self, sort=-1):
        """Print a table with profile statistics."""
        
        import pstats
        pstats.Stats(self).strip_dirs().sort_stats(sort).print_stats()

    def dump_stats(self, file):
        import marshal
        with open(file, 'wb') as f:
            self.create_stats()
            marshal.dump(self.stats, f)

    def create_stats(self):
        self.disable()
        self.snapshot_stats()

    def snapshot_stats(self):
        entries = self.getstats()
        self.stats = {}
        callersdicts = {}
        # call information
        for entry in entries:
            func = label(entry.code)
            nc = entry.callcount         # ncalls column of pstats (before '/')
            cc = nc - entry.reccallcount # ncalls column of pstats (after '/')
            tt = entry.inlinetime        # tottime column of pstats
            ct = entry.totaltime         # cumtime column of pstats
            callers = {}
            callersdicts[id(entry.code)] = callers
            self.stats[func] = cc, nc, tt, ct, callers
        # subcall information
        for entry in entries:
            if entry.calls:
                func = label(entry.code)
                for subentry in entry.calls:
                    try:
                        callers = callersdicts[id(subentry.code)]
                    except KeyError:
                        continue
                    nc = subentry.callcount
                    cc = nc - subentry.reccallcount
                    tt = subentry.inlinetime
                    ct = subentry.totaltime
                    if func in callers:
                        prev = callers[func]
                        nc += prev[0]
                        cc += prev[1]
                        tt += prev[2]
                        ct += prev[3]
                    callers[func] = nc, cc, tt, ct

    # The following two methods can be called by clients to use
    # a profiler to profile a statement, given as a string.

    def run(self, cmd):
        import __main__
        dict = __main__.__dict__
        return self.runctx(cmd, dict, dict)

    def runctx(self, cmd, globals, locals):
        self.enable()
        try:
            exec(cmd, globals, locals)
        finally:
            self.disable()
        return self

    # This method is more useful to profile a single function call.
    def runcall(self, func, *args, **kw):
        self.enable()
        try:
            return func(*args, **kw)
        finally:
            self.disable()

# ____________________________________________________________

def label(code):
    if isinstance(code, str):
        return ('~', 0, code)    # built-in functions ('~' sorts at the end)
    elif isinstance(code, FunctionCall):
        return (code.filename, code.lineno, str(code))
    else:
        return (code.co_filename, code.co_firstlineno, code.co_name)

# ____________________________________________________________

def main():
    import os, sys
    from optparse import OptionParser
    usage = "cProfile.py [-o output_file_path] [-s sort] scriptfile [arg] ..."
    parser = OptionParser(usage=usage)
    parser.allow_interspersed_args = False
    parser.add_option('-o', '--outfile', dest="outfile",
        help="Save stats to <outfile>", default=None)
    parser.add_option('-s', '--sort', dest="sort",
        help="Sort order when printing to stdout, based on pstats.Stats class",
        default=-1)

    if not sys.argv[1:]:
        parser.print_usage()
        sys.exit(2)

    (options, args) = parser.parse_args()
    sys.argv[:] = args

    if len(args) > 0:
        progname = args[0]
        sys.path.insert(0, os.path.dirname(progname))
        with open(progname, 'rb') as fp:
            code = compile(fp.read(), progname, 'exec')
        globs = {
            '__file__': progname,
            '__name__': '__main__',
            '__package__': None,
            '__cached__': None,
        }
        runctx(code, globs, None, options.outfile, options.sort)
    else:
        parser.print_usage()
    return parser

# When invoked as main program, invoke the profiler on a script
if __name__ == '__main__':
    main()
