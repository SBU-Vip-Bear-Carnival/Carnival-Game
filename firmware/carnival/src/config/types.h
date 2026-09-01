#pragma once
//
// types.h — enums and state structs. Rarely changes.
//
// Kept apart from pins.h and tuning.h on purpose: those two are edited
// constantly during bring-up, and merging is easier when a wiring change and
// a game-logic change do not land in the same file.
//

enum LightPattern {
  STANDBY = 0,
  IDLE,
  MOVING,
  PLAYER1_WIN,
  PLAYER2_WIN,
  RESETTING
};

enum GameMode {
  MODE_STANDBY = 0,
  MODE_SINGLE_EASY,
  MODE_TWO_PLAYER,
  MODE_SINGLE_HARD
};

enum TrackError {
  NO_ERROR  = 0,
  LIMIT_HIT = 2,
  BUSY      = 3
};

struct Mode1State {
  bool gameStarted, gameWon, waitingForReset, isResetting, isMoving;
  void reset() {
    gameStarted = gameWon = waitingForReset = isResetting = isMoving = false;
  }
};

struct Mode2State {
  bool gameStarted, gameWon, waitingForReset, isResetting, track1Moving, track2Moving;
  int  winner;
  void reset() {
    gameStarted = gameWon = waitingForReset = isResetting = false;
    track1Moving = track2Moving = false;
    winner = 0;
  }
};

struct Mode3State {
  bool          gameStarted, gameWon, waitingForReset, isResetting;
  bool          isMovingForward, isDrifting;
  unsigned long lastDriftTime, lastStepTime;
  void reset() {
    gameStarted = gameWon = waitingForReset = isResetting = false;
    isMovingForward = isDrifting = false;
    lastDriftTime = lastStepTime = 0;
  }
};
