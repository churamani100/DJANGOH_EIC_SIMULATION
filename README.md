# DJANGOH-HERACLES4.6.10-1.0: Polarized DIS-CC 9x275 Q2-Binned Samples

## Dataset

This repository documents the generation and preprocessing of polarized charged-current DIS samples for EIC production.

Process:

```text
e- + p -> nu_e + X
```

Generator:

```text
DJANGOH/HERACLES 4.6.10
```

Beam configuration:

```text
9 GeV electron x 275 GeV proton
```

Physics process label:

```text
DIS-CC
```

Samples:

```text
pPlus  = proton helicity +1
pMinus = proton helicity -1
```

Final production format:

```text
hepmc3.tree.root
```

Release tag:

```text
DJANGOH-HERACLES4.6.10-1.0
```

This tag follows the requested Case 2 versioning scheme:

```text
<generator version>-<steering/script major.minor>
```

where `DJANGOH-HERACLES4.6.10` is the generator version and `1.0` is the steering/script version.

---

## Repository Contents

```text
cards/9x275/q2_binned/      DJANGOH steering cards
scripts/                    EVT-to-HepMC conversion script
logs/9x275/q2_binned/       DJANGOH log and output summaries
metadata/9x275/q2_binned/   checksums, cross sections, and dataset summary
README.md                   production documentation
.gitignore                  excludes large generated files
```

Large generated files are not committed to GitHub:

```text
*.root
*.hepmc
*_evt.dat
*_smp.dat
*_rnd.dat
```

---

## Q2 Binning and Event Counts

For 9x275, the approximate DIS limit is

```text
s = 4 Ee Ep = 4 x 9 x 275 = 9900 GeV^2
```

With `ymax = 0.95`, the practical maximum is

```text
Q2max ~ 9400 GeV^2
```

Therefore, the attempted `q2_10000to100000` bin was removed because it is outside the physical phase space for 9x275.

Final generated bins:

| Q2 bin [GeV^2] | pPlus events | pMinus events | Total events |
| -------------- | -----------: | ------------: | -----------: |
| 100-1000       |       500000 |        500000 |      1000000 |
| 1000-3000      |       500000 |        500000 |      1000000 |
| 3000-9000      |      1000000 |       1000000 |      2000000 |

Total generated events:

```text
4000000
```

---

## Cross Sections

Corrected total cross sections reported by DJANGOH/HERACLES:

| Q2 bin [GeV^2] | Proton helicity sample | Total cross section [pb] |
| -------------- | ---------------------- | -----------------------: |
| 100-1000       | pPlus                  |                   21.440 |
| 100-1000       | pMinus                 |                   9.5747 |
| 1000-3000      | pPlus                  |                   10.321 |
| 1000-3000      | pMinus                 |                   3.0338 |
| 3000-9000      | pPlus                  |                   1.2666 |
| 3000-9000      | pMinus                 |                  0.30165 |

These cross sections should be used for luminosity scaling and for combining the Q2-binned samples.

---

## Steering Cards

Final steering cards are stored in:

```text
cards/9x275/q2_binned/
```

Files:

```text
cc_g5_pPlus_9x275_q2_100to1000.in
cc_g5_pMinus_9x275_q2_100to1000.in
cc_g5_pPlus_9x275_q2_1000to3000.in
cc_g5_pMinus_9x275_q2_1000to3000.in
cc_g5_pPlus_9x275_q2_3000to9000.in
cc_g5_pMinus_9x275_q2_3000to9000.in
```

Main beam settings:

```text
EL-BEAM
            9D0    -1.0D0    -1

PR-BEAM
            275D0   +1.0D0   for pPlus
            275D0   -1.0D0   for pMinus
```

Charged-current DIS is enabled and neutral-current DIS is disabled.

---

## Generation

Generation was performed in:

```text
/w/hallb-scshelf2102/clas12/cpaudel/EIC/g5_djangoh_test/djangoh_q2binned_9x275
```

