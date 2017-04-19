
byte serialByte;


// the setup routine runs once when you press reset:
void setup() { 
  // port D maps to Arduino pins 0-7
  DDRD = DDRD | B00000000;  // setting pins 0 to 7 as inputs
	                  // NOTE: make sure to leave last 2 bits to 0
                          // these are piins 0 & 1, which are RX & TX. 
                          //changing will lead to problems with serial communication  

  Serial.begin (115200);  //start serial connection
}

// the loop routine runs over and over again forever:
void loop() {
    while (Serial.available()>0){  
    serialByte=Serial.read();
    if (serialByte=='Q'){
      Serial.write(PIND);// send register status through serial port
    }
  }
}
