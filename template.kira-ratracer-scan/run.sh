#!/bin/sh

rm -rf input_kira/ ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} export.yaml

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time ratracer \
#% if p.preferred_masters:
    define-family master \
    load-equations master-eqns \
#% pass
    $(for x in input_kira/basis/*.kira.gz; do echo load-equations $x; done) \
    solve-equations \
    choose-equation-outputs --family=basis --maxr={p.maxr} --maxs={p.maxs} --maxd={p.maxd} \
    drop-equations \
    keep-outputs output-list \
    optimize finalize save-trace uds.trace.zst

/usr/bin/time ratracer \
    load-trace uds.trace.zst \
    measure \
    reconstruct --inmem --factor-scan --shift-scan --threads={p.threads} --to=ibp-tables

#% if p.preferred_masters:
/usr/bin/time sed -E ibp-tables \
#%     for i, indices in enumerate(p.preferred_masters):
        -e 's/\bmaster\@{i}\b/basis[{",".join(str(i) for i in indices)}]/g' \
#%     pass
    | ./rat2mat >ibp-tables.m
#% else:
/usr/bin/time ./rat2mat <ibp-tables >ibp-tables.m
#% pass
