# Automated-Four-Arm-Elevated-Plus-Maze

An open-architecture, automated behavioral scoring system for the Elevated Plus Maze (EPM) — achieving millisecond-precision event detection, eliminating observer bias, and producing analysis-ready datasets at a fraction of commercial cost.

---

## Overview

This system replaces manual/video-based EPM scoring with a pressure-sensor array and microcontroller-based data acquisition pipeline. Four FSR sensors detect rodent arm entry and exit events in real time, which are timestamped and logged by a Python host application.

> **Patent Status:** Invention disclosure filed  
> **Application Area:** Behavioral Neuroscience / Anxiety Research / Pharmacology

---

## How It Works

Four force-sensitive resistors (FSRs) sit beneath each maze arm in voltage divider circuits:

```
5V → FSR → Analog Pin (A0–A3) → 10kΩ Pulldown → GND
```

The Arduino firmware continuously samples all channels, applies a threshold to classify each arm as occupied or unoccupied, and transmits state-transition events (`ARM1_ENTER`, `ARM2_EXIT`) over USB serial. A debounce delay suppresses false triggers.

The Python host application receives these events, assigns system-clock timestamps, pairs entry/exit events to compute per-arm durations, and exports structured CSVs ready for statistical software.

---

## Hardware

| Component | Quantity | Purpose |
|---|---|---|
| Arduino Uno | 1 | Microcontroller |
| Force Sensitive Resistor (FSR) | 4 | One per maze arm |
| 10kΩ Resistor | 4 | Voltage divider pulldown |
| Breadboard + Jumper wires | 1 set | Circuit assembly |
| USB Cable | 1 | Serial communication to PC |

**Pin Mapping:**

| FSR | Arduino Pin | Arm Type |
|---|---|---|
| FSR 1 | A0 | Closed |
| FSR 2 | A1 | Closed |
| FSR 3 | A2 | Open |
| FSR 4 | A3 | Open |

---

## Project Structure

```
├── plus_maze_final.ino     # Arduino firmware
├── maze_logger.py          # Python host application
├── circuit_diagram.png     # Tinkercad circuit diagram
└── README.md
```

---

## Getting Started

### Arduino Setup
1. Open `plus_maze_final.ino` in Arduino IDE
2. Select **Board:** Arduino Uno, **Port:** your COM port
3. Upload to Arduino

### Python Setup
```bash
pip install pyserial
```

Edit `maze_logger.py` and set your port:
```python
PORT = "COM3"   # Windows
# PORT = "/dev/ttyUSB0"  # Linux/Mac
```

Run:
```bash
python maze_logger.py
```

---

## Output

**Real-time serial events:**
```
MAZE_READY
ARM1_ENTER
ARM1_EXIT
ARM3_ENTER
ARM3_EXIT
```

**CSV log** (`maze_output/maze_session_YYYYMMDD_HHMMSS.csv`):

| Timestamp | Event | Arm | ArmType | Duration_s |
|---|---|---|---|---|
| 4.231 | ENTER | 1 | CLOSED | |
| 9.847 | EXIT | 1 | CLOSED | 5.616 |

**Summary report** includes:
- Time spent per arm (seconds)
- Total entries per arm
- % Open arm time
- Anxiety index
- Latency to first open arm entry

---

##  Behavioral Metrics

| Metric | Description |
|---|---|
| Time per arm | Cumulative seconds in each arm |
| Entry count | Total entries per arm |
| % Open arm time | Open arm time / total arm time × 100 |
| Anxiety index | 1 − (open arm time / total arm time) |
| Latency to open arm | Time from start to first open arm entry |

---

## Key Technical Decisions

**FSRs over IR beam-break sensors** — detect actual weight on the arm surface rather than inferring position, reducing ambiguity at arm junctions.

**Event-driven serial messaging** — transmits only on state transitions instead of continuous streaming, minimising bandwidth and keeping logging simple.

**Debounce delay** — 50ms stabilisation window eliminates false triggers from vibration or partial contact.

---

##  Citation

If you use this system in your research, please cite:

> Automated Four-Arm Pressure-Sensor Based Elevated Plus Maze System. Invention disclosure filed, 2024.

---

## 🙋 Author

Developed as part of open-architecture behavioral neuroscience instrumentation research.
