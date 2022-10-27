#!/usr/bin/env python3

import glob
import json
import os
import re
import subprocess
import time

def fmt_amount(amount, units):
    sym, value = units[-1]
    for s, v in units:
        if amount <= v*0.95: break
        sym, value = s, v
    amount = amount/value
    if amount >= 100:
        return f"{amount:.0f}{sym}"
    else:
        return f"{amount:.1f}{sym}"

def fmt_time(seconds):
    return fmt_amount(seconds, (
        (" us", 1e-6), (" ms", 1e-3), (" s", 1)#, ("m", 60), ("h", 60*60), ("d", 24*60*60)
    ))

def fmt_bytes(seconds):
    return fmt_amount(seconds, (
        (" B", 1),
        (" kB", 1024),
        (" MB", 1024**2),
        (" GB", 1024**3)
    ))

def fmt_units(n):
    return fmt_amount(n, (
        ("", 1),
        (" 10^1", 10**1),
        (" 10^2", 10**2),
        (" 10^3", 10**3),
        (" 10^4", 10**4),
        (" 10^5", 10**5),
        (" 10^6", 10**6),
        (" 10^7", 10**7),
        (" 10^8", 10**8),
        (" 10^9", 10**9),
    ))

table = []
now = time.time()
for statfn in glob.glob("problems/*/comon.json"):
    logfn = statfn.replace("/comon.json", "/log")
    if not os.path.exists(logfn): continue
    ok = os.path.exists(statfn.replace("/comon.json", "/ibp-tables.m"))
    m = re.fullmatch(r"problems/([^.]*)\.([^.]*)/comon.json", statfn)
    problem = m.group(1)
    method = m.group(2)
    with open(logfn, "r") as f:
        log = f.read()
    m = re.search(r"Completed reconstruction in ([0-9.e+-]*) s \| ([0-9]*) probes", log)
    if m is not None:
        firefly_time = float(m.group(1))
        firefly_probes = float(m.group(2))
    else:
        firefly_time = None
        firefly_probes = None
    proberuns = []
    for m in re.finditer(r"Completed current prime field in [^\n]* \| ([0-9]*) probes in total\n[^\n]*probe: ([0-9.e+-]*) s", log):
        proberuns.append((float(m.group(1)), float(m.group(2))))
    if proberuns:
        firefly_probetime = sorted(proberuns)[-1][1]
    else:
        firefly_probetime = None
    m = re.search(r"Average time: ([0-9.e+-]*)s", log)
    if m is not None:
        ratracer_probetime = float(m.group(1))
    else:
        ratracer_probetime = None
    try:
        with open(statfn, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        #print("# skip", statfn)
        continue
    mtime = max(os.path.getmtime(logfn), os.path.getmtime(statfn))
    mem_proportional_idx = data["columns"].index("mem_proportional")
    table.append([
        problem,
        method,
        ("" if ok else "!! ") + fmt_time(data["time"]),
        fmt_time(firefly_time) if firefly_time else "--",
        fmt_time(firefly_probetime) if firefly_probetime else "--",
        fmt_time(ratracer_probetime) if ratracer_probetime else "--",
        fmt_units(firefly_probes) if firefly_probes else "--",
        f"{firefly_probetime*firefly_probes/firefly_time/8*100:.1f}%" if firefly_probetime and firefly_probes and firefly_time else "--",
        fmt_bytes(max(sum(p[mem_proportional_idx] for p in s["processes"]) for s in data["series"])),
        fmt_bytes(max(s["disk"] for s in data["series"])),
        fmt_time(now - mtime)
    ])
table.sort()

header = ["problem", "method", "time", "ff_time", "ff_probe", "rart_probe", "ff_probes", "ff_eff", "ram", "disk", "time_ago"]
fmt = ["-", "-", "", "", "", "", "", "", "", "", ""]
table = [header] + table
width = [max(len(cell) for cell in column) for column in zip(*table)]

for row in table:
    print("  ".join([f"%{f}{w}s" % cell for cell, w, f in zip(row, width, fmt)]))
