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

def indices_in_sector(indices, sector):
    result = []
    for idx in indices:
        r = []
        i = 0
        for s in sector:
            if s:
                r.append(idx[i])
                i += 1
            else:
                r.append(0)
        result.append(tuple(r))
    return result

assert indices_in_sector([(1,2), (11,22)], (1,0,1,0)) == [(1,0,2,0), (11,0,22,0)]

def all_indices(nindices, rmin=1, rmax=1, smin=0, smax=0, dmin=0, dmax=None, sector=None):
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
    if sector:
        assert(sum(bool(s) for s in sector) == nindices)
        result = indices_in_sector(result, sector)
    return sorted(result)

assert len(all_indices(4, rmax=6, smax=0)) == 209
assert len(all_indices(4, rmax=5, smax=0, dmax=1)) == 47

class Problem:
    def __init__(self, external_momenta, loop_momenta, invariants, replace_by_one, scalar_product_rules, denominators, integrals, top_sector, preferred_masters=[], threads=1):
        def tolist(obj):
            return obj.split() if isinstance(obj, str) else obj
        assert len(top_sector) == len(denominators)
        self.external_momenta = tolist(external_momenta)
        self.loop_momenta = tolist(loop_momenta)
        self.invariants = invariants
        self.replace_by_one = replace_by_one
        self.scalar_product_rules = scalar_product_rules
        self.denominators = denominators
        self.integrals = integrals
        self.top_sector = top_sector
        self.preferred_masters = preferred_masters
        self.threads = threads

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
    def top_sector_id(self):
        return sum(2**i for i in range(len(self.denominators)))

    @property
    def top_sector_first(self):
        i = 0
        while i < len(self.top_sector) and not self.top_sector[i]: i+= 1
        return i

    @property
    def top_sector_last(self):
        i = len(self.top_sector) - 1
        while i >= 0 and not self.top_sector[i]: i-= 1
        return i

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
            os.chmod(dst, os.stat(src).st_mode)

# one loop box with massive internal lines (same mass)
# and massless external legs
problem = Problem(
    external_momenta = "p1 p2 p3",
    loop_momenta = "l",
    invariants = {"m2": 2, "s12": 2, "s23": 2},
    replace_by_one = "m2",
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
    integrals = all_indices(4, rmax=10, smax=5, dmax=5),
    top_sector = (1,1,1,1),
    threads = 16
)

format_template_dir("template.kira", "box1L.kira", p=problem)
format_template_dir("template.kira-firefly", "box1L.kira-firefly", p=problem)
format_template_dir("template.fire", "box1L.fire", p=problem)
format_template_dir("template.fire-nohint", "box1L.fire-nohint", p=problem)

