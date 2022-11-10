#!/usr/bin/env python3

import itertools
import os
import os.path
import re

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

def gen_all_indices(sector, rmin, rmax, smin, smax, dmin, dmax):
    if sector == ():
        if (rmin <= 0 <= rmax) and (smin <= 0 <= smax) and (dmin <= 0 <= dmax):
            yield ()
        return
    if rmax < 0 or smax < 0 or dmax < 0: return
    indices = []
    if sector[0]:
        for i in range(1, rmax + 1):
            d = max(i - 1, 0)
            for p in gen_all_indices(sector[1:], rmin-i, rmax-i, smin, smax, dmin-d, dmax-d):
                yield (i,) + p
    for i in range(0, smax + 1):
        for p in gen_all_indices(sector[1:], rmin, rmax, smin-i, smax-i, dmin, dmax):
            yield (-i,) + p

def all_indices(sector, rmin=1, rmax=1, smin=0, smax=0, dmin=0, dmax=None):
    if dmax is None: dmax = rmax - 1
    return sorted(list(gen_all_indices(sector, rmin, rmax, smin, smax, dmin, dmax)))

assert len(all_indices((1,1,0), rmax=2, smax=1, dmax=0)) == 8
assert len(all_indices((1,1,1,1), rmax=6, smax=0)) == 209
assert len(all_indices((1,1,1,1), rmax=5, smax=0, dmax=1)) == 47

def shuffle_sector(items, sector):
    assert len(items) == len(sector)
    front = []
    back = []
    for i, s in enumerate(sector):
        (front if s else back).append(i)
    return tuple([items[i] for i in front + back])

assert shuffle_sector((11,22,33,44,55,66), (1,0,1,1,0,0)) == (11,33,44,22,55,66)
assert shuffle_sector((11,22,33,44,55), (0,1,0,1,1)) == (22,44,55,11,33)

def replace_variables(text, values):
    if values:
        pat = "|".join(f"\\b{k}\\b" for k in values.keys())
        return re.sub(pat, lambda m: f"({values[m.group()]})", text)
    else:
        return text

assert replace_variables("5*m22+11*m2+(3-lam)*m2", {"m2": "7", "lam": "1"}) == "5*m22+11*(7)+(3-(1))*(7)"

class Problem:
    def __init__(self, name, external_momenta, loop_momenta, invariants, replace_by_one, scalar_product_rules, denominators, integrals, top_sector, preferred_masters=[], threads=1, invariant_values={}):
        def tolist(obj):
            return obj.split() if isinstance(obj, str) else obj
        assert len(top_sector) == len(denominators)
        self.name = name
        self.external_momenta = tolist(external_momenta)
        self.loop_momenta = tolist(loop_momenta)
        self.invariants = {k:v for k,v in invariants.items() if k not in invariant_values}
        self.replace_by_one = replace_by_one
        self.scalar_product_rules = [
            (p1, p2, replace_variables(sp, invariant_values))
            for p1, p2, sp in scalar_product_rules
        ]
        self.denominators = [
            (replace_variables(mom, invariant_values), replace_variables(mass, invariant_values))
            for mom, mass in shuffle_sector(denominators, top_sector)
        ]
        self.top_sector = shuffle_sector(top_sector, top_sector)
        self.preferred_masters = [shuffle_sector(i, top_sector) for i in preferred_masters]
        self.integrals = sorted(set(
            [shuffle_sector(i, top_sector) for i in integrals] + self.preferred_masters
        ))
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
    def maxd(self):
        return max(
            (sum(i-1 for i in indices if i > 0) for indices in self.integrals),
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
    assert os.path.isdir(srcdir)
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

templates = [
    "kira",
    "kira-firefly",
    "kira-ratracer",
    "kira-ratracer-scan",
    "kira-ratracer-eps0",
    "kira-ratracer-eps1",
    "kira-ratracer-eps2",
    "kira-ratracer-eps0-scan",
    "kira-ratracer-eps1-scan",
    "kira-ratracer-eps2-scan",
    "fire",
    "fire-nohint"
]

# one loop box with massive internal lines (same mass)
# and massless external legs
problem = Problem(
    name = "box1l",
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
        ("l + p1", "m2"),
        ("l + p1 + p2", "m2"),
        ("l - p3", "m2")
    ],
    integrals = all_indices((1,1,1,1), rmax=10, smax=6, dmax=6),
    top_sector = (1,1,1,1),
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)

