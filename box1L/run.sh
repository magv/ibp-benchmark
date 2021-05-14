#!/bin/sh

rm -rf results/ sectormappings/ tmp/ kira.log

kira --parallel=2 jobs.yaml
