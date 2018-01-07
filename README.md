# BadISO

*BadISO* is a tool to aid investigating what files can be recovered from
ISO9660 filesytem images that might be damaged or incomplete. It outputs
a file listing with indications as to which files are intact, based on a
GNU ddrescue map file corresponding to the image.

## Example output

    …
    ✔ ./joes/allstars.zip
    ✗ ./joes/ban.gif
    ✔ ./joes/eur-mgse.zip
    ✔ ./joes/gold.zip
    ✗ ./joes/graphhack.txt
    ✗ ./joes/machines.zip
    ✔ ./joes/md.zip
    ✔ ./joes/midi.zip
    ✗ ./joes/mnc-driv.zip
    ✔ ./joes/nes.zip
    …

## Dependencies

You need a GNU ddrescue map file for every ISO9660 image you wish to inspect.

badiso currently depends upon xorriso to work. There is some code to use
isoinfo from cdrkit instead, but it requires some editing to activate. The
plan is to remove both dependencies in future.

NOTE: for damaged images, versions of xorriso >= 1.4.8 are recommended; there
are some bugs in 1.4.6 that prevent it from extracting a file list in some
circumstances.

## Future

Remove dependency on an external ISO9660 tool (xorriso, isoinfo, etc.)

Configurable output (optional colour); filtering (show only good/bad files)

Rewrite in Haskell.

## See also

 * GNU ddrescue
 * ddrescueview
 * xorriso

## Author

Jonathan Dowland
<jon@dow.land>
<https://jmtd.net/>
