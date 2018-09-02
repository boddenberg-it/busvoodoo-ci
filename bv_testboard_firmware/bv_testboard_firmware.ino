/*
 * 
 */
void setup() {

  // multiplexer (MP)
  int 10 = MP_S0;
  int 11 = MP_S1;
  int 12 = MP_S2;
  int 13 = MP_S3;
  int 14 = MP_S4;
  int 15 = MP_EN;
  int 16 = MP_VCC;

  // BusVoodoo (BV)
  int 17 = BV_DFU_MODE;
  int 18 = BV_RESET;
  // photo resistors to verify LED status
  int 19 = BV_PR_1;
  int 20 = BV_PR_2;
  
  digitalWrite(S2, LOW);
  digitalWrite(S3, LOW);
  digitalWrite(S4, LOW);
  digitalWrite(EN, LOW);
  ...
  
  // power cycle multiplexer (MP)
  digitalWrite(VCC, HIGH);

  Serial.begin(9600);
}

void loop() {
  
        if (Serial.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial.read();

                // say what you got:
                Serial.print("I received: ");
                Serial.println(incomingByte, DEC);
        }


        digitalWrite(EN, LOW);

        // setMultiPlexer
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

}


