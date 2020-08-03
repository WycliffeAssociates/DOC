# coding: latin-1
# This source file converts a repository of quasi-USFM text files to a single
# file in proper USFM format, in the same folder.

import re

# Copies XX.txt to XX-orig.txt.
# Calls ensureFirstMarkers().
# On exit, XX.txt contains the improved chunk.
# On exit, XX-orig.txt contains the original chunk, if different.
def cleanupChunk(directory, filename):
    dot = filename.find('.')
    verse = filename[0:dot]
    chapter = u""
    if verse == "01":
        chapter = directory
    ext = filename[dot:]
    path = directory + "/" + filename
    tmpPath = directory + "/" + verse + "-orig" + ext
    if os.access(tmpPath, os.F_OK):
        os.remove(tmpPath)
    os.rename(path, tmpPath)

    input = io.open(tmpPath, "tr", 1, encoding='utf-8')
    output = io.open(path, "tw", 1, encoding='utf-8')
    lacking = lacksMarkers(input, chapter.lstrip('0'), verse.lstrip('0'))  # returns (lacksC, lacksV) pair
    input.seek(0)
    changed = ensureFirstMarkers(input, output, lacking[0], lacking[1])
    output.close()
    input.close()
    if not changed:
        # Restore the original file
        os.remove(path)
        os.rename(tmpPath, path)

# Many input files are lacking a chapter marker.
# Many are lacking a verse marker.
# This function returns a pair where the first item is the missing chapter, or "", and the
# second item is the missing verse, or "".
def lacksMarkers(input, wantChapter, wantVerse):
    foundC = False
    foundV = False
    foundText = False
    markerExpr = re.compile(u'\\\\[a-z0-9]+[ \n\t]+[\d]{0,3}')

    line = input.readline()
    while line and not foundV and not foundText:
        s = line.lstrip()
        match = markerExpr.match(s)
        while match and not foundV:
            # Peel off and output leading USF markers
            marker = s[match.start():match.end()]
            # print "WRITING MARKER: <" + marker + ">"
            if marker[0:2] == "\\c" and not foundV:
                wantChapter = ""
            elif marker[0:2] == "\\v" and not foundText:
                foundV = True
                wantVerse = ""
            s = s[match.end():].lstrip()    # s has everything after the marker
            # print "S AFTER STRIPPING PREV MATCH: <" + s + ">"
            match = markerExpr.match(s)

        # At this point, S contains the remainder of the input on the current line
            
        if len(s) > 1 and not foundV:
            # At this point we have a non-empty string with no leading markers
            foundText = True
        else:
            # The line was blank or had markers only
            line = input.readline()
    return (wantChapter, wantVerse)


# Many input files are missing the first verse marker.
# This function prepends a verse marker if missing. The verse number is based on the file name.
# Since all 01.txt input files start a new chapter, they should all start with a chapter marker.
# This method makes it so.
# Returns True if any missing markers were corrected.
def ensureFirstMarkers(input, output, missingChapter, missingVerse):
    foundV = False
    changes = (missingChapter or missingVerse)
    markerExpr = re.compile(u'\\\\[a-z0-9]+[ \n\t]+[\d]{0,3}')

    line = input.readline()
    while line and (missingChapter or missingVerse):
        s = line.lstrip()
        match = markerExpr.match(s)
        while match and not foundV:
            # Peel off and output leading USF markers
            marker = s[match.start():match.end()]
            # print "WRITING MARKER: <" + marker + ">"
            if marker[0:2] == "\\v" and missingChapter:
                output.write(u"\\c " + missingChapter + u"\n")
                missingChapter = ""
                missingVerse = ""
                foundV = True
            output.write(marker + u'\n')
            s = s[match.end():].lstrip()    # s has everything after the marker
            # print "S AFTER STRIPPING PREV MATCH: <" + s + ">"
            match = markerExpr.match(s)

        # At this point the output file contains everything up to where a verse marker
        # or text is found.
        # S contains everything in the current line not yet written to the output file.
            
        if len(s) > 1:    # Found text before verse marker appeared, or verse marker was found
            if missingChapter:
                output.write(u"\\c " + missingChapter + u"\n")
                missingChapter = ""
            if missingVerse:
                output.write(u"\\v " + missingVerse + u"\n")
                missingVerse = ""
            output.write(s + u"\n")
        line = input.readline()

    if missingChapter:
        output.write(u"\\c " + missingChapter + u"\n")
        missingChapter = ""
    if missingVerse:
        output.write(u"\\v " + missingVerse + u"\n")
        missingVerse = ""
    while line:
        # print "COPYING: " + line
        output.write(line)
        line = input.readline()
    return changes

