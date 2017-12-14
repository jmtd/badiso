#!/usr/bin/python
# -*- coding: utf-8 -*-

# proof-of-concept markupper on top of an ISO list tool

import subprocess
import re
import sys

# lowest numbered LBA (a directory probably) will likely give us our block offset

iso="archive_26_08_2000_joejon.iso"

if len(sys.argv) > 1:
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

def check_file_status(fsize, lba, fname):
    fstart = lba*2048
    fend   = fstart + fsize
    fstatus = '!' # missing/unknown. ? would be better but used for non-tried block

    for pos,size,status in triplets:
        bstart = pos
        bend   = bstart + size

        # does this file start in this block
        if (fstart >= bstart) and (fstart <= bend):
            if fstatus == "!" and status == good_block:
                fstatus = "✔"
            if status != good_block:
                fstatus = "✗"

        # does this file end in this block
        if (fend <= bend) and (fend >= bstart):
            if fstatus == "!" and status == good_block:
                fstatus = "✔"
            if status != good_block:
                fstatus = "✗"

    print("{} {}".format(fstatus,fname))

def markup_isoinfo_output():
    output = subprocess.Popen(['isoinfo', '-lJ', '-i', iso], stdout=subprocess.PIPE).communicate()[0]
    for line in output.splitlines():
        if not line or line[:1] not in "d-":
            continue
        # ----------   0    0    0        10565946 Nov 26 2004 [  31388 00]  filename.xyz;1
        md = re.match(r'.---------\s+\d+\s+\d+\s+\d+\s+(\d+)\s+... .. .... \[\s*(\d+)\s+\d+\]  (.*)$', line)
        if not md:
            print "didn't match: {}".format(line)
            sys.exit(1)
        fsize, lba, fname = md.groups()
        check_file_status(int(fsize), int(lba), fname)

def markup_xorriso_output():
    output = subprocess.Popen(['xorriso', '-read_fs', 'norock', '-indev', iso, '-find', '.', '-exec', 'report_lba'], stdout=subprocess.PIPE).communicate()[0]
    for line in output.splitlines():
        if not re.match(r'^File data lba', line):
            continue
        bits = line.split(",")
        startlba = bits[1].strip()
        fsize = bits[3].strip()
        fname = ",".join(bits[4:])[1:-1]
        check_file_status(int(fsize), int(startlba), fname)

#markup_isoinfo_output()
markup_xorriso_output()
