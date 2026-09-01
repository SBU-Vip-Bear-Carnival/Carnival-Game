#pragma once
//
// audio.h — DFPlayer Mini wrapper.
//
// Ported from the V1 repo's main.ino (Blaze91827's MyAudioSystem), with one
// fix: the AudioTrack enum was missing a comma after AUDIO_BRIGHTNESS, so it
// never compiled. That is why V1's main branch was broken from 2026-05-07
// onward and nobody noticed -- there was no CI. There is now.
//
// Track numbers are the file numbers on the SD card (0001.mp3 = 1).
//

#include <Arduino.h>
#include <DFRobotDFPlayerMini.h>

enum AudioTrack {
  AUDIO_NONE           = 0,
  AUDIO_MENU_OPTIONS   = 1,
  AUDIO_GAME_MODE      = 2,
  AUDIO_SINGLEPLAYER   = 3,
  AUDIO_MULTIPLAYER    = 4,
  AUDIO_EASY           = 5,
  AUDIO_MEDIUM         = 6,
  AUDIO_HARD           = 7,
  AUDIO_CALIBRATION    = 8,
  AUDIO_PRESSURE_PLATE = 9,
  AUDIO_FLEX_SENSOR    = 10,
  AUDIO_VOLUME         = 11,
  AUDIO_BRIGHTNESS     = 12,   // <-- the missing comma lived here
  AUDIO_MUSIC_SLOW     = 13,
  AUDIO_MUSIC_MEDIUM   = 14,
  AUDIO_MUSIC_FAST     = 15
};

class AudioSystem {
  public:
    AudioSystem() : currentTrack(AUDIO_NONE), volume(20), ready(false) {}

    // Call from setup(), after the serial port for the DFPlayer is open.
    bool begin(Stream &port) {
      ready = player.begin(port);
      if (ready) player.volume(volume);
      return ready;
    }

    void play(AudioTrack track) {
      if (!ready || track == AUDIO_NONE) return;
      currentTrack = track;
      player.play(track);
    }

    void loopTrack(AudioTrack track) {
      if (!ready || track == AUDIO_NONE) return;
      currentTrack = track;
      player.loop(track);
    }

    void stop() {
      if (!ready) return;
      currentTrack = AUDIO_NONE;
      player.stop();
    }

    void setVolume(uint8_t v) {
      volume = constrain(v, 0, 30);
      if (ready) player.volume(volume);
    }

    uint8_t     getVolume()  const { return volume; }
    AudioTrack  getTrack()   const { return currentTrack; }
    bool        isReady()    const { return ready; }

  private:
    DFRobotDFPlayerMini player;
    AudioTrack          currentTrack;
    uint8_t             volume;
    bool                ready;
};
