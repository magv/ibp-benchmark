#!/bin/sh
mkhintconfig() {{
    echo "#bucket 28"
    echo "#database $tmpdir/hint.database"
    echo "#threads ${{THREADS:-16}}"
    while [ $# -ge 2 ]; do
        case "$1" in
            -norm-*) ;;
            -hint-*) echo "#${{1#-hint-}} $2";;
            *) echo "#${{1#-}} $2";;
        esac
        shift 2
    done
    echo "#hint $tmpdir/hint/"
}}

mkconfig() {{
    echo "#bucket 28"
    echo "#database $tmpdir/database"
    echo "#threads ${{THREADS:-16}}"
    while [ $# -ge 2 ]; do
        case "$1" in
            -norm-*) echo "#${{1#-norm-}} $2";;
            -hint-*) ;;
            *) echo "#${{1#-}} $2";;
        esac
        shift 2
    done
    echo "#hint $tmpdir/hint/"
}}

tmpdir=$(mktemp -td "fire.$$.XXXXXXXXXX")
mkdir -p "$tmpdir/hint" || exit 1

mkhintconfig "$@" > "$tmpdir/firehint.config"
mkconfig "$@" > "$tmpdir/fire.config"

sed 's/^/# /' "$tmpdir/firehint.config"
echo "# ${{FIREPATH}}/bin/FIRE6p -c $tmpdir/firehint"
${{FIREPATH}}/bin/FIRE6p -c "$tmpdir/firehint" || exit 1

rm -rf "$tmpdir/hint.database"

sed 's/^/# /' "$tmpdir/fire.config"
echo "# ${{FIREPATH}}/bin/FIRE6 -c $tmpdir/fire"
${{FIREPATH}}/bin/FIRE6 -c "$tmpdir/fire" || exit 1

date > "$tmpdir/success" || exit 1
rm -rf "$tmpdir"
