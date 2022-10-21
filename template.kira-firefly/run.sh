#!/bin/sh

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} --bunch_size=4 jobs.yaml

mv results/basis/kira_integrals.m ibp-tables.m
