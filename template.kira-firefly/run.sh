#!/bin/sh

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

kira --parallel={p.threads} jobs.yaml

mv results/basis/kira_integrals.m ibp-tables.m