# Restores files that were renamed to XX-orig.txt by cleanupCheck().
# Renames fixed XX.txt file to XX-fixed.txt.
def restoreOrigFile(directory, filename):
    dot = filename.find('.')
    verse = filename[0:dot]
    ext = filename[dot:]
    path = directory + "/" + filename
    tmpPath = directory + "/" + verse + "-orig" + ext
    if os.access(tmpPath, os.F_OK):
        fixPath = directory + "/" + verse + "-fixed" + ext
        if os.access(fixPath, os.F_OK):
            os.remove(fixPath)
        os.rename(path, fixPath)
        os.rename(tmpPath, path)


# Does a first pass on a list of lines to eliminate unwanted line breaks,
# tabs, and extra whitespace. Places most markers at the beginning of lines.
# May perform other first pass cleanup tasks.
def combineLines(lines):
    section = ""
    for line in lines:
        line = line.strip(" \t\r\n")    # strip leading and trailing whitespace
        line = line.replace("\t", " ")
        line = line.replace("   ", " ")
        line = line.replace("  ", " ")
        line = line.replace(" \\c", "\n\\c")
        line = line.replace(" \\p", "\n\\p")
        line = line.replace(" \\s", "\n\\s")
        line = line.replace("\\v", "\n\\v")
        # line = line.replace(" \\v", "\n\\v")
        line = line.strip(" \t\r\n")    # strip trailing spaces

        if line:    # disregard lines that reduced to nothing
            if len(section) == 0:
                section = line
            else:
                if line[0] != '\\':
                    section = section + " " + line
                else:
                    section = section + "\n" + line
    return section

cvExpr = re.compile(u'\\\\[cv] [0-9]+')

# Prepends an s5 marker before the first chapter or verse marker.
def addSectionMarker(section):
    marker = cvExpr.search(section)
    if marker:
        newsection = section[0:marker.start()] + u'\\s5\n' + section[marker.start():]
    else:
        newsection = section    # this should rarely occur
    return newsection

# Adds a paragraph marker after each chapter marker
# Where a chapter does not start a new paragraph (like John 8), manually
# replace the paragraph marker with \nb.
def addParagraphMarker(section):
    tokenlist = re.split('(\\\\c [0-9]+)', section)
    marked = ""
    for token in tokenlist:
        if re.match('\\\\c [0-9]+', token):
            token = token + "\n\\p"   # add paragraph mark after each chapter marker
        marked = marked + token
    return marked

# Removes extraneous space before clause ending punctuation and adds space after
# sentence/clause end if needed.
def fixPunctuationSpacing(section):
    # First remove space before most punctuation
    section = section.replace(" .", ".")
    section = section.replace(" ;", ";")
    section = section.replace(" :", ":")
    section = section.replace(" ,", ",")
    section = section.replace(" ?", "?")
    section = section.replace(" !", "!")
    section = section.replace(" )", ")")
    section = section.replace(u" �", u"�")
    section = section.replace(u" �", u"�")

    # Then add space after punctuation where needed
    jammed = re.compile(u"[.?!;:,)][^ .?!;:,)'����\"]")
    match = jammed.search(section, 0)
    while match:
        if match.end() < len(section) and section[match.end()-1] != '\n':
            section = section[:match.end()-1] + ' ' + section[match.end()-1:]
        pos = match.end() - 1
        match = jammed.search(section, pos)
    return section
    
# Inserts space between \c and the chapter number if needed
def fixChapterMarkers(section):
    pos = 0
    match = re.search(u'\\\\c[0-9]', section, 0)
    while match:
        section = section[:match.end()-1] + ' ' + section[match.end()-1:]
        pos = match.end()
        match = re.search(u'\\\\c[0-9]', section, pos)
    return section
    
