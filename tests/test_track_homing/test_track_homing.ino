#include <Adafruit_NeoPixel.h>

#define LED_PIN    13
#define LED_COUNT  74

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// ------------------------------------------------
// TMC2209
// ------------------------------------------------
const int STEP_PIN = 53;
const int DIR_PIN  = 51;

// ------------------------------------------------
// Buttons
// ------------------------------------------------
const int FORWARD_BUTTON = 43;
const int STOP_BUTTON    = 41;
const int SLOWER_BUTTON  = 39;
const int FASTER_BUTTON  = 37;
const int REVERSE_BUTTON = 35;

// ------------------------------------------------
// Limit switches: pin -> switch -> GND, pressed = LOW
// ⚠ GUESSED pins (the cabinet's pins.h, track 1). Change to where yours are wired.
// ------------------------------------------------
const int HOME_SWITCH = 25;   // start of the track
const int END_SWITCH  = 23;   // end of the track

// DIR level that moves the carriage TOWARD the home switch.
// LOW = the REVERSE button's direction. If homing runs into the
// END switch, it stops with a FAULT telling you to flip this to HIGH.
const int HOME_DIR = LOW;

// ------------------------------------------------
// Homing
// ------------------------------------------------
const unsigned long HOMING_STEP_DELAY = 3000;   // slow and safe
const unsigned long HOMING_TIMEOUT_MS = 30000;  // give up after 30 s
const int BACKOFF_STEPS = 100;                  // step off the switch after touching it

// Measuring the track: drive home -> end once and count the steps
const unsigned long MEASURE_STEP_DELAY = 1500;
const unsigned long MEASURE_TIMEOUT_MS = 60000;  // give up after 60 s

bool faulted = false;
long position = 0;      // steps from home, 0 = just off the home switch
long maxPosition = 0;   // just off the end switch, found by measureTrack()

// ------------------------------------------------
// Motor
// ------------------------------------------------
bool motorRunning = false;

const int FORWARD = 1;
const int REVERSE = 0;

int motorDirection = FORWARD;

// Speed level: 1 - 10
int speedLevel = 5;

// Step timing
unsigned long stepDelay = 1500;
unsigned long lastStepTime = 0;

// ------------------------------------------------
// Previous button states
// ------------------------------------------------
int lastForwardState = HIGH;
int lastStopState = HIGH;
int lastSlowerState = HIGH;
int lastFasterState = HIGH;
int lastReverseState = HIGH;


void setup() {

  Serial.begin(9600);

  // ------------------------------------------------
  // Motor
  // ------------------------------------------------
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);

  // ------------------------------------------------
  // Buttons
  // ------------------------------------------------
  pinMode(FORWARD_BUTTON, INPUT_PULLUP);
  pinMode(STOP_BUTTON, INPUT_PULLUP);
  pinMode(SLOWER_BUTTON, INPUT_PULLUP);
  pinMode(FASTER_BUTTON, INPUT_PULLUP);
  pinMode(REVERSE_BUTTON, INPUT_PULLUP);

  // Limit switches
  pinMode(HOME_SWITCH, INPUT_PULLUP);
  pinMode(END_SWITCH, INPUT_PULLUP);

  // Start direction as forward
  digitalWrite(DIR_PIN, HIGH);

  // Calculate starting speed
  updateSpeed();

  // ------------------------------------------------
  // NeoPixels
  // ------------------------------------------------
  strip.begin();
  strip.setBrightness(80);
  strip.show();

  Serial.println("------------------------");
  Serial.println("TRACK TEST READY");
  Serial.println("------------------------");
  Serial.print("Starting Speed Level: ");
  Serial.println(speedLevel);

  // ------------------------------------------------
  // Startup sequence: report switches, then home
  // ------------------------------------------------
  delay(2000);   // time to open Serial Monitor
  Serial.print("Home switch (");
  Serial.print(HOME_SWITCH);
  Serial.println(pressed(HOME_SWITCH) ? "): PRESSED" : "): open");
  Serial.print("End switch  (");
  Serial.print(END_SWITCH);
  Serial.println(pressed(END_SWITCH) ? "): PRESSED" : "): open");

  if (home() && measureTrack() && goTo(0)) {
    setColor(0, 60, 0);   // green = ready
    Serial.println("------------------------");
    Serial.print("READY - track is ");
    Serial.print(maxPosition);
    Serial.println(" steps long");
    Serial.println("------------------------");
  }
}


