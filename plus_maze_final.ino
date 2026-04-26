// ============================================================
// Automated Four-Arm Elevated Plus Maze
// Arduino Uno Firmware — Tinkercad Compatible
//
// Circuit (repeat for each arm):
//   5V → FSR → junction → Analog Pin (A0/A1/A2/A3)
//                  |
//                10kΩ
//                  |
//                 GND
//
// A0 = Arm 1 (Closed)
// A1 = Arm 2 (Closed)
// A2 = Arm 3 (Open)
// A3 = Arm 4 (Open)
// ============================================================

const int NUM_ARMS     = 4;
const int PINS[4]      = {A0, A1, A2, A3};
const int THRESHOLD    = 200;  // ADC value above this = arm occupied
const int DEBOUNCE_MS  = 50;   // ms to wait before confirming state change
const int SAMPLE_MS    = 20;   // main loop delay

bool armState[4]            = {false, false, false, false};
bool lastRawState[4]        = {false, false, false, false};
unsigned long debounceTimer[4] = {0, 0, 0, 0};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < NUM_ARMS; i++) {
    pinMode(PINS[i], INPUT);
  }
  Serial.println("MAZE_READY");
}

void loop() {
  unsigned long now = millis();

  for (int i = 0; i < NUM_ARMS; i++) {
    int val          = analogRead(PINS[i]);
    bool rawOccupied = (val > THRESHOLD);

    // If raw state changed, reset debounce timer
    if (rawOccupied != lastRawState[i]) {
      lastRawState[i]   = rawOccupied;
      debounceTimer[i]  = now;
    }

    // Only confirm state change after debounce period
    if ((now - debounceTimer[i]) >= DEBOUNCE_MS) {
      if (rawOccupied != armState[i]) {
        armState[i] = rawOccupied;

        // Send event over serial
        Serial.print("ARM");
        Serial.print(i + 1);
        if (armState[i]) {
          Serial.println("_ENTER");
        } else {
          Serial.println("_EXIT");
        }
      }
    }
  }

  delay(SAMPLE_MS);
}