# Fixes the format of verse markers in the section
# All verse markers in the incoming string should already be at the beginning of a line.
# Converts "\v 10 10" or "\v10 10" or "\v10" to "\v 10"
def fixVerseMarkers(section):
    # Ensure space after each \v
    jammed = re.compile(u'\\\\v[0-9]')
    match = jammed.search(section, 0)
    while match:
        section = section[:match.end()-1] + ' ' + section[match.end()-1:]
        pos = match.end()
        match = jammed.search(section, pos)

    # Take care of repeated verse numbers
    tokenlist = re.split('(\\\\v [0-9]+ [0-9]+)', section)
    section = ""
    repeatedVerseNumber = re.compile(u'\\\\v [0-9]+ [0-9]+')
    for token in tokenlist:
        if repeatedVerseNumber.match(token):
            parts = re.split(' ', token)
            verse = parts[1]
            if parts[2] == parts[1]:
                token = "\\v " + parts[1]
        section = section + token

    # Ensure space after each verse number
    jammed = re.compile(u'\\\\v [0-9]+[^ \n0123456789]')
    match = jammed.search(section)
    while match:
        section = section[:match.end()-1] + ' ' + section[match.end()-1:]
        match = jammed.search(section)

    # Eliminate duplicate verse markers
    vm = re.compile(u'(\\\\v [0-9]+)')
    tokenlist = re.split(vm, section)
    section = ""
    lastVerseMarker = ""
    for token in tokenlist:
        if vm.match(token):
            if token != lastVerseMarker:
                lastVerseMarker = token
                section = section + token
            else:
                print "REMOVED DUPLICATE VERSE MARKER: " + token
        else:
            section = section + token
    
    return section
    
import io
import os

# Accepts a directory, and single file name which contains one chunk.
# Reads all the lines from that file and converts the text to a single
# USFM section.
def convertFile(directory, filename):
    input = io.open(directory + "/" + filename, "tr", 1, encoding='utf-8')
    lines = input.readlines()
    input.close()
    section = u"\n" + combineLines(lines)
    section = addSectionMarker(section)
    section = addParagraphMarker(section)
    # Most texts already have paragraph markers after chapter markers
    # Technically, only the first verse in the book is required to have a paragraph marker
    section = fixPunctuationSpacing(section)
    section = fixChapterMarkers(section)
    section = fixVerseMarkers(section)
    return section

# Returns True if the specified directory is one with text files to be converted
def isChapter(dirname):
    isChap = False
    if len(dirname) == 2 and dirname != '00' and re.match('\d\d', dirname):
        isChap = True
    return isChap

# Returns True if the specified file name matches a pattern that indicates
# the file contains text to be converted.
def isChunk(filename):
    isSect = False
    if re.match('\d\d\.txt', filename) and filename != '00.txt':
        isSect = True;
    return isSect

import sys

def convertFolder(folder):
    if not folder:
        folder = os.getcwd()
    try:
        os.chdir(folder)
    except IOError as e:
        sys.stderr.write("Invalid folder: " + folder + "\n")
        return
    except WindowsError as e:
        sys.stderr.write("Invalid folder: " + folder + "\n")
        return
    else:
        convertBook()   # converts the pieces in the current folder

# This method is called to convert the pieces in the *current folder* to USFM
def convertBook():
    # Copies bookId.usfm to main .usfm file.
    try:
        introFile = io.open("bookId.usfm", "tr", 1, encoding='utf-8')
    except IOError as e:
        sys.stderr.write("Create bookId.usfm file for book heading, then rerun this script.\n")
    else:
        # Opens output USFM file for writing.
        pathComponents = os.path.split(os.getcwd())
        usfmFile = io.open(pathComponents[-1] + ".usfm", "tw", buffering=1, encoding='utf-8', newline='\n')

        for line in introFile:
            usfmFile.write(line)
        introFile.close()

        print "CREATING: " + pathComponents[-1] + ".usfm"
        for directory in os.listdir(os.getcwd()):
            if isChapter(directory):
                sys.stdout.write(directory + " ")
                sys.stdout.flush
                for filename in os.listdir(directory):
                    if isChunk(filename):
                        cleanupChunk(directory, filename)
                        section = convertFile(directory, filename) + u'\n'
                        usfmFile.write(section)
                        restoreOrigFile(directory, filename)
                # Process misnamed 00.txt file last, if it exists
                # if os.access(directory + "/00.txt", os.F_OK):
                #     section = convertFile(directory, "00.txt") + u'\n'
                #     usfmFile.write(section)
        # Wrap up
        usfmFile.close()
        print "\nFINISHED: " + pathComponents[-1]


# Processes each directory and its files one at a time
if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python txt2USFM <folder>\n  Use . for current folder.\n")
    elif sys.argv[1] == 'hard-coded-path':
        convertFolder(r'C:\Users\Larry\Documents\GitHub\Cebuano\ceb_2ti_text_ulb_L3')
    else:
        convertFolder(sys.argv[1])
