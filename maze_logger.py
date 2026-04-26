# ============================================================
# Automated Four-Arm Elevated Plus Maze
# Python Host Application — Serial Logger & Analyzer
# ============================================================

import serial
import time
import csv
import os
from datetime import datetime

# ── CONFIGURATION ────────────────────────────────────────────
PORT        = "COM3"       # Change to your Arduino port (e.g. /dev/ttyUSB0 on Linux)
BAUD_RATE   = 9600
NUM_ARMS    = 4
OUTPUT_DIR  = "maze_output"

# ── SETUP OUTPUT ─────────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)
session_id  = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path    = os.path.join(OUTPUT_DIR, f"maze_session_{session_id}.csv")
summary_path = os.path.join(OUTPUT_DIR, f"maze_summary_{session_id}.txt")

# ── STATE TRACKING ───────────────────────────────────────────
entry_times     = [None] * (NUM_ARMS + 1)   # index 1-4
durations       = [0.0]  * (NUM_ARMS + 1)   # cumulative seconds per arm
entry_counts    = [0]    * (NUM_ARMS + 1)   # total entries per arm
first_open_entry = None                      # latency to first open arm (Arms 3 & 4)

# Open arms are defined as Arm 3 and Arm 4 (standard EPM convention)
OPEN_ARMS   = {3, 4}
CLOSED_ARMS = {1, 2}

# ── HELPER ───────────────────────────────────────────────────
def arm_type(arm_num):
    return "OPEN" if arm_num in OPEN_ARMS else "CLOSED"

def print_banner():
    print("=" * 55)
    print("  Automated Four-Arm Elevated Plus Maze Logger")
    print("=" * 55)
    print(f"  Session ID : {session_id}")
    print(f"  Port       : {PORT}")
    print(f"  Output     : {csv_path}")
    print("=" * 55)
    print("  Press Ctrl+C to stop recording and export summary.")
    print("=" * 55)

# ── MAIN ─────────────────────────────────────────────────────
def main():
    global first_open_entry

    print_banner()

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
        print(f"\n[INFO] Connected to Arduino on {PORT}")
        time.sleep(2)  # Allow Arduino to reset

        # Wait for MAZE_READY
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line == "MAZE_READY":
                print("[INFO] Arduino ready. Recording started.\n")
                break

        # Open CSV and start recording
        with open(csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "Event", "Arm", "ArmType", "Duration_s"])

            session_start = time.time()

            while True:
                raw = ser.readline().decode("utf-8", errors="ignore").strip()
                if not raw:
                    continue

                ts = time.time()
                elapsed = ts - session_start

                # Parse event: ARM1_ENTER / ARM2_EXIT etc.
                if raw.startswith("ARM") and "_" in raw:
                    try:
                        parts       = raw.split("_")
                        arm_num     = int(parts[0].replace("ARM", ""))
                        event_type  = parts[1]  # ENTER or EXIT
                    except (ValueError, IndexError):
                        print(f"[WARN] Unrecognised message: {raw}")
                        continue

                    atype = arm_type(arm_num)

                    if event_type == "ENTER":
                        entry_times[arm_num] = ts
                        entry_counts[arm_num] += 1

                        # Latency to first open arm entry
                        if arm_num in OPEN_ARMS and first_open_entry is None:
                            first_open_entry = elapsed

                        writer.writerow([
                            f"{elapsed:.3f}", "ENTER", arm_num, atype, ""
                        ])
                        csvfile.flush()
                        print(f"[{elapsed:8.3f}s]  ARM{arm_num} ENTER  ({atype})")

                    elif event_type == "EXIT":
                        duration = ""
                        if entry_times[arm_num] is not None:
                            duration = ts - entry_times[arm_num]
                            durations[arm_num] += duration
                            entry_times[arm_num] = None
                            duration = f"{duration:.3f}"

                        writer.writerow([
                            f"{elapsed:.3f}", "EXIT", arm_num, atype, duration
                        ])
                        csvfile.flush()
                        print(f"[{elapsed:8.3f}s]  ARM{arm_num} EXIT   ({atype})  dur={duration}s")

    except serial.SerialException as e:
        print(f"\n[ERROR] Serial connection failed: {e}")
        print("        Check PORT setting and that Arduino is connected.")

    except KeyboardInterrupt:
        print("\n\n[INFO] Recording stopped by user.")

    finally:
        try:
            ser.close()
        except Exception:
            pass
        export_summary(session_start if 'session_start' in dir() else time.time())

# ── SUMMARY EXPORT ───────────────────────────────────────────
def export_summary(session_start):
    total_time   = time.time() - session_start
    total_open   = sum(durations[a] for a in OPEN_ARMS)
    total_closed = sum(durations[a] for a in CLOSED_ARMS)
    recorded     = total_open + total_closed

    pct_open   = (total_open   / recorded * 100) if recorded > 0 else 0
    pct_closed = (total_closed / recorded * 100) if recorded > 0 else 0

    # Anxiety index: 1 - (open arm time / total arm time)
    anxiety_index = 1 - (total_open / recorded) if recorded > 0 else None

    lines = []
    lines.append("=" * 55)
    lines.append("  ELEVATED PLUS MAZE — SESSION SUMMARY")
    lines.append("=" * 55)
    lines.append(f"  Session ID      : {session_id}")
    lines.append(f"  Total Duration  : {total_time:.1f} s")
    lines.append("")
    lines.append("  PER-ARM METRICS")
    lines.append("  " + "-" * 45)
    for i in range(1, NUM_ARMS + 1):
        atype = arm_type(i)
        lines.append(
            f"  Arm {i} ({atype:6s}) : "
            f"entries={entry_counts[i]:3d}  "
            f"time={durations[i]:7.2f}s"
        )
    lines.append("")
    lines.append("  AGGREGATE METRICS")
    lines.append("  " + "-" * 45)
    lines.append(f"  Open Arm Time   : {total_open:.2f} s  ({pct_open:.1f}%)")
    lines.append(f"  Closed Arm Time : {total_closed:.2f} s  ({pct_closed:.1f}%)")
    lines.append(
        f"  Anxiety Index   : "
        f"{anxiety_index:.3f}" if anxiety_index is not None else "  Anxiety Index   : N/A"
    )
    if first_open_entry is not None:
        lines.append(f"  Latency (open)  : {first_open_entry:.3f} s")
    else:
        lines.append("  Latency (open)  : No open arm entry recorded")
    lines.append("=" * 55)
    lines.append(f"  CSV saved to    : {csv_path}")
    lines.append("=" * 55)

    summary_text = "\n".join(lines)
    print("\n" + summary_text)

    with open(summary_path, "w") as f:
        f.write(summary_text + "\n")

    print(f"\n[INFO] Summary saved to {summary_path}")

# ── ENTRY POINT ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
