/*
  DATE: 23.09.2018

  MAINTAINER: andre@blobb.me

  USED BOARD: Arduino Nano

  USED MULTIPLEXER: CD74HC4067 CMOS 16 Channel Analog
		    Digital Multiplexer Breakout Module

  read ./README.md and/or help function below for further information.
*/

const char version[ ] = "BusVoodoo testboard v0.3";

// multiplexer (MP) pins (directly connected)
int MP_VCC = 2;// D2
int MP_EN = 3; // D3
int MP_S0 = 4; // D4
int MP_S1 = 5; // D5
int MP_S2 = 6; // D6
int MP_S3 = 7; // D7

// BusVoodoo (BV) pins are not directly
// connected. Pin A0 and A1 are connected
// to the gate of a P-MOSFET.
int BV_DFU_MODE = 14;     // A0
int RESET_BUSVOODOO = 15; // A1
// A0 MOSFET connects BV DFU Pin to 5V
// A1 MOSFET connects BV RST Pin to GND

// buffer for incoming requests
char b[16];

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

  digitalWrite(MP_S0, LOW);
  digitalWrite(MP_S1, LOW);
  digitalWrite(MP_S2, LOW);
  digitalWrite(MP_S3, LOW);
  // multiplexer is disabled when MP_EN is HIGH
  digitalWrite(MP_EN, HIGH);
  digitalWrite(MP_VCC, HIGH);
  digitalWrite(BV_DFU_MODE, LOW);
  digitalWrite(RESET_BUSVOODOO, LOW);

  Serial.begin(9600);
  Serial.println("BusVoodoo testboard initialised...");
}

void loop() {

  // check for pending request
  if (Serial.available() > 0) {

    fill_buffer();
    char request = b[0];

    switch (request) {
      case 'b': {
          boot_bv_into_dfu_mode();
        } break;
      case 'g': {
          get_multiplexer();
        } break;
      case 'r': {
          reset_busvoodoo();
        } break;
      case 's': {
          set_multiplexer(b[1], b[2], b[3], b[4]);
        } break;
      case 'd': {
          disable_multiplexer();
        } break;
      case 'v': {
          send_version();
        } break;
      case 'h': {
          help();
        } break;
      default:
        error("command not found");
    }
  }

}

// FUNCTIONS
void help() {
  Serial.println("");
  Serial.println(version);
  Serial.println("maintainer: andre@blobb.me");
  Serial.println("date: 22.09.2018");
  Serial.println("");
  Serial.println("This testboard provides following functionalities:");
  Serial.println("   - [r] reset the BusVoodoo");
  Serial.println("   - [b] boot BusVoodoo into DFU BOOT mode");
  Serial.println("   - [g] get current multiplexer settings:");
  Serial.println("         'ACK: 0-1010' first bool represents !state of multiplexer,");
  Serial.println("                       second bool[] represents states of s0,s1,s2,s3");
  Serial.println("");
  Serial.println("   - [s1010] enable multiplexer and set channel, e.g. 1010 = 5 (LSB first)");
  Serial.println("             Note: simply go from 0-8 for the pinstest");
  Serial.println("");
  Serial.println("   - [d] disable multiplexer");
  Serial.println("   - [h] show this help");
  Serial.println("   - [v] get version of firmware");
  Serial.println("");
  Serial.println("More information about:");
  Serial.println("BusVoodo: https://busvoodoo.cuvoodoo.info/");
  Serial.println("BusVoodo-CI: https://git.boddenberg.it/busvoodoo-ci/");
  Serial.println("");
}

// HELPERS
void error(String e) {
  Serial.println("ERROR: " + e);
}

void ack(String a) {
  Serial.println("ACK: " + a);
}

void fill_buffer() {
  for (int i = 0; i < 16; i++) {
    b[i] = Serial.read();
    delay(5); // necessary otherwise only first char is read
  }
}

char getState(int pin) {
  if (digitalRead(pin)) {
    return '1';
  }
  return '0';
}

// EXPOSED FUNCTIONS
// help is first occurring functions though
void send_version() {
  ack(version);
}

void reset_busvoodoo() {
  digitalWrite(RESET_BUSVOODOO, HIGH);
  delay(50);
  digitalWrite(RESET_BUSVOODOO, LOW);
  ack("reset_busvoodoo()");
}

void boot_bv_into_dfu_mode() {
  digitalWrite(BV_DFU_MODE, HIGH);
  reset_busvoodoo();
  delay(5000); // give BusVoodoo
  // some time to boot into DFU
  digitalWrite(BV_DFU_MODE, LOW);
  ack("boot_bv_into_dfu_mode()");
}

void disable_multiplexer() {
  digitalWrite(MP_EN, HIGH);
  ack("disable_multiplexer()");
}

void get_multiplexer() {
  String result = "";
  result = result + getState(MP_EN);
  result = result + "-";
  result = result + getState(MP_S0);
  result = result + getState(MP_S1);
  result = result + getState(MP_S2);
  result = result + getState(MP_S3);
  ack(result);
}

void set_multiplexer(char c0, char c1, char c2, char c3) {
  // disable multiplexer
  digitalWrite(MP_EN, HIGH);
  delay(50);

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

  // enabler multiplexer
  digitalWrite(MP_EN, LOW);
  ack("set_multiplexer()");
}
