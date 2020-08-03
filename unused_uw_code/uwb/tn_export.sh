#!/usr/bin/env bash
# -*- coding: utf8 -*-
#
#  Copyright (c) 2015 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Jesse Griffin <jesse@distantshores.org>
#  Richard Mahn <richard_mahn@wycliffeassociates.org>
#  Caleb Maclennan <caleb@alerque.com>

set -e # die if there is an error
shopt -s extglob # allow globbing

: ${TOOLS_DIR:=$(cd $(dirname "$0")/../ && pwd)} # Tools directory, relative to this script

export PATH=/usr/local/texlive/2016/bin/x86_64-linux:$PATH

FILE_TYPES=()
BOOKS_TO_PROCESS=()

VALID_FILE_TYPES=(pdf docx html tex txt text)

# Gets us an associative array called $bookS
source "$TOOLS_DIR/general_tools/bible_books.sh"

#gather command-line arguments
while [[ $# > 0 ]]
do
    arg="$1"
    case $arg in
        -o|--output)
            OUTPUT_DIR="$2"
            shift # past argument
        ;;
        -w|--working)
            WORKING_DIR="$2"
            shift # past argument
        ;;
        -l|--lang|-language)
            LANGUAGE="$2"
            shift # past argument
        ;;
        -d|--debug)
            DEBUG=true
        ;;
        -t|--type)
            arg2=${2,,}

            if [ ! ${VALID_FILE_TYPES[$arg2]+_} ];
            then
                echo "Invalid type: $arg2"
                echo "Valid types: pdf, docx, html, tex, txt, text"
                exit 1
            fi

            FILE_TYPES+=("$arg2")

            shift # past argument
        ;;
        *)
            if [ ! ${BOOK_NAMES[${arg,,}]+_} ];
            then
                if [ ${arg,,} = "ot" ];
                then
                    BOOKS_TO_PROCESS+=(gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab zep hag zec mal)
                elif [ ${arg,,} = "nt" ];
                then
                    BOOKS_TO_PROCESS+=(mat mrk luk jhn act rom 1co 2co gal eph php col 1ti 2ti 1th 2th tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev)
                elif [ ${arg,,} = "all" ];
                then
                    BOOKS_TO_PROCESS+=(gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab zep hag zec mal mat mrk luk jhn act rom 1co 2co gal eph php col 1ti 2ti 1th 2th tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev)
                else
                    echo "Invalid book given: $arg"
                    exit 1;
                fi
            else
                BOOKS_TO_PROCESS+=("$arg")
            fi
        ;;
    esac
    shift # past argument or value
done

: ${DEBUG:=false}
: ${LANGUAGE:=en}

: ${OUTPUT_DIR:=$(pwd)}
: ${TEMPLATE:=$TOOLS_DIR/uwb/tex/tn_tw_tq_template.tex}

