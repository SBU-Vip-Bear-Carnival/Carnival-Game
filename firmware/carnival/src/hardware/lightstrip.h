#pragma once
//
// Ported from V1's `cleanup` branch (main/src/lightstrip.h) on 2026-09-02,
// unchanged except for the include lines: V1 had one config.h, V2 splits it
// into config/pins.h, config/tuning.h and config/types.h.
// reads DATA_PIN, NUM_LEDS, LightPattern
//
#include <FastLED.h>
#include <Arduino.h>
#include "../config/pins.h"
#include "../config/tuning.h"
#include "../config/types.h"

extern CRGB leds[];  // defined in carnival.ino

class MyLightstrip {
public:
  MyLightstrip()
    : CurrPattern(STANDBY), lastUpdate(0), patternIndex(0),
      hue(0), movingIndex(0), movingHue(0), blinkState(false), breathAngle(0) {}

  void begin() {
    FastLED.addLeds<WS2812B, DATA_PIN, GRB>(leds, NUM_LEDS);
    FastLED.setBrightness(255);
    FastLED.clear();
    FastLED.show();
  }

  LightPattern getCurrentPattern() { return CurrPattern; }

  void play() {
    unsigned long now = millis();
    switch (CurrPattern) {
      case STANDBY:
        if (now - lastUpdate >= 250) {
          lastUpdate = now;
          if (patternIndex < NUM_LEDS) { leds[patternIndex] = CRGB::Cyan; patternIndex++; }
          else { FastLED.clear(); patternIndex = 0; }
          FastLED.show();
        }
        break;
      case IDLE:
        if (now - lastUpdate >= 20) {
          lastUpdate = now;
          hue++;
          fill_solid(leds, NUM_LEDS, CHSV(hue, 255, 255));
          FastLED.show();
        }
        break;
      case MOVING:
        if (now - lastUpdate >= 100) {
          lastUpdate = now;
          FastLED.clear();
          leds[movingIndex] = CHSV(movingHue, 255, 255);
          movingHue   += 32;
          movingIndex  = (movingIndex + 1) % NUM_LEDS;
          FastLED.show();
        }
        break;
      case PLAYER1_WIN:
        if (now - lastUpdate >= 500) {
          lastUpdate = now;
          blinkState = !blinkState;
          if (blinkState) fill_solid(leds, NUM_LEDS, CRGB::Green);
          else FastLED.clear();
          FastLED.show();
        }
        break;
      case PLAYER2_WIN:
        if (now - lastUpdate >= 500) {
          lastUpdate = now;
          blinkState = !blinkState;
          if (blinkState) fill_solid(leds, NUM_LEDS, CRGB::Blue);
          else FastLED.clear();
          FastLED.show();
        }
        break;
      case RESETTING:
        if (now - lastUpdate >= 30) {
          lastUpdate  = now;
          breathAngle = (breathAngle + 4) % 256;
          uint8_t brightness = sin8(breathAngle);
          for (int i = 0; i < NUM_LEDS; i++) leds[i] = CRGB(brightness, 0, 0);
          FastLED.show();
        }
        break;
    }
  }

  bool changePattern(LightPattern pattern) {
    if (pattern == CurrPattern) return false;
    CurrPattern  = pattern;
    patternIndex = 0; hue = 0; movingIndex = 0;
    movingHue = 0; blinkState = false; breathAngle = 0;
    lastUpdate = millis();
    FastLED.clear();
    FastLED.show();
    return true;
  }

  void turnOff() {
    FastLED.clear();
    FastLED.show();
    CurrPattern = STANDBY;
  }

private:
  LightPattern  CurrPattern;
  unsigned long lastUpdate;
  int           patternIndex, movingIndex;
  uint8_t       hue, movingHue, breathAngle;
  bool          blinkState;
};