# two loop box with massive internal lines (same mass)
# and massless external legs
problem = Problem(
    name = "box2l",
    external_momenta = "p1 p2 p3",
    loop_momenta = "l1 l2",
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
        ("l1", "m2"),
        ("l2", "m2"),
        ("l1 - l2", "m2"),
        ("l1 + p1", "m2"),
        ("l1 + p1 + p2", "m2"),
        ("l2 + p1 + p2", "m2"),
        ("l2 - p3", "m2"),
        ("l2 + p1", "0"),
        ("l1 - p3", "0")
    ],
    integrals = all_indices((1,1,1,1,1,1,1,0,0), rmax=9, smax=2, dmax=2),
    top_sector = (1,1,1,1,1,1,1,0,0),
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)

# two loop massive diamond topology
problem = Problem(
    name = "diamond2l",
    external_momenta = "q",
    loop_momenta = "l1 l2",
    invariants = {"s": 2, "ma2": 2, "mb2": 2},
    replace_by_one = "s",
    scalar_product_rules = [
        ("q", "q", "s")
    ],
    denominators = [
        ("l1 - l2", "0"),
        ("l1", "ma2"),
        ("l2", "ma2"),
        ("l1 + q", "mb2"),
        ("l2 + q", "mb2")
    ],
    integrals = all_indices((1,1,1,1,1), rmax=8, smax=3, dmax=3),
    top_sector = (1,1,1,1,1),
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)

# three loop massive diamond topology
problem = Problem(
    name = "diamond3l",
    external_momenta = "q",
    loop_momenta = "l1 l2 l3",
    invariants = {"s": 2, "ma2": 2, "mb2": 2},
    replace_by_one = "s",
    scalar_product_rules = [
        ("q", "q", "s")
    ],
    denominators = [
        ("l1 - l2", "0"),
        ("l2 - l3", "0"),
        ("l1", "ma2"),
        ("l2", "ma2"),
        ("l3", "ma2"),
        ("l1 + q", "mb2"),
        ("l2 + q", "mb2"),
        ("l3 + q", "mb2"),
        ("l1 - l3", "0")
    ],
    integrals = all_indices((1,1,1,1,1,1,1,1,0), rmax=10, smax=2, dmax=1),
    top_sector = (1,1,1,1,1,1,1,1,0),
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)

# pentabubble, qq->ttH b16
problem = Problem(
    name = "tth2l_b16",
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
    integrals = all_indices((1,0,1,1,1,0,1,1,0,0,0), rmax=7, smax=1, dmax=1),
    top_sector = (1,0,1,1,1,0,1,1,0,0,0),
    # d-factorizing basis
    preferred_masters = [
        (0,0,0,1,0,0,1,1,0,0,0),
        (0,0,0,1,1,0,0,0,0,0,0),
        (0,0,0,1,1,0,0,1,0,0,0),
        (0,0,0,1,1,0,1,0,0,0,0),
        (0,0,0,1,1,0,1,1,0,0,0),
        (0,0,0,1,1,0,2,0,0,0,0),
        (0,0,0,1,1,0,2,1,0,0,0),
        (0,0,0,1,2,0,1,1,0,0,0),
        (0,0,1,1,0,0,0,1,0,0,0),
        (0,0,1,1,0,0,1,0,0,0,0),
        (0,0,1,1,0,0,1,1,0,0,0),
        (0,0,1,1,0,0,1,2,0,0,0),
        (0,0,1,1,0,0,2,0,0,0,0),
        (0,0,1,1,0,0,2,1,0,0,0),
        (0,0,1,1,1,0,0,1,0,0,0),
        (0,0,1,1,1,0,1,0,0,0,0),
        (0,0,1,1,1,0,1,1,0,0,0),
        (0,0,1,1,1,0,1,2,0,0,0),
        (0,0,1,1,1,0,2,0,0,0,0),
        (0,0,1,1,1,0,2,1,0,0,0),
        (1,0,0,1,0,0,0,1,0,0,0),
        (1,0,0,1,0,0,1,1,0,0,0),
        (1,0,0,1,0,0,1,2,0,0,0),
        (1,0,0,1,1,0,0,0,0,0,0),
        (1,0,0,1,1,0,0,1,0,0,0),
        (1,0,0,1,1,0,1,0,0,0,0),
        (1,0,0,1,1,0,1,1,0,0,0),
        (1,0,0,1,1,0,1,2,0,0,0),
        (1,0,0,1,1,0,2,0,0,0,0),
        (1,0,0,1,1,0,2,1,0,0,0),
        (1,0,1,1,0,0,1,1,0,0,0),
        (1,0,1,1,0,0,1,2,0,0,0),
        (1,0,1,1,1,0,0,1,0,0,0),
        (1,0,1,1,1,0,1,0,0,0,0),
        (1,0,1,1,1,0,1,1,0,0,0),
        (1,0,1,1,1,0,1,2,0,0,0),
        (1,0,1,1,1,0,2,0,0,0,0),
        (1,0,1,1,1,0,2,1,0,0,0)
    ],
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)

