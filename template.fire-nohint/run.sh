#!/bin/sh

if [ ! -e "$FIREPATH/bin/FIRE6" ]; then
    echo "FIREPATH must be set to a FIRE6 source dir" 1>&2
    exit 1
fi

MATH=${{MATH:-math}}

if ! which $MATH >/dev/null; then
    echo "MATH must be set to the Mathematica CLI binary name" 1>&2
    exit 1
fi

rm -f *.start *.lbases *.sbases
rm -rf litered

$MATH -script step1.m || exit 1
$MATH -script step2.m || exit 1
$MATH -script step3.m || exit 1

mkdir fire.hintdir
$FIREPATH/bin/FIRE6 -c fire || exit 1

$MATH -script step4.m || exit 1