# ttH b16
extraintegrals = [
    (-1,0,0,1,1,0,1,1,0,0,0),  (-1,0,1,1,0,0,1,0,0,0,0),
    (-1,0,1,1,0,0,1,1,0,0,0),  (-1,0,1,1,1,0,1,0,0,0,0),
    (-1,0,1,1,1,0,1,1,0,0,0),  (0,0,0,0,0,0,1,1,0,0,0),
    (0,0,0,0,1,0,1,1,0,0,0),   (0,0,0,1,0,0,1,1,0,0,0),
    (0,0,0,1,1,0,0,0,0,0,0),   (0,0,0,1,1,0,0,1,0,0,0),
    (0,0,0,1,1,0,1,0,0,0,0),   (0,0,0,1,1,0,1,1,0,0,0),
    (0,0,0,1,1,0,1,2,0,0,0),   (0,0,0,1,1,0,2,0,0,0,0),
    (0,0,0,1,1,0,2,1,0,0,0),   (0,0,1,0,0,0,1,1,0,0,0),
    (0,0,1,0,1,0,1,1,0,0,0),   (0,0,1,1,0,0,0,1,0,0,0),
    (0,0,1,1,0,0,1,0,0,0,0),   (0,0,1,1,0,0,1,1,0,0,0),
    (0,0,1,1,0,0,1,2,0,0,0),   (0,0,1,1,0,0,2,0,0,0,0),
    (0,0,1,1,0,0,2,1,0,0,0),   (0,0,1,1,1,0,0,1,0,0,0),
    (0,0,1,1,1,0,1,0,0,0,0),   (0,0,1,1,1,0,1,1,0,0,0),
    (0,0,1,1,1,0,1,2,0,0,0),   (0,0,1,1,1,0,2,0,0,0,0),
    (0,0,1,1,1,0,2,1,0,0,0),   (1,-1,0,1,0,0,1,1,0,0,0),
    (1,-1,0,1,1,0,1,0,0,0,0),  (1,-1,0,1,1,0,1,1,0,0,0),
    (1,-1,1,1,0,0,1,1,0,0,0),  (1,-1,1,1,1,0,1,0,0,0,0),
    (1,-1,1,1,1,0,1,1,0,0,0),  (1,0,0,0,0,0,1,1,0,0,0),
    (1,0,0,0,1,0,1,0,0,0,0),   (1,0,0,0,1,0,1,1,0,0,0),
    (1,0,0,1,0,0,0,1,0,0,0),   (1,0,0,1,0,0,1,1,0,0,0),
    (1,0,0,1,0,0,1,2,0,0,0),   (1,0,0,1,1,0,0,0,0,0,0),
    (1,0,0,1,1,0,0,1,0,0,0),   (1,0,0,1,1,0,1,0,0,0,0),
    (1,0,0,1,1,0,1,1,0,0,0),   (1,0,0,1,1,0,1,2,0,0,0),
    (1,0,0,1,1,0,2,0,0,0,0),   (1,0,0,1,1,0,2,1,0,0,0),
    (1,0,1,0,1,0,1,1,0,0,0),   (1,0,1,1,0,0,1,1,0,0,0),
    (1,0,1,1,0,0,1,2,0,0,0),   (1,0,1,1,1,0,0,1,0,0,0),
    (1,0,1,1,1,0,1,0,0,0,0),   (1,0,1,1,1,0,1,1,0,0,0),
    (1,0,1,1,1,0,1,2,0,0,0),   (1,0,1,1,1,0,2,0,0,0,0),
    (1,0,1,1,1,0,2,1,0,0,0)
]

problem = Problem(
    external_momenta = "q1 q2 p1 p2",
    loop_momenta = "l1 l2",
    invariants = {"mt2": 2, "mh2": 2, "x12": 2, "x23": 2, "x35": 2, "x41": 2, "x54": 2},
    replace_by_one = "mt2",
    scalar_product_rules = [
        ("p1", "p1", "mt2"),
        ("p1", "p2", "mh2/2 - mt2 + x12/2 - x35/2 - x54/2"),
        ("p1", "q1", "x12/2 + x23/2 - x54/2"),
        ("p1", "q2", "-x23/2"),
        ("p2", "p2", "mt2"),
        ("p2", "q1", "-x41/2"),
        ("p2", "q2", "x12/2 - x35/2 + x41/2"),
        ("q1", "q1", "0"),
        ("q1", "q2", "x12/2"),
        ("q2", "q2", "0")
    ],
    denominators = [
        ("l1", "0"),
        ("l2 - p1", "0"),
        ("l1 - q1", "0"),
        ("l2", "mt2"),
        ("l1 + p2 - q1", "mt2"),
        ("l2 - q2", "mt2"),
        ("l1 - l2 + q2", "mt2"),
        ("l1 - p1 + q2", "mt2"),
        ("l1 + q2", "0"),
        ("l2 + q1", "0"),
        ("l2 + p2", "0")
    ],
    integrals = extraintegrals + all_indices(6, rmax=7, smax=1, dmax=1, sector=(1,0,1,1,1,0,1,1,0,0,0)),
    top_sector = (1,0,1,1,1,0,1,1,0,0,0),
    threads = 16
)

format_template_dir("template.kira", "tth_b16.kira", p=problem)
format_template_dir("template.kira-firefly", "tth_b16.kira-firefly", p=problem)
format_template_dir("template.fire", "tth_b16.fire", p=problem)
format_template_dir("template.fire-nohint", "tth_b16.fire-nohint", p=problem)
