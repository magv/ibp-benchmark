#!/bin/sh

rm -rf results/ sectormappings/ tmp/ kira.log

kira --parallel={p.threads} jobs.yaml

mv results/basis/kira_integrals.m ibp-tables.m
