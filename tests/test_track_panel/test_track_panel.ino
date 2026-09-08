#include <LiquidCrystal.h>
#include <Adafruit_NeoPixel.h>

#define LED_PIN    13
#define LED_COUNT  74

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// ------------------------------------------------
// LCD
// RS, E, D4, D5, D6, D7
// ------------------------------------------------
LiquidCrystal lcd(2, 5, 6, 7, A1, A2);

// ------------------------------------------------
// TMC2209
// ------------------------------------------------
const int STEP_PIN = 3;
const int DIR_PIN  = 4;

// ------------------------------------------------
// Buttons
// ------------------------------------------------
const int FORWARD_BUTTON = 8;
const int STOP_BUTTON    = 9;
const int SLOWER_BUTTON  = 10;
const int FASTER_BUTTON  = 11;
const int REVERSE_BUTTON = 12;

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


// Custom filled box for speed bar
byte fullBox[8] = {
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111
};


void setup() {

  Serial.begin(9600);

  // Motor
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);

  // Buttons
  pinMode(FORWARD_BUTTON, INPUT_PULLUP);
  pinMode(STOP_BUTTON, INPUT_PULLUP);
  pinMode(SLOWER_BUTTON, INPUT_PULLUP);
  pinMode(FASTER_BUTTON, INPUT_PULLUP);
  pinMode(REVERSE_BUTTON, INPUT_PULLUP);

  // Start forward
  digitalWrite(DIR_PIN, HIGH);

  // LCD
  lcd.begin(16, 2);

  // Create filled box character
  lcd.createChar(0, fullBox);

  updateSpeed();
  updateLCD();

  Serial.println("Track Ready");

  strip.begin();
  strip.setBrightness(80);
  strip.show();
}


void loop() {

  rainbowCycle(10);

  // Read buttons
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

    Serial.println("FORWARD");

    updateLCD();
  }


  // ------------------------------------------------
  // STOP
  // ------------------------------------------------
  if (lastStopState == HIGH && stopState == LOW) {

    motorRunning = false;

    Serial.println("STOP");

    updateLCD();
  }


  // ------------------------------------------------
  // SLOWER
  // ------------------------------------------------
  if (lastSlowerState == HIGH && slowerState == LOW) {

    if (speedLevel > 1) {
      speedLevel--;
    }

    updateSpeed();

    Serial.print("Speed Level: ");
    Serial.println(speedLevel);

    updateLCD();
  }


  // ------------------------------------------------
  // FASTER
  // ------------------------------------------------
  if (lastFasterState == HIGH && fasterState == LOW) {

    if (speedLevel < 10) {
      speedLevel++;
    }

    updateSpeed();

    Serial.print("Speed Level: ");
    Serial.println(speedLevel);

    updateLCD();
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

    Serial.println("REVERSE");

    updateLCD();
  }


  // Save button states
  lastForwardState = forwardState;
  lastStopState = stopState;
  lastSlowerState = slowerState;
  lastFasterState = fasterState;
  lastReverseState = reverseState;


  // ------------------------------------------------
  // STEPPER MOTOR
  // ------------------------------------------------
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


// ------------------------------------------------
// Convert speed level into motor step delay
// ------------------------------------------------
void updateSpeed() {

  // Level 1 = slow
  // Level 10 = fast

  stepDelay = map(speedLevel, 1, 10, 5000, 500);
}


// ------------------------------------------------
// Update LCD
// ------------------------------------------------
void updateLCD() {

  lcd.clear();

  // FIRST ROW
  lcd.setCursor(0, 0);

  if (!motorRunning) {
    lcd.print("Mode: STOP");
  }
  else if (motorDirection == FORWARD) {
    lcd.print("Mode: FORWARD");
  }
  else {
    lcd.print("Mode: REVERSE");
  }


  // SECOND ROW
  lcd.setCursor(0, 1);

  lcd.print("Spd:");

  // 10-box speed bar
  for (int i = 1; i <= 10; i++) {

    if (i <= speedLevel) {
      lcd.write(byte(0));
    }
    else {
      lcd.print("-");
    }
  }
}

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