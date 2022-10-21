#!/bin/sh

rm -rf input_kira/ ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} export.yaml

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time ratracer \
    set d '4-2*eps' \
    $(for x in input_kira/basis/*.kira.gz; do echo load-equations $x; done) \
    solve-equations \
    choose-equation-outputs --family=basis --maxr={p.maxr} --maxs={p.maxs} --maxd={p.maxd} \
    drop-equations \
    optimize finalize save-trace uds.trace.zst \
    to-series eps 1 \
    finalize unfinalize optimize finalize \
    save-trace uds.eps.trace.zst

/usr/bin/time ratracer \
    load-trace uds.eps.trace.zst \
    measure \
    reconstruct --inmem --threads={p.threads} --to=ibp-tables

/usr/bin/time ./rat2mat <ibp-tables >ibp-tables.m
