/*
  USED BOARD: Arduino Nano
  MAINTAINER: andre@boddenberg.it

*/// PINS

// multiplexer (MP)
int MP_VCC = 5;
int MP_EN = 6;
int MP_S0 = 7;
int MP_S1 = 8;
int MP_S2 = 9;
int MP_S3 = 10;
// BusVoodoo (BV)
int BV_DFU_MODE = 19;
// USB hub resets
int RESET_BUSVOODOO = 20;
int RESET_FLASHBOARD = 21;
int RESET_YOURSELF = 22;

// buffer for incoming requests
char b [16];

void setup() {
  // settings I/O modes
  pinMode(MP_S0, OUTPUT);
  pinMode(MP_S1, OUTPUT);
  pinMode(MP_S2, OUTPUT);
  pinMode(MP_S3, OUTPUT);
  pinMode(MP_EN, OUTPUT);
  pinMode(MP_VCC, OUTPUT);
  pinMode(BV_DFU_MODE, OUTPUT);
  pinMode(RESET_BUSVOODOO, OUTPUT);
  pinMode(RESET_FLASHBOARD, OUTPUT);
  pinMode(RESET_YOURSELF, OUTPUT);

  // pulling every output low
  digitalWrite(MP_S0, LOW);
  digitalWrite(MP_S1, LOW);
  digitalWrite(MP_S2, LOW);
  digitalWrite(MP_S3, LOW);
  digitalWrite(MP_EN, LOW);
  digitalWrite(MP_VCC, LOW);
  digitalWrite(BV_DFU_MODE, LOW);
  digitalWrite(RESET_BUSVOODOO, LOW);
  digitalWrite(RESET_FLASHBOARD, LOW);
  digitalWrite(RESET_YOURSELF, LOW);

  Serial.begin(9600);
  Serial.println("BusVoodoo testboard initialised...");
}

void loop() {

  if (Serial.available() > 0) {

    fill_buffer();

    char request = b[0];

    switch (request) {
      case 'a': {
          reset_all();
        } break;
      case 'b': {
          boot_bv_into_dfu_mode();
        } break;
      case 'p': {
          ping();
        } break;
      case 'g': {
          get_multiplexer();
        } break;
      case 'r': {
          reset(b[1]);
        } break;
      case 's': {
          set_multiplexer(b[1], b[2], b[3], b[4]);
        } break;
      case 'd': {
          disable_multiplexer();
        } break;
      default:
        error("command not found");
    }
    // flush buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}

// functions
void fill_buffer() {
  for (int i = 0; i < 16; i++) {
    b[i] = Serial.read();
    delay(5); // necessary otherwise
    // only first char is read
  }
}

void reset_all() {
  digitalWrite(RESET_BUSVOODOO, HIGH);
  digitalWrite(RESET_FLASHBOARD, HIGH);
  digitalWrite(RESET_YOURSELF, HIGH);
  // no ack can be send
}

// helper for get_multiplexer()
char getState(int pin) {
  if (digitalRead(pin)) {
    return '1';
  }
  return '0';
}

void get_multiplexer() {
  String result = "";
  result = result + getState(MP_S0);
  result = result + getState(MP_S1);
  result = result + getState(MP_S2);
  result = result + getState(MP_S3);
  ack("get_multiplexer() -> " + result);
}

void ping() {
  ack("pong");
}

void reset(char device) {
  switch (device) {
    case 'b': {
        digitalWrite(RESET_BUSVOODOO, HIGH);
        delay(500);
        digitalWrite(RESET_BUSVOODOO, LOW);
        ack("reset BusVoodoo");
      } break;
    case 'f': {
        digitalWrite(RESET_FLASHBOARD, HIGH);
        delay(500);
        digitalWrite(RESET_FLASHBOARD, LOW);
        ack("reset flashboard");
      } break;
    case 't': {
        digitalWrite(RESET_YOURSELF, HIGH);
      } break;
    default:
      error("reset device not known (b|f|t)");
  }
}

void disable_multiplexer() {
  digitalWrite(MP_VCC, LOW);
  digitalWrite(MP_EN, LOW);
  digitalWrite(MP_S0, LOW);
  digitalWrite(MP_S1, LOW);
  digitalWrite(MP_S2, LOW);
  digitalWrite(MP_S3, LOW);
  ack("disable_multiplexer()");
}

/* takes number [0,15] and uses
   the first 4 bits to set
   the multiplexer.
*/
void set_multiplexer(char c0, char c1, char c2, char c3) {

  // disable multiplexer
  digitalWrite(MP_EN, LOW);
  delay(500);

  // set multiplexer
  if (c0 == '1') {
    digitalWrite(MP_S0, HIGH);
  } else {
    digitalWrite(MP_S0, LOW);
  }
  if (c1 == '1') {
    digitalWrite(MP_S1, HIGH);
  } else {
    digitalWrite(MP_S1, LOW);
  }
  if (c2 == '1') {
    digitalWrite(MP_S2, HIGH);
  } else {
    digitalWrite(MP_S2, LOW);
  }
  if (c3 == '1') {
    digitalWrite(MP_S3, HIGH);
  } else {
    digitalWrite(MP_S3, LOW);
  }

  // enable and power cycle multplexer
  // (in case it has been disabled prevously)
  digitalWrite(MP_EN, HIGH);
  digitalWrite(MP_VCC, HIGH);

  ack("set_multiplexer()");
}

void error(String e) {
  Serial.println("ERROR: " + e);
}

void ack(String a) {
  Serial.println("ACK: " + a);
}

void boot_bv_into_dfu_mode() {
  digitalWrite(BV_DFU_MODE, HIGH);
  digitalWrite(RESET_BUSVOODOO, HIGH);
  delay(500);
  digitalWrite(RESET_BUSVOODOO, LOW);
  delay(1000);
  digitalWrite(BV_DFU_MODE, LOW);
  ack("boot_bv_into_dfu_mode()");
}
