#!/bin/sh

rm -rf input_kira/ ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} export.yaml

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time ratracer \
    $(for x in input_kira/basis/*.kira.gz; do echo load-equations $x; done) \
    solve-equations \
    choose-equation-outputs --family=basis --maxr={p.maxr} --maxs={p.maxs} --maxd={p.maxd} \
    drop-equations \
    optimize finalize save-trace uds.trace.zst

/usr/bin/time ratracer \
    load-trace uds.trace.zst \
    measure \
    reconstruct --inmem --factor-scan --shift-scan --threads={p.threads} --to=ibp-tables

/usr/bin/time ./rat2mat <ibp-tables >ibp-tables.m