# qq->ttH b25, hexatriangle
problem = Problem(
    name = "tth2l_b25",
    external_momenta = "q1 q2 p1 p2",
    loop_momenta = "l1 l2",
    invariants = {"mt2": 2, "mh2": 2, "x12": 2, "x23": 2, "x35": 2, "x41": 2, "x54": 2, "lam": 0},
    invariant_values = {
        "mh2": "mt2*12/23",
        "x12": "mt2*(397/45)",
        "x23": "mt2*(-79/24+2897/2856*lam)",
        "x35": "mt2*(149/60)",
        "x54": "mt2*(768/329)",
        "x41": "mt2*(-306/79+4003/3950*lam)"
    },
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
        ("l1 - p1 - p2", "0"),
        ("l1 - q1", "0"),
        ("l1 - q1 - q2", "0"),
        ("l2", "mt2"),
        ("l1 - p1", "mt2"),
        ("l1 + l2 - p1 - p2", "mt2"),
        ("l1 + l2 - q1 - q2", "mt2"),
        ("l2 - q1", "0"),
        ("l2 - q2", "0"),
        ("l2 - p1", "0"),
    ],
    integrals = all_indices((1,1,1,1,1,1,1,1,0,0,0), rmax=9, smax=1, dmax=1),
    # d-factorizing basis
    preferred_masters = [
        (0,0,0,0,1,0,1,1,0,0,0),
        (0,0,0,0,1,1,0,0,0,0,0),
        (0,0,0,0,1,1,0,1,0,0,0),
        (0,0,0,0,1,1,0,2,0,0,0),
        (0,0,0,0,1,1,1,0,0,0,0),
        (0,0,0,0,1,1,1,1,0,0,0),
        (0,0,0,0,1,1,1,2,0,0,0),
        (0,0,0,0,1,1,2,1,0,0,0),
        (0,0,0,1,0,1,1,1,0,0,0),
        (0,0,0,1,1,0,1,0,0,0,0),
        (0,0,0,1,1,0,2,0,0,0,0),
        (0,0,0,1,1,1,0,0,0,0,0),
        (0,0,0,1,1,1,1,0,0,0,0),
        (0,0,0,1,1,1,1,1,0,0,0),
        (0,0,0,1,1,1,1,2,0,0,0),
        (0,0,0,1,1,1,2,0,0,0,0),
        (0,0,0,1,1,1,2,1,0,0,0),
        (0,0,0,1,1,2,1,0,0,0,0),
        (0,0,1,0,0,1,1,1,0,0,0),
        (0,0,1,0,1,0,1,0,0,0,0),
        (0,0,1,0,1,0,1,1,0,0,0),
        (0,0,1,0,1,0,1,2,0,0,0),
        (0,0,1,0,1,0,2,0,0,0,0),
        (0,0,1,0,1,0,2,1,0,0,0),
        (0,0,1,0,1,1,0,0,0,0,0),
        (0,0,1,0,1,1,0,1,0,0,0),
        (0,0,1,0,1,1,0,2,0,0,0),
        (0,0,1,0,1,1,1,0,0,0,0),
        (0,0,1,0,1,1,1,1,0,0,0),
        (0,0,1,0,1,1,1,2,0,0,0),
        (0,0,1,0,1,1,1,3,0,0,0),
        (0,0,1,0,1,1,2,0,0,0,0),
        (0,0,1,0,1,1,2,1,0,0,0),
        (0,0,1,0,1,1,2,2,0,0,0),
        (0,0,1,0,1,2,1,0,0,0,0),
        (0,0,1,0,1,2,1,1,0,0,0),
        (0,0,1,0,2,1,1,1,0,0,0),
        (0,0,1,1,1,1,1,0,0,0,0),
        (0,0,1,1,1,1,1,1,0,0,0),
        (0,0,1,1,1,1,2,0,0,0,0),
        (0,0,1,1,1,1,2,1,0,0,0),
        (0,0,2,0,1,1,1,1,0,0,0),
        (0,1,0,0,1,1,0,1,0,0,0),
        (0,1,0,0,1,1,0,2,0,0,0),
        (0,1,0,1,0,0,1,1,0,0,0),
        (0,1,0,1,0,1,1,1,0,0,0),
        (0,1,0,1,1,0,0,0,0,0,0),
        (0,1,0,1,1,0,1,1,0,0,0),
        (0,1,0,1,1,1,0,0,0,0,0),
        (0,1,0,1,1,1,1,1,0,0,0),
        (0,1,1,0,0,0,1,1,0,0,0),
        (0,1,1,0,0,1,1,1,0,0,0),
        (0,1,1,0,1,0,0,0,0,0,0),
        (0,1,1,0,1,0,0,1,0,0,0),
        (0,1,1,0,1,0,0,2,0,0,0),
        (0,1,1,0,1,0,1,1,0,0,0),
        (0,1,1,0,1,0,1,2,0,0,0),
        (0,1,1,0,1,0,2,1,0,0,0),
        (0,1,1,0,1,1,0,0,0,0,0),
        (0,1,1,0,1,1,0,1,0,0,0),
        (0,1,1,0,1,1,0,2,0,0,0),
        (0,1,1,0,1,1,1,1,0,0,0),
        (0,1,1,0,1,1,1,2,0,0,0),
        (0,1,1,0,1,1,2,1,0,0,0),
        (0,1,1,0,1,2,0,1,0,0,0),
        (0,1,1,1,0,1,1,1,0,0,0),
        (0,1,1,1,1,1,0,0,0,0,0),
        (0,1,1,1,1,1,1,1,0,0,0),
        (1,0,0,0,1,0,0,1,0,0,0),
        (1,0,0,0,1,0,0,2,0,0,0),
        (1,0,0,0,1,0,1,0,0,0,0),
        (1,0,0,0,1,0,1,1,0,0,0),
        (1,0,0,0,1,0,1,2,0,0,0),
        (1,0,0,0,1,0,2,0,0,0,0),
        (1,0,0,0,1,0,2,1,0,0,0),
        (1,0,0,0,1,1,0,1,0,0,0),
        (1,0,0,0,1,1,0,2,0,0,0),
        (1,0,0,0,1,1,1,0,0,0,0),
        (1,0,0,0,1,1,1,1,0,0,0),
        (1,0,0,0,1,1,1,2,0,0,0),
        (1,0,0,0,1,1,1,3,0,0,0),
        (1,0,0,0,1,1,2,0,0,0,0),
        (1,0,0,0,1,1,2,1,0,0,0),
        (1,0,0,0,1,2,1,1,0,0,0),
        (1,0,0,0,2,1,1,1,0,0,0),
        (1,0,0,1,0,0,1,1,0,0,0),
        (1,0,0,1,0,1,1,1,0,0,0),
        (1,0,0,1,1,0,0,0,0,0,0),
        (1,0,0,1,1,0,1,0,0,0,0),
        (1,0,0,1,1,0,1,1,0,0,0),
        (1,0,0,1,1,0,1,2,0,0,0),
        (1,0,0,1,1,0,2,0,0,0,0),
        (1,0,0,1,1,0,2,1,0,0,0),
        (1,0,0,1,1,1,0,0,0,0,0),
        (1,0,0,1,1,1,1,0,0,0,0),
        (1,0,0,1,1,1,1,1,0,0,0),
        (1,0,0,1,1,1,1,2,0,0,0),
        (1,0,0,1,1,1,2,0,0,0,0),
        (1,0,0,1,1,1,2,1,0,0,0),
        (1,0,0,1,1,2,1,0,0,0,0),
        (1,0,0,2,1,0,1,0,0,0,0),
        (1,0,1,0,1,0,1,1,0,0,0),
        (1,0,1,0,1,0,1,2,0,0,0),
        (1,0,1,0,1,1,0,1,0,0,0),
        (1,0,1,0,1,1,0,2,0,0,0),
        (1,0,1,0,1,1,1,0,0,0,0),
        (1,0,1,0,1,1,1,1,0,0,0),
        (1,0,1,0,1,1,1,2,0,0,0),
        (1,0,1,0,1,1,2,0,0,0,0),
        (1,0,1,0,1,1,2,1,0,0,0),
        (1,0,1,0,1,2,1,1,0,0,0),
        (1,0,1,0,2,0,1,1,0,0,0),
        (1,0,1,0,2,1,1,1,0,0,0),
        (1,0,1,1,0,1,1,1,0,0,0),
        (1,0,1,1,1,0,1,0,0,0,0),
        (1,0,1,1,1,0,1,1,0,0,0),
        (1,0,1,1,1,0,2,0,0,0,0),
        (1,0,1,1,1,0,2,1,0,0,0),
        (1,0,1,1,1,1,0,0,0,0,0),
        (1,0,1,1,1,1,1,0,0,0,0),
        (1,0,1,1,1,1,1,1,0,0,0),
        (1,0,1,1,1,1,1,2,0,0,0),
        (1,0,1,1,1,1,2,0,0,0,0),
        (1,0,1,1,1,1,2,1,0,0,0),
        (1,0,1,1,1,2,1,0,0,0,0),
        (1,0,2,0,1,1,1,1,0,0,0),
        (1,1,0,0,0,0,1,1,0,0,0),
        (1,1,0,0,0,1,1,1,0,0,0),
        (1,1,0,0,1,0,0,0,0,0,0),
        (1,1,0,0,1,0,0,1,0,0,0),
        (1,1,0,0,1,0,0,2,0,0,0),
        (1,1,0,0,1,0,1,1,0,0,0),
        (1,1,0,0,1,0,1,2,0,0,0),
        (1,1,0,0,1,0,2,1,0,0,0),
        (1,1,0,0,1,1,0,0,0,0,0),
        (1,1,0,0,1,1,0,1,0,0,0),
        (1,1,0,0,1,1,0,2,0,0,0),
        (1,1,0,0,1,1,1,1,0,0,0),
        (1,1,0,0,1,1,1,2,0,0,0),
        (1,1,0,0,1,1,2,1,0,0,0),
        (1,1,0,0,1,2,0,1,0,0,0),
        (1,1,0,1,0,0,1,1,0,0,0),
        (1,1,0,1,0,1,1,1,0,0,0),
        (1,1,0,1,1,0,0,0,0,0,0),
        (1,1,0,1,1,0,1,1,0,0,0),
        (1,1,0,1,1,1,0,0,0,0,0),
        (1,1,0,1,1,1,1,1,0,0,0),
        (1,1,1,0,0,1,1,1,0,0,0),
        (1,1,1,0,1,0,0,1,0,0,0),
        (1,1,1,0,1,0,0,2,0,0,0),
        (1,1,1,0,1,0,1,1,0,0,0),
        (1,1,1,0,1,0,1,2,0,0,0),
        (1,1,1,0,1,1,0,0,0,0,0),
        (1,1,1,0,1,1,0,1,0,0,0),
        (1,1,1,0,1,1,0,2,0,0,0),
        (1,1,1,0,1,1,1,1,0,0,0),
        (1,1,1,0,1,1,1,2,0,0,0),
        (1,1,1,0,1,1,2,1,0,0,0),
        (1,1,1,0,1,2,0,1,0,0,0),
        (1,1,1,1,0,0,1,1,0,0,0),
        (1,1,1,1,0,1,1,1,0,0,0),
        (1,1,1,1,1,0,0,0,0,0,0),
        (1,1,1,1,1,0,1,1,0,0,0),
        (1,1,1,1,1,1,0,0,0,0,0),
        (1,1,1,1,1,1,1,1,0,0,0),
        (1,2,0,0,1,0,0,1,0,0,0),
        (2,0,0,0,1,1,1,1,0,0,0),
        (2,0,1,0,1,1,1,1,0,0,0)
    ],
    top_sector = (1,1,1,1,1,1,1,1,0,0,0),
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)