Example command:

```bash
nohup djangoh < cc_g5_pPlus_9x275_q2_100to1000.in \
  > cc_g5_pPlus_9x275_q2_100to1000.log 2>&1 &
```

The six cards were run independently.

---

## Conversion to HepMC

DJANGOH `_evt.dat` files were converted to HepMC using:

```text
scripts/djangoh_evt_to_hepmc_9x275.py
```

The converter was configured for:

```python
E_ELECTRON = 9.0
E_PROTON   = 275.0
```

Conversion command:

```bash
for f in *_evt.dat; do
  out=${f/_evt.dat/.hepmc}
  python3 ../djangoh_evt_to_hepmc.py "$f" "$out"
done
```

---

## Afterburner

The default system `abconv` did not expose the 9x275 presets. A newer EIC afterburner was built locally from:

```text
https://github.com/eic/afterburner
tag: v0.2.1
```

The source contains the required presets:

```text
ip6_hidiv_275x9
ip6_hiacc_275x9
```

Local build:

```bash
cd /w/hallb-scshelf2102/clas12/cpaudel/EIC/afterburner

cmake -B build -S cpp \
  -DCMAKE_INSTALL_PREFIX=/w/hallb-scshelf2102/clas12/cpaudel/EIC/afterburner/install

cmake --build build -j4
cmake --install build
```

Runtime setup:

```bash
export LD_LIBRARY_PATH=/opt/local/lib:$LD_LIBRARY_PATH
```

Afterburner command:

```bash
AB=/w/hallb-scshelf2102/clas12/cpaudel/EIC/afterburner/install/bin/abconv

for f in *.hepmc; do
  $AB -p ip6_hidiv_275x9 "$f" -o "${f}.ab"
done
```

Only the resulting `*.hepmc3.tree.root` files are production inputs. The `*.hist.root` files are diagnostic afterburner outputs.

---

## Production File Naming

The required naming convention is:

```text
<generator repository release tag>_<physics processes>_<electron momentum>x<proton momentum>_q2_<minimum q2>to<maximum q2>_run<index>.hepmc3.tree.root
```

This dataset uses:

```text
DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpPlus_9x275_q2_<range>_run001.hepmc3.tree.root
DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpMinus_9x275_q2_<range>_run001.hepmc3.tree.root
```

---

## Production Directory Structure

The final files should be placed as:

```text
DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_100to1000/
DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_1000to3000/
DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_3000to9000/
```

Final files:

```text
DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_100to1000/
  DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpPlus_9x275_q2_100to1000_run001.hepmc3.tree.root
  DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpMinus_9x275_q2_100to1000_run001.hepmc3.tree.root
  checksums.sha256

DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_1000to3000/
  DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpPlus_9x275_q2_1000to3000_run001.hepmc3.tree.root
  DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpMinus_9x275_q2_1000to3000_run001.hepmc3.tree.root
  checksums.sha256

DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_3000to9000/
  DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpPlus_9x275_q2_3000to9000_run001.hepmc3.tree.root
  DJANGOH-HERACLES4.6.10-1.0_DIS-CC-polpMinus_9x275_q2_3000to9000_run001.hepmc3.tree.root
  checksums.sha256
```

---

## Checksums

Checksums were generated with:

```bash
for d in DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275/q2_*; do
  sha256sum $d/*.root > $d/checksums.sha256
done
```

Checksum copies are stored in:

```text
metadata/9x275/q2_binned/
```

---

## Validation

Expected final production files:

```bash
find DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275 -name "*.hepmc3.tree.root" | wc -l
```

Expected output:

```text
6
```

Check that no histogram files are included:

```bash
find DIS/CC/DJANGOH-HERACLES4.6.10-1.0/9x275 -name "*.hist.root"
```

Expected output: none.

---

## Contact

Churamani Paudel
New Mexico State University / Jefferson Lab
[paudel.churamani@gmail.com](mailto:paudel.churamani@gmail.com)
