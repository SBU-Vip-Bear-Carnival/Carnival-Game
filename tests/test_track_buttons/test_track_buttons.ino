// -----------------------------
// TMC2209
// -----------------------------
const int STEP_PIN = 3;
const int DIR_PIN  = 4;

// -----------------------------
// Buttons
// -----------------------------
const int GO_BUTTON      = 8;
const int STOP_BUTTON    = 9;
const int SLOWER_BUTTON  = 10;
const int FASTER_BUTTON  = 11;
const int REVERSE_BUTTON = 12;

// -----------------------------
// Motor settings
// -----------------------------
bool motorRunning = false;

// Smaller number = faster
// Larger number  = slower
unsigned long stepDelay = 1500;

// Speed limits
const unsigned long FASTEST_SPEED = 300;
const unsigned long SLOWEST_SPEED = 5000;

// Speed change per button press
const unsigned long SPEED_CHANGE = 200;

// Step timing
unsigned long lastStepTime = 0;

//loght


// -----------------------------
// Previous button states
// -----------------------------
int lastGoState = HIGH;
int lastStopState = HIGH;
int lastSlowerState = HIGH;
int lastFasterState = HIGH;
int lastReverseState = HIGH;


void setup() {

  Serial.begin(9600);

  // Motor pins
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);

  // Button pins
  pinMode(GO_BUTTON, INPUT_PULLUP);
  pinMode(STOP_BUTTON, INPUT_PULLUP);
  pinMode(SLOWER_BUTTON, INPUT_PULLUP);
  pinMode(FASTER_BUTTON, INPUT_PULLUP);
  pinMode(REVERSE_BUTTON, INPUT_PULLUP);

  // Start in forward direction
  digitalWrite(DIR_PIN, HIGH);

  Serial.println("Track Control Ready");
  Serial.println();
  Serial.println("D8  = GO / FORWARD");
  Serial.println("D9  = STOP");
  Serial.println("D10 = SLOWER");
  Serial.println("D11 = FASTER");
  Serial.println("D12 = REVERSE");
}


void loop() {

  // Read buttons
  int goState = digitalRead(GO_BUTTON);
  int stopState = digitalRead(STOP_BUTTON);
  int slowerState = digitalRead(SLOWER_BUTTON);
  int fasterState = digitalRead(FASTER_BUTTON);
  int reverseState = digitalRead(REVERSE_BUTTON);


  // -----------------------------
  // GO / FORWARD
  // -----------------------------
  if (lastGoState == HIGH && goState == LOW) {

    digitalWrite(DIR_PIN, HIGH);

    motorRunning = true;

    Serial.println("TRACK: FORWARD");

    delay(30);
  }


  // -----------------------------
  // STOP
  // -----------------------------
  if (lastStopState == HIGH && stopState == LOW) {

    motorRunning = false;

    Serial.println("TRACK: STOPPED");

    delay(30);
  }


  // -----------------------------
  // SLOWER
  // -----------------------------
  if (lastSlowerState == HIGH && slowerState == LOW) {

    if (stepDelay < SLOWEST_SPEED - SPEED_CHANGE) {
      stepDelay += SPEED_CHANGE;
    }
    else {
      stepDelay = SLOWEST_SPEED;
    }

    Serial.print("TRACK: SLOWER | Step Delay = ");
    Serial.println(stepDelay);

    delay(30);
  }


  // -----------------------------
  // FASTER
  // -----------------------------
  if (lastFasterState == HIGH && fasterState == LOW) {

    if (stepDelay > FASTEST_SPEED + SPEED_CHANGE) {
      stepDelay -= SPEED_CHANGE;
    }
    else {
      stepDelay = FASTEST_SPEED;
    }

    Serial.print("TRACK: FASTER | Step Delay = ");
    Serial.println(stepDelay);

    delay(30);
  }


  // -----------------------------
  // REVERSE / BACKWARD
  // -----------------------------
  if (lastReverseState == HIGH && reverseState == LOW) {

    digitalWrite(DIR_PIN, LOW);

    motorRunning = true;

    Serial.println("TRACK: REVERSE");

    delay(30);
  }


  // -----------------------------
  // Save button states
  // -----------------------------
  lastGoState = goState;
  lastStopState = stopState;
  lastSlowerState = slowerState;
  lastFasterState = fasterState;
  lastReverseState = reverseState;


  // -----------------------------
  // MOVE STEPPER
  // -----------------------------
  if (motorRunning) {

    unsigned long currentTime = micros();

    if (currentTime - lastStepTime >= stepDelay) {

      lastStepTime = currentTime;

      digitalWrite(STEP_PIN, HIGH);
      delayMicroseconds(5);
      digitalWrite(STEP_PIN, LOW);
    }
  }
}