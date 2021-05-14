#!/usr/bin/env python3

import itertools
import os
import os.path

def integer_partitions(n, min=1, maxsize=None):
    if n == 0:
        yield ()
        return
    if maxsize is None: maxsize = n
    if maxsize <= 0: return
    yield (n,)
    for first in range(min, n//2 + 1):
        for p in integer_partitions(n - first, first, maxsize-1):
            yield (first,) + p

assert len(list(integer_partitions(3))) == 3
assert len(list(integer_partitions(10))) == 42

def all_indices(nindices, rmin=1, rmax=1, smin=0, smax=0, dmin=0, dmax=None):
    result = []
    def ndots(indices):
        return sum(i-1 for i in indices if i > 1)
    if dmax is None: dmax = rmax - 1
    for r in range(rmin, rmax+1):
        rind = list(p for p in integer_partitions(r, maxsize=nindices) if dmin <= ndots(p) <= dmax)
        for s in range(smin, smax+1):
            sind = integer_partitions(s, maxsize=nindices)
            sind = [tuple(-i for i in p) for p in sind]
            for i1, i2 in itertools.product(rind, sind):
                nzeros = nindices - len(i1) - len(i2)
                if nzeros < 0: continue
                for indices in set(itertools.permutations(i1+i2+(0,)*nzeros)):
                    result.append(indices)
    return sorted(result)

assert len(all_indices(4, rmax=6, smax=0)) == 209
assert len(all_indices(4, rmax=5, smax=0, dmax=1)) == 47

class Problem:
    def __init__(self, external_momenta, loop_momenta, invariants, scalar_product_rules, denominators, integrals):
        def tolist(obj):
            return obj.split() if isinstance(obj, str) else obj
        self.external_momenta = tolist(external_momenta)
        self.loop_momenta = tolist(loop_momenta)
        self.invariants = invariants
        self.scalar_product_rules = scalar_product_rules
        self.denominators = denominators
        self.integrals = integrals

    @property
    def maxr(self):
        return max(
            (sum(i for i in indices if i > 0) for indices in self.integrals),
            default=0)

    @property
    def maxs(self):
        return max(
            (-sum(i for i in indices if i < 0) for indices in self.integrals),
            default=0)

    @property
    def top_sector(self):
        return sum(2**i for i in range(len(self.denominators)))

def ensure_directory(path):
    try:
        os.makedirs(path)
    except FileExistsError:
        pass

def render_template(template, **kwargs):
    """
    A templating language: wraps each line of the template in
    print(f"..."), except for lines that start with "#% " --
    those are left as they are. Runs the resulting Python code.
    """
    result = []
    indent = 0
    for line in template.splitlines():
        if line.startswith("#% "):
            line = line[3:]
            result.append(line)
            indent = len(line) - len(line.lstrip(" "))
            if line.endswith(":"): indent += 4
        else:
            line += '\n'
            result.append(f"{' '*indent}_fout.write(f{line!r})")
    body = '\n    '.join(result)
    code = f"""\
def _template_fn({", ".join(str(k) for k in kwargs.keys())}):
    import io
    _fout = io.StringIO()
    {body}
    return _fout.getvalue()
"""
    variables = {}
    exec(code, variables)
    return variables["_template_fn"](**kwargs)

def format_template_dir(srcdir, dstdir, **kwargs):
    for root, dirs, files in os.walk(srcdir):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(dstdir, os.path.relpath(src, srcdir))
            print(src, "->", dst)
            with open(src, "r") as f:
                template = f.read()
            data = render_template(template, **kwargs)
            ensure_directory(os.path.dirname(dst))
            with open(dst, "w") as f:
                f.write(data)

# one loop box with massive internal lines (same mass)
# and massless external legs
problem = Problem(
    external_momenta = "p1 p2 p3",
    loop_momenta = "l",
    invariants = {"m2": 2, "s12": 2, "s23": 2},
    scalar_product_rules = [
        ("p1", "p1", "0"),
        ("p2", "p2", "0"),
        ("p3", "p3", "0"),
        ("p1", "p2", "s12/2"),
        ("p1", "p3", "-s12/2-s23/2"),
        ("p2", "p3", "s23/2")
    ],
    denominators = [
        ("l", "m2"),
        ("l + p2", "m2"),
        ("l - p1 - p3", "m2"),
        ("l - p1", "m2")
    ],
    integrals = all_indices(4, rmax=4, smax=2, dmax=1)
)

format_template_dir("template.kira", "box1L.kira", p=problem)
format_template_dir("template.fire", "box1L.fire", p=problem)
