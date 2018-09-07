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
}

void loop() {

        // 
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

void set_multiplexer(String result) {

        digitalWrite(EN, LOW);

        if(result[0] = 1) {
          digitalWrite(S0, HIGH);
        } else {
          digitalWrite(S0, LOW);
        }
        if(result[1] = 1) {
          digitalWrite(S1, HIGH);
        } else {
          digitalWrite(S1, LOW);
        }
        if(result[2] = 1) {
          digitalWrite(S2, HIGH);
        } else {
          digitalWrite(S2, LOW);
        }
        if(result[3] = 1) {
          digitalWrite(S3, HIGH);
        } else {
          digitalWrite(S3, LOW);
        }

        digitalWrite(EN, HIGH);
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
