 // PINS
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

void setup() {
  // I/O modes
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
    char request = Serial.read();
    switch(request) {
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
        Serial.println('w');
        delay(1500);
        char input = Serial.read();
        reset(input);
      } break;
      case 's': {
        Serial.println('w');
        delay(1500);
        int input = Serial.read();
        set_multiplexer(input);
      } break;
      case 'd': {
        disable_multiplexer();
      } break;
      default:
        Serial.println("command not found");
    }
    // empty buffer
    while(Serial.available() > 0) {
      Serial.read();
    }
  }
}

// functions

void reset_all(){
  digitalWrite(RESET_BUSVOODOO, HIGH);
  digitalWrite(RESET_FLASHBOARD, HIGH);
  digitalWrite(RESET_YOURSELF, HIGH);
  // no ack can be send
}

char getState(int pin) {
  if(digitalRead(pin)) {
    return '1';
  }
  return '0';
}

void get_multiplexer() {
  String result ="";
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
  switch(device) {
    case 'b': {
      digitalWrite(RESET_BUSVOODOO, HIGH);
      delay(500);
      digitalWrite(RESET_BUSVOODOO, LOW);
    }break;
    case 'f': {
      digitalWrite(RESET_FLASHBOARD, HIGH);
      delay(500);
      digitalWrite(RESET_FLASHBOARD, LOW);
    }break;
    case 'y': {
      digitalWrite(RESET_YOURSELF, HIGH);
    }break;
    default:
      error("reset device nout known (b|f|y)");
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

void set_multiplexer(int result) {
  // disable multiplexer
  digitalWrite(MP_EN, LOW);
  delay(500);

  // set multiplexer
  if(bitRead(result, 3) == 1) {
    digitalWrite(MP_S0, HIGH);
  } else {
    digitalWrite(MP_S0, LOW);
  }
  if(bitRead(result, 2) == 1) {
    digitalWrite(MP_S1, HIGH);
  } else {
    digitalWrite(MP_S1, LOW);
  }
  if(bitRead(result, 1) == 1) {
    digitalWrite(MP_S2, HIGH);
  } else {
    digitalWrite(MP_S2, LOW);
  }
  if(bitRead(result, 0) == 1) {
    digitalWrite(MP_S3, HIGH);
  } else {
    digitalWrite(MP_S3, LOW);
  }

  // enable and power cycle multplexer
  // (in case it has been disabled prevously)
  digitalWrite(MP_EN, HIGH);
  digitalWrite(MP_VCC, HIGH);

  ack("set_multiplexer() -> " + result);
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
