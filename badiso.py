#!/usr/bin/python
# -*- coding: utf-8 -*-

# proof-of-concept markupper on top of an ISO list tool

import subprocess
import re
import sys

if len(sys.argv) != 2:
    sys.stderr.write("usage: {} <file.iso>\n"\
        "\twhere <file.iso> is a partial ISO9660 image\n"\
        "\tand <file.log> is a corresponding ddrescue map file.\n".format(sys.argv[0]))
    sys.exit(1)

iso=sys.argv[1]

good_block = '+'
bad_blocks = '*/-'
non_tried  = '?'

lastblock = 0

# triplets parsed out of the logfile
triplets = []

log = iso.replace("iso","log")
with open(log,"r") as fh:
    for line in fh:
        if line[:1] == "#":
            continue
        bits = line.split()
        if len(bits) != 3:
            continue

        pos,size,status = bits
        triplets.append((int(pos,16), int(size,16), status))

        possible_maxblock = int(pos,16) + int(size,16)
        if possible_maxblock > lastblock:
            lastblock = possible_maxblock

unknown_status = '!' # missing/unknown. ? would be better but used for non-tried block
good_status = "[92m✔[0m"
bad_status  = "[91m✗[0m"

def check_file_status(fsize, lba, fname):
    fstart = lba*2048
    fend   = fstart + fsize
    fstatus = unknown_status

    for pos,size,status in triplets:
        bstart = pos
        bend   = bstart + size

        # does this file start in this block
        if (fstart >= bstart) and (fstart <= bend):
            if fstatus == "!" and status == good_block:
                fstatus = good_status
            if status != good_block:
                fstatus = bad_status

        # does this file end in this block
        if (fend <= bend) and (fend >= bstart):
            if fstatus == "!" and status == good_block:
                fstatus = good_status
            if status != good_block:
                fstatus = bad_status

    print("{} {}".format(fstatus,fname))

def markup_isoinfo_output():
    """Extract a file list from the ISO via isoinfo(1) and check each file's
       status from the ddrescue map.

       This procedure is not currently enabled.
    """
    output = subprocess.Popen(['isoinfo', '-lJ', '-i', iso], stdout=subprocess.PIPE).communicate()[0]
    for line in output.splitlines():
        if not line or line[:1] not in "d-":
            continue
        # ----------   0    0    0        10565946 Nov 26 2004 [  31388 00]  filename.xyz;1
        md = re.match(r'.---------\s+\d+\s+\d+\s+\d+\s+(\d+)\s+... .. .... \[\s*(\d+)\s+\d+\]  (.*)$', line)
        if not md:
            print("didn't match: {}".format(line))
            sys.exit(1)
        fsize, lba, fname = md.groups()
        check_file_status(int(fsize), int(lba), fname)

def build_xorriso_cmd(iso):
    return ['xorriso', '-read_fs', 'norock', '-indev', iso, '-find', '.', '-exec', 'report_lba']

def markup_xorriso_output():
    """Extract a file list from the ISO via xorriso(1) and check each file's
       status from the ddrescue map."""
    output = subprocess.Popen(build_xorriso_cmd(iso), stdout=subprocess.PIPE).communicate()[0]
    for line in output.splitlines():
        if not re.match(r'^File data lba', line): # XXX not python3 compatible
            continue
        bits = line.split(",")
        startlba = bits[1].strip()
        fsize = bits[3].strip()
        fname = ",".join(bits[4:])[2:-3] # strips leading " '" and trailing ";?'" (version)
        check_file_status(int(fsize), int(startlba), fname)

markup_xorriso_output()
