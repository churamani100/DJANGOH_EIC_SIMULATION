#!/usr/bin/env python3
import sys
import math
import argparse
import csv

E_ELECTRON = 9.0
E_PROTON   = 275.0
M_ELECTRON = 0.00051099895
M_PROTON   = 0.93827208816

def is_event_summary(tokens):
    if len(tokens) < 31:
        return False
    try:
        return int(tokens[0]) == 0
    except Exception:
        return False

def is_particle_line(tokens):
    if len(tokens) < 14:
        return False
    try:
        int(tokens[0])
        int(tokens[1])
        int(tokens[2])
        float(tokens[6])
        float(tokens[7])
        float(tokens[8])
        float(tokens[9])
        float(tokens[10])
        return True
    except Exception:
        return False

def read_djangoh_events(infile, max_events=None):
    events = []
    current = None

    with open(infile, "r", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("=") or line.startswith("DJANGOH") or line.startswith("I,"):
                continue

            toks = line.split()

            if is_event_summary(toks):
                if current is not None:
                    events.append(current)
                    if max_events is not None and len(events) >= max_events:
                        return events

                current = {
                    "evnum": int(toks[1]),
                    "y": float(toks[8]),
                    "q2": float(toks[9]),
                    "x": float(toks[10]),
                    "w2": float(toks[11]),
                    "truey": float(toks[13]),
                    "trueq2": float(toks[14]),
                    "truex": float(toks[15]),
                    "truew2": float(toks[16]),
                    "sigtot": float(toks[18]),
                    "err_sigtot": float(toks[19]),
                    "g1cc": float(toks[28]),
                    "g5cc": float(toks[29]),
                    "particles": []
                }
                continue

            if current is not None and is_particle_line(toks):
                status = int(toks[1])
                pdg    = int(toks[2])

                px = float(toks[6])
                py = float(toks[7])
                pz = float(toks[8])
                e  = float(toks[9])
                m  = float(toks[10])

                # Keep only stable final-state particles for detector simulation.
                # DJANGOH/JETSET stable particles have status = 1 in this file.
                if status == 1:
                    current["particles"].append((pdg, px, py, pz, e, m))

    if current is not None and (max_events is None or len(events) < max_events):
        events.append(current)

    return events

def write_hepmc2(events, outfile):
    with open(outfile, "w") as out:
        out.write("HepMC::Version 2.06.09\n")
        out.write("HepMC::IO_GenEvent-START_EVENT_LISTING\n")

        for iev, ev in enumerate(events, start=1):
            particles = ev["particles"]

            # HepMC2 E-line format:
            # E event_number mpi scale alphaQCD alphaQED signal_process_id
            #   signal_vertex_barcode n_vertices beam1_barcode beam2_barcode
            #   random_states_size weights_size weight
            scale = math.sqrt(max(ev["trueq2"], 0.0))

            event_number = iev
            mpi = -1
            alpha_qcd = -1.0
            alpha_qed = -1.0
            signal_process_id = 0
            signal_vertex_barcode = -1
            n_vertices = 1
            beam1_barcode = 1
            beam2_barcode = 2
            random_states_size = 0
            weights_size = 1
            weight = 1.0

            out.write(
                f"E {event_number} {mpi} {scale:.8e} {alpha_qcd:.8e} {alpha_qed:.8e} "
                f"{signal_process_id} {signal_vertex_barcode} {n_vertices} "
                f"{beam1_barcode} {beam2_barcode} {random_states_size} "
                f"{weights_size} {weight:.8e}\n"
            )

            out.write('N 1 "event_weight"\n')
            out.write("U GEV MM\n")

            # One interaction vertex at the origin.
            vertex_barcode = -1
            vertex_id = 0
            x = y = z = t = 0.0

            n_incoming_orphans = 2
            n_outgoing = len(particles)
            weights_size_vertex = 0

            out.write(
                f"V {vertex_barcode} {vertex_id} {x:.8e} {y:.8e} {z:.8e} {t:.8e} "
                f"{n_incoming_orphans} {n_outgoing} {weights_size_vertex}\n"
            )

            # Incoming electron and proton.
            # In HepMC, status 3 is often used for documentation/beam particles.
            # Their end_vertex is the interaction vertex barcode (-1).
            out.write(
                f"P 1 11 0.00000000e+00 0.00000000e+00 {-E_ELECTRON:.8e} {E_ELECTRON:.8e} "
                f"{M_ELECTRON:.8e} 4 0.00000000e+00 0.00000000e+00 {vertex_barcode} 0\n"
            )

            pz_proton = math.sqrt(max(E_PROTON*E_PROTON - M_PROTON*M_PROTON, 0.0))
            out.write(
                f"P 2 2212 0.00000000e+00 0.00000000e+00 {pz_proton:.8e} {E_PROTON:.8e} "
                f"{M_PROTON:.8e} 4 0.00000000e+00 0.00000000e+00 {vertex_barcode} 0\n"
            )

            barcode = 3
            for pdg, px, py, pz, e, m in particles:
                status = 1
                theta = 0.0
                phi = 0.0
                end_vertex = 0
                flow_size = 0

                out.write(
                    f"P {barcode} {pdg} {px:.8e} {py:.8e} {pz:.8e} {e:.8e} {m:.8e} "
                    f"{status} {theta:.8e} {phi:.8e} {end_vertex} {flow_size}\n"
                )
                barcode += 1

        out.write("HepMC::IO_GenEvent-END_EVENT_LISTING\n")

def write_truth_csv(events, csvfile):
    with open(csvfile, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["event", "x", "y", "Q2", "W2", "truex", "truey", "trueQ2", "trueW2", "SIGtot_nb", "errSIGtot_nb", "G1CC", "G5CC", "nStable"])
        for i, ev in enumerate(events, start=1):
            w.writerow([
                i, ev["x"], ev["y"], ev["q2"], ev["w2"],
                ev["truex"], ev["truey"], ev["trueq2"], ev["truew2"],
                ev["sigtot"], ev["err_sigtot"], ev["g1cc"], ev["g5cc"],
                len(ev["particles"])
            ])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_evt")
    ap.add_argument("output_hepmc")
    ap.add_argument("--max", type=int, default=None, help="convert only first N events")
    args = ap.parse_args()

    events = read_djangoh_events(args.input_evt, args.max)

    if not events:
        print("ERROR: no events found")
        sys.exit(1)

    write_hepmc2(events, args.output_hepmc)

    csvfile = args.output_hepmc.replace(".hepmc", "_truth.csv")
    write_truth_csv(events, csvfile)

    print(f"Converted {len(events)} events")
    print(f"Wrote {args.output_hepmc}")
    print(f"Wrote {csvfile}")

if __name__ == "__main__":
    main()
