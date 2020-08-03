#!/usr/bin/env sh
# -*- coding: utf8 -*-
#
#  Copyright (c) 2014 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Jesse Griffin <jesse@distantshores.org>
#  Caleb Maclennan <caleb@alerque.com>

APIBASE=/var/www/vhosts/api.unfoldingword.org/httpdocs/obs/txt/1/
help() {
    echo
    echo "Publish OBS."
    echo
    echo "Usage:"
    echo "   $PROGNAME -l <LangCode>"
    echo "   $PROGNAME --help"
    echo
    exit 1
}

if [ $# -lt 1 ]; then
    help
fi
while test -n "$1"; do
    case "$1" in
        --help|-h)
            help
            ;;
        --lang|-l)
            LANG="$2"
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            help
            ;;
    esac
    shift
done

if [ -z "$LANG" ]; then
    echo "Error: language to export must be specified."
    help
fi

# Figure out where _this_ script is so we can reference other scripts relative
# to it ever if called from elsewhere (in, say the directory we want the output)
BASEDIR=$(cd $(dirname "$0")/../ && pwd)

# Test for required TeX file first
[ ! -f "$BASEDIR/obs/tex/noto-$LANG.tex" ] && echo "Missing tex file" && exit 1

# Run export of OBS to JSON
$BASEDIR/obs/json/json_export.py -l $LANG -e || exit 1

VER=$($BASEDIR/uw/get_ver.py $LANG)
LEV=$($BASEDIR/uw/get_level.py $LANG)

# Create image symlinks on api.unfoldingword.org
$BASEDIR/uw/makejpgsymlinks.sh -l $LANG

# Create PDF via ConTeXt
$BASEDIR/obs/book/pdf_export.sh -l $LANG -c "$LEV" -v "$VER" \
    -o "$APIBASE/$LANG/"

# Create Open Document export
#$BASEDIR/obs/book/odt_export.sh -l $LANG

# Create web reveal.js viewer
# Removed as uW website does this now
#$BASEDIR/obs/js/reveal_export.py

# Run update of v2 API
$BASEDIR/uw/update_catalog.py

chown -R syncthing:syncthing "$APIBASE"

PUBNOTICE="Hello,\n\nThe resource OBS has recently been published for the $LANG language.  The version is $VER and the checking the level is $LEV.\n\nSincerely,\nYour Publishing Bot"

echo -e "$PUBNOTICE" | mail -s "OBS Published for $LANG" \
    publishing@unfoldingword.org 
