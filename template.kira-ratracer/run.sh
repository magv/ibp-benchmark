#!/bin/sh

rm -rf input_kira/ ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

kira --parallel={p.threads} export.yaml

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

ratracer \
    $(for x in input_kira/basis/*.kira.gz; do echo load-equations $x; done) \
    solve-equations \
    choose-equation-outputs --family=basis --maxr={p.maxr} --maxs={p.maxs} --maxd={p.maxd} \
    optimize finalize save-trace uds.trace.gz \
    reconstruct --inmem --threads={p.threads} --to=ibp-tables

./rat2mat <ibp-tables >ibp-tables.m
