#!/bin/sh

if [ ! -e "$FIREPATH/bin/FIRE6" ]; then
    echo "FIREPATH must be set to a FIRE6 source dir" 1>&2
    exit 1
fi

MATH=${{MATH:-math}}

rm -f *.start *.lbases *.sbases
rm -rf litered

$MATH -script step1.m
$MATH -script step2.m
$MATH -script step3.m

env THREADS=2 \
    sh ./fire-with-hint.sh \
        -hint-variables "d->521,m2->44203,s12->46639,s23->52289" \
        -hint-prime "1" \
        -norm-variables "d,m2,s12,s23" \
        -start "" \
        -problem "1 |1,4|$PWD/basisx.sbases" \
        -lbases "$PWD/basisx.lbases" \
        -integrals "$PWD/integrals" \
        -hint-output "$PWD/basisx.hint.tables" \
        -norm-output "$PWD/basisx.tables"

$MATH -script step4.m