void loop() {

  // Motor stays off after a fault until the Giga is reset
  if (faulted) return;

  // ------------------------------------------------
  // Read buttons
  // ------------------------------------------------
  int forwardState = digitalRead(FORWARD_BUTTON);
  int stopState = digitalRead(STOP_BUTTON);
  int slowerState = digitalRead(SLOWER_BUTTON);
  int fasterState = digitalRead(FASTER_BUTTON);
  int reverseState = digitalRead(REVERSE_BUTTON);


  // ------------------------------------------------
  // FORWARD
  // ------------------------------------------------
  if (lastForwardState == HIGH && forwardState == LOW) {

    motorRunning = false;
    delay(50);

    motorDirection = FORWARD;
    digitalWrite(DIR_PIN, HIGH);

    delay(10);

    motorRunning = true;

    Serial.println("FORWARD button pressed");
    Serial.println("Motor running FORWARD");
  }


  // ------------------------------------------------
  // STOP
  // ------------------------------------------------
  if (lastStopState == HIGH && stopState == LOW) {

    motorRunning = false;

    Serial.println("STOP button pressed");
    Serial.println("Motor STOPPED");
    printPosition();
  }


  // ------------------------------------------------
  // SLOWER
  // ------------------------------------------------
  if (lastSlowerState == HIGH && slowerState == LOW) {

    if (speedLevel > 1) {
      speedLevel--;
    }

    updateSpeed();

    Serial.println("SLOWER button pressed");
    Serial.print("Speed Level: ");
    Serial.println(speedLevel);
  }


  // ------------------------------------------------
  // FASTER
  // ------------------------------------------------
  if (lastFasterState == HIGH && fasterState == LOW) {

    if (speedLevel < 10) {
      speedLevel++;
    }

    updateSpeed();

    Serial.println("FASTER button pressed");
    Serial.print("Speed Level: ");
    Serial.println(speedLevel);
  }


  // ------------------------------------------------
  // REVERSE
  // ------------------------------------------------
  if (lastReverseState == HIGH && reverseState == LOW) {

    motorRunning = false;
    delay(50);

    motorDirection = REVERSE;
    digitalWrite(DIR_PIN, LOW);

    delay(10);

    motorRunning = true;

    Serial.println("REVERSE button pressed");
    Serial.println("Motor running REVERSE");
  }


  // ------------------------------------------------
  // Save button states
  // ------------------------------------------------
  lastForwardState = forwardState;
  lastStopState = stopState;
  lastSlowerState = slowerState;
  lastFasterState = fasterState;
  lastReverseState = reverseState;


  // ------------------------------------------------
  // STEPPER MOTOR
  // ------------------------------------------------
  if (motorRunning) {

    int dirLevel = (motorDirection == FORWARD) ? HIGH : LOW;
    bool towardHome = (dirLevel == HOME_DIR);

    // Soft limit: stop at the measured ends before touching a switch
    if ((towardHome && position <= 0) || (!towardHome && position >= maxPosition)) {
      motorRunning = false;
      Serial.println(towardHome ? "At HOME end - stopped" : "At END - stopped");
      printPosition();
      return;
    }

    // Hard limit: the switch is the backup if the count ever drifts
    int limit = towardHome ? HOME_SWITCH : END_SWITCH;
    if (pressed(limit)) {
      motorRunning = false;
      Serial.println(towardHome ? "Hit HOME switch - stopped (count had drifted)" : "Hit END switch - stopped (count had drifted)");
      position = towardHome ? 0 : maxPosition;   // re-sync the count
      printPosition();
      return;
    }

    unsigned long currentTime = micros();

    if (currentTime - lastStepTime >= stepDelay) {

      lastStepTime = currentTime;

      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(5);
      digitalWrite(STEP_PIN, LOW);

      position += towardHome ? -1 : 1;
    }
  }
}


// ------------------------------------------------
// Limit switch / button helper (pull-up, pressed = LOW)
// ------------------------------------------------
bool pressed(int pin) {
  return digitalRead(pin) == LOW;
}


void stepOnce(unsigned long wait) {
  digitalWrite(STEP_PIN, HIGH);
  delayMicroseconds(5);
  digitalWrite(STEP_PIN, LOW);
  delayMicroseconds(wait);
}


void setColor(int r, int g, int b) {
  strip.fill(strip.Color(r, g, b));
  strip.show();
}


// ------------------------------------------------
// Stop everything and say why
// ------------------------------------------------
void fault(const char *why) {
  motorRunning = false;
  faulted = true;
  setColor(60, 0, 0);   // red = fault
  Serial.print("FAULT: ");
  Serial.println(why);
  Serial.println("Fix it, then press RESET on the Giga to home again.");
}