# non-planar double-box with two masses, qq->tb
# "topo5" from Kira
problem = Problem(
    name = "xbox2l2m",
    external_momenta = "p1 p2 q2",
    loop_momenta = "l1 l2",
    invariants = {"s": 2, "t": 2, "ma2": 2, "mb2": 2},
    replace_by_one = "ma2",
    scalar_product_rules = [
        ("p1", "p1", "0"),
        ("p1", "p2", "s/2"),
        ("p1", "q2", "-t/2"),
        ("p2", "p2", "0"),
        ("p2", "q2", "-ma2/2 + s/2 + t/2"),
        ("q2", "q2", "0")
    ],
    denominators = [
        ("l1", "0"),
        ("l2", "0"),
        ("q2-l1", "0"),
        ("p1-l2", "0"),
        ("p1+p2-q2+l1", "ma2"),
        ("p1+p2-q2+l1-l2", "ma2"),
        ("p1-q2+l1-l2", "mb2"),
        ("l1-p1", "0"),
        ("l2-q2-p2", "0")
    ],
    integrals = all_indices((1,1,1,1,1,1,1,0,0), rmax=7, smax=2, dmax=0),
    top_sector = (1,1,1,1,1,1,1,0,0),
    # Kira basis
    preferred_masters = (
        (1,1,0,0,0,1,0,0,0),
        (0,1,1,0,0,1,0,0,0),
        (-1,1,1,0,0,1,0,0,0),
        (1,0,0,1,0,1,0,0,0),
        (1,-1,0,1,0,1,0,0,0),
        (0,0,1,1,0,1,0,0,0),
        (1,1,1,1,0,1,0,0,0),
        (1,1,1,1,-1,1,0,0,0),
        (0,0,0,0,1,1,0,0,0),
        (0,0,1,0,1,1,0,0,0),
        (1,0,0,1,1,1,0,0,0),
        (1,-1,0,1,1,1,0,0,0),
        (0,0,1,1,1,1,0,0,0),
        (-1,0,1,1,1,1,0,0,0),
        (1,0,1,1,1,1,0,0,0),
        (1,-1,1,1,1,1,0,0,0),
        (1,1,0,0,0,0,1,0,0),
        (1,1,-1,0,0,0,1,0,0),
        (0,1,1,0,0,0,1,0,0),
        (1,1,1,1,0,0,1,0,0),
        (0,0,0,0,1,0,1,0,0),
        (0,1,0,0,1,0,1,0,0),
        (1,1,0,0,1,0,1,0,0),
        (1,1,-1,0,1,0,1,0,0),
        (0,0,1,0,1,0,1,0,0),
        (0,1,1,0,1,0,1,0,0),
        (-1,1,1,0,1,0,1,0,0),
        (1,1,1,0,1,0,1,0,0),
        (1,1,1,-1,1,0,1,0,0),
        (0,0,0,1,1,0,1,0,0),
        (-1,0,0,1,1,0,1,0,0),
        (0,-1,0,1,1,0,1,0,0),
        (1,0,0,1,1,0,1,0,0),
        (1,1,0,1,1,0,1,0,0),
        (1,1,-1,1,1,0,1,0,0),
        (1,1,0,1,1,-1,1,0,0),
        (0,1,1,1,1,0,1,0,0),
        (1,1,0,0,0,1,1,0,0),
        (0,1,1,0,0,1,1,0,0),
        (1,1,1,0,0,1,1,0,0),
        (1,1,1,-1,0,1,1,0,0),
        (1,0,0,1,0,1,1,0,0),
        (1,1,0,1,0,1,1,0,0),
        (1,1,-1,1,0,1,1,0,0),
        (1,0,1,1,0,1,1,0,0),
        (0,1,1,1,0,1,1,0,0),
        (1,1,1,1,0,1,1,0,0),
        (1,1,1,1,-1,1,1,0,0),
        (1,1,0,0,1,1,1,0,0),
        (1,1,-1,0,1,1,1,0,0),
        (0,1,1,0,1,1,1,0,0),
        (-1,1,1,0,1,1,1,0,0),
        (0,1,1,-1,1,1,1,0,0),
        (1,1,1,0,1,1,1,0,0),
        (1,1,1,-1,1,1,1,0,0),
        (0,0,0,1,1,1,1,0,0),
        (-1,0,0,1,1,1,1,0,0),
        (1,0,0,1,1,1,1,0,0),
        (1,-1,0,1,1,1,1,0,0),
        (1,0,-1,1,1,1,1,0,0),
        (1,0,0,1,1,1,1,-1,0),
        (1,0,0,1,1,1,1,0,-1),
        (1,1,0,1,1,1,1,0,0),
        (1,1,-1,1,1,1,1,0,0),
        (1,1,0,1,1,1,1,-1,0),
        (1,1,0,1,1,1,1,0,-1),
        (0,0,1,1,1,1,1,0,0),
        (-1,0,1,1,1,1,1,0,0),
        (0,-1,1,1,1,1,1,0,0),
        (1,0,1,1,1,1,1,0,0),
        (1,-1,1,1,1,1,1,0,0),
        (0,1,1,1,1,1,1,0,0),
        (1,1,1,1,1,1,1,0,0),
        (1,1,1,1,1,1,1,-1,0),
        (1,1,1,1,1,1,1,0,-1),
        (1,1,1,1,1,1,1,-1,-1)
    ),
    threads = 8
)

for t in templates:
    format_template_dir(f"template.{t}", f"problems/{problem.name}.{t}", p=problem)
