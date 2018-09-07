/*
 *
 */ 
void setup() {

  // multiplexer (MP)
  int 10 = MP_S0;
  int 11 = MP_S1;
  int 12 = MP_S2;
  int 13 = MP_S3;
  int 15 = MP_EN;
  int 16 = MP_VCC;

  // BusVoodoo (BV)
  int 17 = BV_DFU_MODE;
  // photo resistors to verify LED status
  int 19 = BV_PR_1;
  int 20 = BV_PR_2;

  // USB hub resets
  int 18 = RESET_BUSVOODOO;
  int 21 = RESET_FLASHBOARD;
  int 22 = RESET_YOURSELF;

  pinMode(MP_S0, OUTPUT); 
  pinMode(MP_S1, OUTPUT); 
  pinMode(MP_S2, OUTPUT); 
  pinMode(MP_S3, OUTPUT); 
  pinMode(MP_EN, OUTPUT); 
  pinMode(MP_VCC, OUTPUT); 
  
  pinMode(BV_DFU_MODE, OUTPUT); 
  pinMode(BV_PR_1, INPUT); 
  pinMode(BV_PR_2, INPUT); 
  
  pinMode(RESET_BUSVOODOO, OUTPUT); 
  pinMode(RESET_FLASHBOARD, OUTPUT); 
  pinMode(RESET_YOURSELF, OUTPUT); 

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
                // read the incoming byte:
                incomingByte = Serial.read();

                // say what you got:
                Serial.print("I received: ");
                Serial.println(incomingByte, DEC);
        }


}

// functions

void reset_all(){
  digitalWrite(RESET_BUSVOODOO, HIGH);
  digitalWrite(RESET_FLASHBOARD, HIGH);
  digitalWrite(RESET_YOURSELF, HIGH);
  // no ack can be send
}

void get_multiplexer() {
  String result ="";
  result = result + getState(MP_S0);
  result = result + getState(MP_S1);
  result = result + getState(MP_S2);
  result = result + getState(MP_S3);
  ack("get_multiplexer() -> " + result);
}

char getState(String pin) {
  if(digitalRead(pin)) {
    return '1';
  }
  return '0';
}

void ping() {
  ack("pong");
}

void reset(char device) {
  switch(device) {
    case 'b':
      digitalWrite(RESET_BUSVOODOO, HIGH);
      delay(500);
      digitalWrite(RESET_BUSVOODOO, LOW);
      break;
    case 'f':
      digitalWrite(RESET_FLASHBOARD, HIGH);
      delay(500);
      digitalWrite(RESET_FLASHBOARD, LOW);
      break;
    case 'y':
      digitalWrite(RESET_YOURSELF, HIGH);
      break;
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

void set_multiplexer(String result) {
  // disable multiplexer
  digitalWrite(MP_EN, LOW);
  delay(500);

  // set multiplexer
  if(result[0] = 1) {
    digitalWrite(MP_S0, HIGH);
  } else {
    digitalWrite(MP_S0, LOW);
  }
  if(result[1] = 1) {
    digitalWrite(MP_S1, HIGH);
  } else {
    digitalWrite(MP_S1, LOW);
  }
  if(result[2] = 1) {
    digitalWrite(MP_S2, HIGH);
  } else {
    digitalWrite(MP_S2, LOW);
  }
  if(result[3] = 1) {
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
