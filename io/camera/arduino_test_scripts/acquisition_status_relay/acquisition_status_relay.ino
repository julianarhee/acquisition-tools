
byte serialByte;
byte register_status;
byte pin_status;


// the setup routine runs once when you press reset:
void setup() {
  // port D maps to Arduino pins 0-7
  DDRD = DDRD | B00100000;  // setting pins 0 to 4, 6, and 7 as inputs
                            //setting pin 5 as output to camera
	                  // NOTE: make sure to leave last 2 bits to 0
                          // these are piins 0 & 1, which are RX & TX. 
                          //changing will lead to problems with serial communication  
  
  Serial.begin (115200);  //start serial connection
}

// the loop routine runs over and over again forever:
void loop() {
  
    while (Serial.available()>0){  
    serialByte=Serial.read();
    if (serialByte=='S'){
      while(1){
        //checking status of acquisition trigger
        register_status=PIND;
        pin_status=(register_status>>6) & 0x1;//bit-shift to the right and mask
        if (pin_status>0){
          PORTD = B00100000;//set pin 5 to high
        }
        while (Serial.available()>0){  
          serialByte=Serial.read();
          if (serialByte=='F'){
            PORTD = B00000000;//set pin 0 to low
            break;
          }
        }
      }
    }
    }
}