: ${D43_BASE_DIR:=/var/www/vhosts/door43.org/httpdocs/data/gitrepo/pages}
: ${D43_BASE_URL:=https://door43.org/_export/xhtmlbody}

: ${TN_DIR:=$LANGUAGE/bible/notes}
: ${TQ_DIR:=$LANGUAGE/bible/questions/comprehension}
: ${TW_DIR:=$LANGUAGE/obe}
: ${TA_DIR:=$LANGUAGE/ta}
: ${VERSION:=6}
: ${REGENERATE_HTML_FILES:=true}
: ${REDOWNLOAD_FILES:=false}

# If running in DEBUG mode, output information about every command being run
$DEBUG && set -x

# Create a temorary diretory using the system default temp directory location
# in which we can stash any files we want in an isolated namespace. It is very
# important that this dir actually exist. The set -e option should always be used
# so that if the system doesn't let us create a temp directory we won't contintue.
if [[ -z $WORKING_DIR ]]; then
    WORKING_DIR=$(mktemp -d -t "ubw_pdf_create.XXXXXX")
    # If _not_ in DEBUG mode, _and_ we made our own temp directory, then
    # cleanup out temp files after every run. Running in DEBUG mode will skip
    # this so that the temp files can be inspected manually
    $DEBUG || trap 'popd > /dev/null; rm -rf "$WORKING_DIR"' EXIT SIGHUP SIGTERM
elif [[ ! -d $WORKING_DIR ]]; then
    mkdir -p "$WORKING_DIR"
fi

# Change to own own temp dir but note our current dir so we can get back to it
pushd "$WORKING_DIR" > /dev/null

DATE=`date +"%Y-%m-%d"`

if [ ! -e $D43_BASE_DIR ];
then
    echo "The directory $D43_BASE_DIR does not exist. Can't continue. Exiting."
    exit 1;
fi

book_export () {
    book=$1

    if [ ! ${BOOK_NAMES[$book]+_} ];
    then
        echo "Invalid book given: $book"
        exit 1;
    fi

    TN_FILE="${LANGUAGE}_${book}_tn.html" # translationNotes
    TQ_FILE="${LANGUAGE}_${book}_tq.html" # translationQuestions
    TW_FILE="${LANGUAGE}_${book}_tw.html" # translationWords
    TA_FILE="${LANGUAGE}_${book}_ta.html" # translationAcademy
    HTML_FILE="${LANGUAGE}_${book}_tn_all.html" # Compilation of all above HTML files
    LINKS_FILE="${LANGUAGE}_${book}_links.sed" # SED commands for links
    OUTPUT_FILE="$OUTPUT_DIR/tn-${BOOK_NUMBERS[$book]}-${book^^}-v${VERSION}"
    BAD_LINKS_FILE="${LANGUAGE}_${book}_bad_links.txt"

    if $REGENERATE_HTML_FILES; then
        rm -f "$TN_FILE" "$TQ_FILE" "$TW_FILE" "$TA_FILE" "$LINKS_FILE" "$HTML_FILE" "$BAD_LINKS_FILE" "$OUTPUT_FILE".*  # We start fresh, only files that remain are any files retrieved with wget
    else
        rm -f "$OUTPUT_FILE".*  # Only remove the output files so they are regenerated
    fi

    touch "$LINKS_FILE"
    touch "$BAD_LINKS_FILE"

    # ----- START GENERATE tN PAGES ----- #
    if [ ! -e "$TN_FILE" ];
    then
        echo "GENERATING $TN_FILE"
        
        touch "$TN_FILE"
        
        find "$D43_BASE_DIR/$TN_DIR/$book" -mindepth 1 -maxdepth 1 -type d -name "[[:digit:]]*" -printf '%P\n' |
            sort -u |
            while read chapter;
            do
                dir="$TN_DIR/$book/$chapter";
                mkdir -p "$dir"
        
                find "$D43_BASE_DIR/$dir" -mindepth 1 -maxdepth 1 -type f \( -name "[[:digit:]]*.txt" -or -name "intro.txt" -or -name "tatopics.txt" -or -name "words.txt" \) \( -exec grep -q 'tag>.*publish' {} \; -or -not -exec grep -q 'tag>.*draft' {} \; \) -printf '%P\n' |
                    grep -v 'asv-ulb' |
                    sort -u |
                    while read f; do
                        section=${f%%.txt}

                        # If the file doesn't exist or is older than (-ot) the file in the Door43 repo, fetch the file
                        if $REDOWNLOAD_FILES || [ ! -e "$dir/$section.html" ] || [ "$dir/$section.html" -ot "$D43_BASE_DIR/$dir/$section.txt" ];
                        then
                            set +e
                            wget -U 'me' "$D43_BASE_URL/$dir/$section" -O "$dir/$section.html"
        
                            if [ $? != 0 ];
                            then
                                rm "$dir/$section.html";
                                echo "$D43_BASE_URL/$dir/$section ($TN_FILE)" >> "$BAD_LINKS_FILE"
                            fi
                            set -e
                        fi
        
                        if [ -e "$dir/$section.html" ];
                        then
                            # Remove TFT and >> and /tag/ lines
                            TFT=false
                            while read line; do
                                if [[ $line == '<h2 class="sectionedit2" id="tft">TFT:</h2>' ]]; then
                                    TFT=true
                                    continue
                                fi
        
                                if [[ ${line:0:25} == '<!-- EDIT2 SECTION "TFT:"' ]]; then
                                    TFT=false
                                    continue
                                fi
        
                                $TFT && continue
        
                                if [[ ! $line =~ '<strong>'.*'&gt;</a></strong>' ]] && [[ ! $line =~ ' href="/tag/' ]];
                                then
                                    echo "$line" >> "$TN_FILE"
                                fi
                            done < "$dir/$section.html"

                            linkname=$(head -3 "$dir/$section.html" | grep -o 'id=".*"' | cut -f 2 -d '=' | tr -d '"')
                            start_verse=${section##+(0)} # strip leading zeros from section to get the start verse
                            end_verse=$(head -3 "$dir/$section.html" | grep -o ':[[:digit:]]\+-[[:digit:]]\+' | cut -f 2 -d '-')
                            if [ -z "$end_verse" ];
                            then
                                end_verse=$start_verse
                            fi
                            if [[ $start_verse =~ ^-?[[:digit:]]+$ ]];
                            then
                                while [ $start_verse -le $end_verse ];
                                do
                                    if [ $start_verse -lt 10 ];
                                    then
                                        if [ "$book" == "psa" ];
                                        then
                                            url="/$dir/00$start_verse"
                                        else
                                            url="/$dir/0$start_verse"
                                        fi
                                    else
                                        if [ $start_verse -lt 100 ] && [ "$book" == "psa" ];
                                        then
                                            url="/$dir/0$start_verse"
                                        else
                                            url="/$dir/$start_verse"
                                        fi
                                    fi
                                    echo "s@\"[^\"]*$url\"@\"#$linkname\"@g" >> "$LINKS_FILE"
                                    let start_verse=start_verse+1
                                done
                            else
                                url="/$dir/$start_verse"
                                echo "s@\"[^\"]*$url\"@\"#$linkname\"@g" >> "$LINKS_FILE"
                            fi
                        else
                            echo "<h1>$book $chapter:$section - MISSING - CONTENT UNAVAILABLE</h1><p>Unable to get content from $D43_BASE_URL/$dir/$section - page does not exist</p>" >> "$TN_FILE"
                        fi
                    done
            done
        
        # Increase all headers by one so that the headers we add when making the HTML_FILE are the only h1 headers
        sed -i -e 's/<\(\/\)\{0,1\}h3/<\1h4/g' "$TN_FILE"
        sed -i -e 's/<\(\/\)\{0,1\}h2/<\1h3/g' "$TN_FILE"
        sed -i -e 's/<\(\/\)\{0,1\}h1/<\1h2/g' "$TN_FILE"
        # Superscript all verses
        sed -i -e "s@\(<span class=['\"]usfm-v['\"]><b class=['\"]usfm['\"]><a name=['\"][^'\"]*['\"]></a>[[:digit:]]\+</b></span>\) *@<sup>\1</sup> @g" "$TN_FILE"
        # Change chapter numbers to <b>#</b>
        sed -i -e "s@<p class='usfm-flush' align='justify'><span class='usfm-c'><big class='usfm-c'><big class='usfm-c'><big class='usfm-c'><big class='usfm-c'>\([[:digit:]]\+\)</big></big></big></big></span>\(.*\)@<b>\1</b> \2@" "$TN_FILE"
        sed -i -e 's@>\([^>]\+\) 0*\([[:digit:]]\+\)\([^<]*\)</h2>@>\1 \2\3</h2>@' "$TN_FILE" # Strip 0 off of any tN title
    else
        echo "NOTE: $TN_FILE already generated."
    fi
    # ----- END GENERATE tN PAGES ------- #

    # ----- START GENERATE tQ PAGES ----- #
    if [ ! -e "$TQ_FILE" ];
    then
        echo "GENERATING $TQ_FILE"
        
        touch "$TQ_FILE"
        
        dir="$TQ_DIR/$book"
        mkdir -p "$dir"
        
        find "$D43_BASE_DIR/$TQ_DIR/$book" -type f -name "[[:digit:]]*.txt" -exec grep -q 'tag>.*publish' {} \; -printf '%P\n' |
            sort |
            while read f;
            do
                chapter=${f%%.txt}
        
                # If the file doesn't exist or is older than (-ot) the file in the Door43 repo, fetch the file
                if $REDOWNLOAD_FILES || [ ! -e "$dir/$chapter.html" ] || [ "$dir/$chapter.html" -ot "$D43_BASE_DIR/$dir/$chapter.txt" ];
                then
                    set +e
                    wget -U 'me' "$D43_BASE_URL/$dir/$chapter" -O "$dir/$chapter.html"
        
                    if [ $? != 0 ];
                    then
                        rm "$dir/$chapter.html";
                        echo "$D43_BASE_URL/$dir/$chapter ($TQ_FILE)" >> "$BAD_LINKS_FILE"
                    fi
                    set -e
                fi
        
                if [ -e "$dir/$chapter.html" ];
                then
                    grep -v '<strong>.*&gt;<\/a><\/strong>' "$dir/$chapter.html" |
                        grep -v ' href="\/tag\/' >> "$TQ_FILE"
        
                    linkname=$(head -3 "$dir/$chapter.html" | grep -o 'id=".*"' | cut -f 2 -d '=' | tr -d '"')
                    echo "s@\"[^\"]*/$dir/$chapter\"@\"#$linkname\"@g" >> "$LINKS_FILE"
                else
                    echo "<h1>$book $chapter - MISSING - CONTENT UNAVAILABLE</h1><p>Unable to get content from $D43_BASE_URL/$dir/$chapter - page does not exist</p>" >> "$TQ_FILE"
                fi
            done

        # Make Q? and A. bold and put a <hr> between Q/A pairs
        sed -i -e 's@^A\.\(.*\)$@A.\1\n</p>\n\n<p>\n<hr/>@' "$TQ_FILE"
        sed -i -e 's@^\(Q?\|A\.\) @<b>\1</b> @' "$TQ_FILE"
        # Pad all verse references with 0s if single digits and then make a link to the chunk of the chapter number and first verse #
        sed -i -e 's@\[\([1-9]\):@[0\1:@g' "$TQ_FILE" # [1: => [01:
        sed -i -e 's@\[\([[:digit:]]\+\):\([[:digit:]]\)\]@[\1:0\2]@g' "$TQ_FILE" # [01:1] => [01:01]
        sed -i -e 's@\[\([[:digit:]]\+\):\([[:digit:]]-[[:digit:]]\+\)\]@[\1:0\2]@g' "$TQ_FILE" # [01:1-2] => [01:01-2]
        sed -i -e 's@\[\([[:digit:]]\+\):\([[:digit:]]+\+\)-\([[:digit:]]\)\]@[\1:\2-0\3]@g' "$TQ_FILE" # [01:01-2] => [01:01-02]
        # Add an extra 0 for padding in Psalm chapters and verses
        if [ "$book" == "psa" ];
        then
            sed -i -e 's@\[\([[:digit:]][[:digit:]]\):@[0\1:@g' "$TQ_FILE" # [01: => [001:
            sed -i -e 's@\[\([[:digit:]]\+\):\([[:digit:]][[:digit:]]\)\]@[\1:0\2]@g' "$TQ_FILE" # [001:1] => [001:001]
            sed -i -e 's@\[\([[:digit:]]\+\):\([[:digit:]][[:digit:]]-[[:digit:]]\+\)\]@[\1:0\2]@g' "$TQ_FILE" # [001:01-02] => [001:001-02]
            sed -i -e 's@\[\([[:digit:]]\+\):\([[:digit:]]+\+\)-\([[:digit:]][[:digit:]]\)\]@[\1:\2-0\3]@g' "$TQ_FILE" # [001:001-02] => [001:001-002]
        fi
        sed -i -e 's@\[\(0*\)\([[:digit:]]\+\):\(0*\)\([[:digit:]]\+\)\(0*\)\([0-9-]*\)\]@[<a href="/en/bible/notes/'$book'/\1\2/\3\4">\2:\4\6</a>]@g' "$TQ_FILE" # Try to link all verse to their chunk
        # Remove "Translation Questions" from title and any leading 0s
        sed -i -e 's@>\([^>]\+\) 0*\([[:digit:]]\+\) Translation Questions@>\1 \2@' "$TQ_FILE"
        # REMOVE links at end of question page to return to question home page
        sed -i -e "\@/$dir/home@d" "$TQ_FILE"
    else
        echo "NOTE: $TQ_FILE already generated."
    fi
    # ----- END GENERATE tQ PAGES ------- #

    # ----- START GENERATE tW PAGES ----- #
    if [ ! -e "$TW_FILE" ];
    then
        echo "GENERATING $TW_FILE"
        
        touch "$TW_FILE"
        
        # Get the linked key terms
        export IFS=$'\n'
        for term_data in $(grep -oPh "\"\/$LANGUAGE\/obe.*?\"" "$TN_FILE" | sed 's@^"/\(.*\)/\(.*\)"@\2\t\1@' | sort -u);
        do
            dir=$(awk -F '\t' '{print $2}'<<<$term_data)
            term=$(awk -F '\t' '{print $1}'<<<$term_data)

            mkdir -p "$dir"
        
            # If the file doesn't exist or is older than (-ot) the file in the Door43 repo, fetch the file
            if $REDOWNLOAD_FILES || [ ! -e "$dir/$term.html" ] || [ "$dir/$term.html" -ot "$D43_BASE_DIR/$dir/$term.txt" ];
            then
                set +e
                wget -U 'me' "$D43_BASE_URL/$dir/$term" -O "$dir/$term.html"
        
                if [ $? != 0 ];
                then
                    rm "$dir/$term.html";
                    echo "$D43_BASE_URL/$dir/$term ($TW_FILE)" >> "$BAD_LINKS_FILE"
                fi
                set -e
            fi
        
            if [ -e "$dir/$term.html" ];
            then
                TAG_LINES=false
                while read line; do
                    # Remove everything after the <div class="tags"><span> tags but keep the closing </div> tag
                    if [[ $line == '<div class="tags"><span>' ]] || $TAG_LINES; then
                        TAG_LINES=true
                        if [[ $line == '</span></div>' ]]; then
                            TAG_LINES=false
                        fi
                        continue
                    fi
        
                    echo "$line" >> "$TW_FILE"
                done < "$dir/$term.html"
        
                linkname=$(head -3 "$dir/$term.html" | grep -o 'id=".*"' | cut -f 2 -d '=' | tr -d '"')
                echo "s@\"[^\"]*/$dir/$term\"@\"#$linkname\"@g" >> "$LINKS_FILE"
            else
                echo "<h1>$term - MISSING - CONTENT UNAVAILABLE</h1><p>Unable to get content from $D43_BASE_URL/$dir/$term - page does not exist</p>" >> "$TW_FILE"
            fi
        done
        unset IFS

        # Quick fix for getting rid of these Bible References lists in a table, removing table tags
        sed -i -e 's/^\s*<table class="ul">/<ul>/' "$TW_FILE"
        sed -i -e 's/^\s*<tr>//' "$TW_FILE"
        sed -i -e 's/^\s*<td class="page"><ul>\(.*\)<\/ul><\/td>/\1/' "$TW_FILE"
        sed -i -e 's/^\s*<\/tr>//' "$TW_FILE"
        sed -i -e 's/^\s*<\/table>/<\/ul>/' "$TW_FILE"
        
        # increase all headers by one so that the headers we add when making the HTML_FILE are the only h1 headers
        sed -i -e 's/<\(\/\)\{0,1\}h3/<\1h4/g' "$TW_FILE"
        sed -i -e 's/<\(\/\)\{0,1\}h2/<\1h3/g' "$TW_FILE"
        sed -i -e 's/<\(\/\)\{0,1\}h1/<\1h2/g' "$TW_FILE"
    else
        echo "NOTE: $TW_FILE already generated."
    fi
    # ----- END GENERATE tW PAGES ------- #

    # ----- START GENERATE tA PAGES ----- #
    if [ ! -e "$TA_FILE" ];
    then
        echo "GENERATING $TA_FILE"
        
        touch "$TA_FILE"
        
        # Get the linked tA
        export IFS=$'\n'
        for term_data in $(grep -oPh "\"\/$LANGUAGE\/ta\/.*?\"" "$TN_FILE" "$TW_FILE" "$TQ_FILE" | sed 's@^"/\(.*\)/\(.*\)"@\2\t\1@' | sort -u);
        do
            dir=$(awk -F '\t' '{print $2}'<<<$term_data)
            term=$(awk -F '\t' '{print $1}'<<<$term_data)

            mkdir -p "$dir"
    
            # If the file doesn't exist or is older than (-ot) the file in the Door43 repo, fetch the file
            if $REDOWNLOAD_FILES || [ ! -e "$dir/$term.html" ] || [ "$dir/$term.html" -ot "$D43_BASE_DIR/$dir/$term.txt" ];
            then
                set +e
                wget -U 'me' "$D43_BASE_URL/$dir/$term" -O "$dir/$term.html"
    
                if [ $? != 0 ];
                then
                    rm "$dir/$term.html";
                    echo "$D43_BASE_URL/$dir/$term ($TA_FILE)" >> "$BAD_LINKS_FILE"
                fi
                set -e
            fi
    
            if [ -e "$dir/$term.html" ];
            then
                cat "$dir/$term.html" |
                    grep -v ' href="\/tag\/' >> "$TA_FILE"
    
                linkname=$(head -3 "$dir/$term.html" | grep -o 'id=".*"' | cut -f 2 -d '=' | tr -d '"')
                echo "s@\"[^\"]*/$dir/$term\"@\"#$linkname\"@g" >> "$LINKS_FILE"
            else
                echo "<h1>$term - MISSING - CONTENT UNAVAILABLE</h1><p>Unable to get content from $D43_BASE_URL/$dir/$section - page does not exist</p>" >> "$TA_FILE"
            fi
        done
        unset IFS
        
        # get rid of the pad.door43.org links and the <hr> with it
        sed -i -e 's/^\s*<a href="https:\/\/pad\.door43\.org.*//' "$TA_FILE"
        sed -i -e 's/^<hr \/>//' "$TA_FILE"
        # sed -i -e 's@<em class="u"[^>]*>\([^<]*\)</em>@<u>\1</u>@g' "$TA_FILE"
    else
        echo "NOTE: $TA_FILE already generated."
    fi
    # ----- END GENERATE tA PAGES ------- #

    # ----- START GENERATE HTML PAGE ----- #
    if [ ! -e "$HTML_FILE" ];
    then
        # Compile all the above CL, tN, tQ, tW, and tA HTML files into one with headers
        echo "GENERATING $HTML_FILE"
        
        echo '<h1>translationNotes</h1>' >> "$HTML_FILE"
        cat "$TN_FILE" >> "$HTML_FILE"
        
        echo '<h1>translationQuestions</h1>' >> "$HTML_FILE"
        cat "$TQ_FILE" >> "$HTML_FILE"
        
        echo '<h1>translationWords</h1>' >> "$HTML_FILE"
        cat "$TW_FILE" >> "$HTML_FILE"
        
        echo '<h1>translationAcademy</h1>' >> "$HTML_FILE"
        cat "$TA_FILE" >> "$HTML_FILE"
        
        # ----- START LINK FIXES AND CLEANUP ----- #
        # Link Fixes
        sed -i -f "$LINKS_FILE" "$HTML_FILE"
        sed -i -e 's/\/en\/bible.*"/"/' "$HTML_FILE"
        sed -i -e 's/\/en\/obs.*"/"/' "$HTML_FILE"
        sed -i -e 's/ \(src\|href\)="\// \1="https:\/\/door43.org\//g' "$HTML_FILE"

        # Clean up
        sed -i -e 's/\xe2\x80\x8b//g' -e '/^<hr>/d' -e '/&lt;&lt;/d' \
            -e 's/<\/span>\([^<]\)/<\/span> \1/g' -e 's/jpg[?a-zA-Z=;&0-9]*"/jpg"/g' \
            "$HTML_FILE"

        # ----- END LINK FIXES AND CLEANUP ------- #
    else
        echo "NOTE: $HTML_FILE already generated."
    fi
    # ----- END GENERATE HTML PAGES ------- #

    # ----- START GENERATE OUTPUT FILES ----- #
    TITLE="${BOOK_NAMES[$book]}"
    SUBTITLE="translationNotes"

    LOGO="https://unfoldingword.org/assets/img/icon-tn.png"
    response=$(curl --write-out %{http_code} --silent --output logo-tn.png "$LOGO");
    if [ $response -eq "200" ];
    then
      LOGO_FILE="-V logo=logo-tn.png"
    fi

    FORMAT_FILE="$TOOLS_DIR/uwb/tex/format.tex"

    for type in "${FILE_TYPES[@]}"
    do
        if [ ! -e "$OUTPUT_FILE.$type" ];
        then
            echo "GENERATING $OUTPUT_FILE.$type";

            pandoc \
                --latex-engine="xelatex" \
                --template="$TEMPLATE" \
                --toc \
                --toc-depth=2 \
                -V documentclass="scrartcl" \
                -V classoption="oneside" \
                -V geometry='hmargin=2cm' \
                -V geometry='vmargin=3cm' \
                -V title="$TITLE" \
                -V subtitle="$SUBTITLE" \
                $LOGO_FILE \
                -V date="$DATE" \
                -V version="$VERSION" \
                -V mainfont="Noto Serif" \
                -V sansfont="Noto Sans" \
                -V fontsize="13pt" \
                -V urlcolor="Bittersweet" \
                -V linkcolor="Bittersweet" \
                -H "$FORMAT_FILE" \
                -o "$OUTPUT_FILE.$type" "$HTML_FILE"
                
            echo "GENERATED FILE: $OUTPUT_FILE.$type"
        else
            echo "NOTE: $OUTPUT_FILE.$type already generated."
        fi
    done
    # ----- END GENERATE OUTPUT FILES ------- #
}

# ---- EXECUTION BEGINS HERE ----- #

if [ ${#BOOKS_TO_PROCESS[@]} -eq 0 ];
then
    echo "Please specify one or more books by adding their abbreviations, separated by spaces. Book abbreviations are as follows:";

    for key in "${!BOOK_NAMES[@]}"
    do
        echo "$key: ${BOOK_NAMES[$key]}";
    done |
    sort -n -k3

    exit 1;
fi

if [ ${#FILE_TYPES[@]} -eq 0 ];
then
    FILE_TYPES=(pdf)
fi

for book in "${BOOKS_TO_PROCESS[@]}"
do
    book_export ${book,,}
done

echo "Done!"
