#!/bin/sh

rm -rf results/ sectormappings/ tmp/ kira.log

/usr/bin/time kira --parallel={p.threads} jobs.yaml

mv results/basis/kira_integrals.m ibp-tables.m