// ------------------------------------------------
// Homing: creep toward the home switch, then back off it
// ------------------------------------------------
bool home() {

  Serial.println("Homing...");
  setColor(0, 0, 60);   // blue = homing

  if (pressed(HOME_SWITCH) && pressed(END_SWITCH)) {
    fault("both limit switches read PRESSED - check switch wiring");
    return false;
  }

  digitalWrite(DIR_PIN, HOME_DIR);
  delay(5);

  unsigned long start = millis();
  bool endWasPressed = pressed(END_SWITCH);   // fine if we start parked on it

  while (!pressed(HOME_SWITCH)) {

    bool endNow = pressed(END_SWITCH);
    if (endNow && !endWasPressed) {
      fault("ran into the END switch while homing - flip HOME_DIR");
      return false;
    }
    endWasPressed = endNow;

    if (pressed(STOP_BUTTON)) {
      fault("homing cancelled with STOP");
      return false;
    }

    if (millis() - start > HOMING_TIMEOUT_MS) {
      fault("home switch never reached in 30 s - check switch and motor");
      return false;
    }

    stepOnce(HOMING_STEP_DELAY);
  }

  Serial.println("Home switch hit, backing off");

  digitalWrite(DIR_PIN, !HOME_DIR);
  delay(5);
  for (int i = 0; i < BACKOFF_STEPS; i++) {
    stepOnce(HOMING_STEP_DELAY);
  }

  if (pressed(HOME_SWITCH)) {
    fault("still on the home switch after backing off - raise BACKOFF_STEPS");
    return false;
  }

  position = 0;
  digitalWrite(DIR_PIN, HIGH);   // back to the default: forward
  return true;
}


// ------------------------------------------------
// Measure the track: from home, run to the end switch counting steps
// ------------------------------------------------
bool measureTrack() {

  Serial.println("Measuring track...");

  digitalWrite(DIR_PIN, !HOME_DIR);
  delay(5);

  unsigned long start = millis();

  while (!pressed(END_SWITCH)) {

    if (pressed(HOME_SWITCH)) {
      fault("hit the HOME switch while measuring - check switch wiring");
      return false;
    }

    if (pressed(STOP_BUTTON)) {
      fault("measuring cancelled with STOP");
      return false;
    }

    if (millis() - start > MEASURE_TIMEOUT_MS) {
      fault("end switch never reached in 60 s - check switch and motor");
      return false;
    }

    stepOnce(MEASURE_STEP_DELAY);
    position++;
  }

  Serial.print("End switch hit at ");
  Serial.print(position);
  Serial.println(" steps, backing off");

  digitalWrite(DIR_PIN, HOME_DIR);
  delay(5);
  for (int i = 0; i < BACKOFF_STEPS; i++) {
    stepOnce(MEASURE_STEP_DELAY);
    position--;
  }

  if (pressed(END_SWITCH)) {
    fault("still on the end switch after backing off - raise BACKOFF_STEPS");
    return false;
  }

  maxPosition = position;
  return true;
}


// ------------------------------------------------
// Drive to an exact step position (used to return home after measuring)
// ------------------------------------------------
bool goTo(long target) {

  bool towardHome = target < position;
  digitalWrite(DIR_PIN, towardHome ? HOME_DIR : !HOME_DIR);
  delay(5);

  while (position != target) {

    if (pressed(STOP_BUTTON)) {
      fault("move cancelled with STOP");
      return false;
    }

    stepOnce(MEASURE_STEP_DELAY);
    position += towardHome ? -1 : 1;
  }

  digitalWrite(DIR_PIN, HIGH);   // back to the default: forward
  return true;
}


// ------------------------------------------------
// "Position: 1234 / 5000 steps (24%)"
// ------------------------------------------------
void printPosition() {
  Serial.print("Position: ");
  Serial.print(position);
  Serial.print(" / ");
  Serial.print(maxPosition);
  Serial.print(" steps (");
  Serial.print(maxPosition > 0 ? position * 100 / maxPosition : 0);
  Serial.println("%)");
}


// ------------------------------------------------
// Convert speed level into motor step delay
// ------------------------------------------------
void updateSpeed() {

  // Level 1 = slow
  // Level 10 = fast

  stepDelay = map(speedLevel, 1, 10, 5000, 500);
}


// ------------------------------------------------
// NeoPixel Rainbow
// ------------------------------------------------
void rainbowCycle(int waitTime) {

  for (long firstPixelHue = 0;
       firstPixelHue < 5 * 65536;
       firstPixelHue += 256) {

    for (int i = 0; i < strip.numPixels(); i++) {

      int pixelHue =
        firstPixelHue +
        (i * 65536L / strip.numPixels());

      strip.setPixelColor(
        i,
        strip.gamma32(strip.ColorHSV(pixelHue))
      );
    }

    strip.show();
    delay(waitTime);
  }
}
