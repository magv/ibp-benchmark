#!/bin/sh

rm -rf input_kira/ ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

kira --parallel={p.threads} export.yaml

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

kira --parallel={p.threads} solve.yaml

mv results/basis/kira_integrals.m ibp-tables.m
