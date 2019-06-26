# sbc-assembly

For initial environment setup:

1. Install Vienna RNA (see https://anaconda.org/bioconda/viennarna).
2. Install NCBI Blast (see https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download).

## LCR2

This script assumes that PlasmidGenie has been used to add the necessary
entries into the ICE database.

1. Amend the script `lcr2.sh`, updating ICE URL, username and password, as well
as ICE ids to assemble. The optional three-letter code for naming the worklist,
currently with a default of `LCR`, may also be updated.

2. Ensure that all necessary source plates are in the `data/plates` directory.
Plates that are required include those containing plasmid parts (i.e. individual
parts within the plasmids, typically that which is returned from Twist), and
those containing primers (these primers are *not* held in ICE, and must be
specified here, using the naming convention of `[PART_PLASMID_ID]_P` and
`[PART_PLASMID_ID]_NP` for phosphorylated and non-phosphorylated primers
respectively. Plates can be defined in one of two formats (see
`data/plates/12135272.csv` and `data/plates/11276738.csv`) for examples of each
format.

3. Run the script through the command: `bash lcr2.sh`.

4. Worklists and plates for each of the six steps in the full LCR assembly
process with be found in the `./out` directory, in a subdirectory named
`[date]LCR`.

The worklists cover each of the six sequential steps in a full automated LCR v2
assembly, and are generated in numbered directories. The steps are:

1. Part PCR. The PCR step required to PCR the part from its parent plasmid
(typically, the plasmid ordered by Twist). Note that both parts and plasmids
should have their own ICE id if they have been generated correctly through
PlasmidGenie). See for example https://ice.synbiochem.co.uk/entry/10041 and 
https://ice.synbiochem.co.uk/entry/10040. SBC010040 corresponds to the Part,
and SBC010041 corresponds to the parent Plasmid. This step essentially PCRs Part
SBC010040 from its parent Plasmid SBC010041.

2. Part digest. This step performs a digest on the Parts generated in the
previous step (e.g. SBC010040) to remove unnecessary flanking sequence at the
5' and 3' ends.

3. Part QC. This step takes the digested parts from Step 2 and prepares them for
(optional) analysis on the fragment analyser.

4. Domino pooling. This step pools together all dominoes required for the LCR
of each pathway. If, for example, a design contains two pathways, two domino
pools will be generated.

5. Part PCR pooling.

6. LCR writer. This step performs the LCR assembly of each pathway in the
design, using digested parts from Step 2, and domino pools from Step 4.

## LCR3

Very early code to begin to implement new LCR version 3 method.

1. Run the script through the command: `bash lcr3.sh`.

2. Output is in the form of a number of csv files in the `.out/lcr3`.

Four files are generated:

1. `design_parts.csv`. This shows each design, along with the individual parts
which need to be LCRed together to make the full design.

2. `part_primers.csv`. This shows each individual part and the primer required
to PCR the part from its parent plasmid (i.e. the plasmid which is purchased
from Twist).

3. `pair_dominoes.csv`. This shows the part pairs (each pair of parts that
need to be LCRed together) and the domino that it required for the LCR.

4. `summary.txt`, which summarises the previous three files in a single text file.

The files `part_primers.csv` and `pair_dominoes.csv` essentially contain the
"shopping list" for what needs to be bought from Twist.

As mentioned, this is very early code, and will have to be much further
developed to integrate with ICE and generate worklists, etc., as is currently
done for LCR v2. Depending upon the priorities of the centre, this work may or
may not be worth doing.


## ENZYME SCREENING

This script reads a manually-generated screening list, and from which generates
appropriate worklists.

See `data/enz_scr/enz_scr.csv` for an example of such a screening list.

1. Amend the script `enz_scr.sh` to update the location of the enzyme screening
list, and the optional three-letter code for naming the worklist, which
currently has a default of `ENZ`.

2. Run the script through the command: `bash enz_scr.sh`.
