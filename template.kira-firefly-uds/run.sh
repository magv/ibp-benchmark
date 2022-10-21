#!/bin/sh

rm -rf input_kira/ ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} export.yaml

rm -rf ff_save/ firefly_saves/ results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} --bunch_size=4 solve.yaml

mv results/basis/kira_integrals.m ibp-tables.m
