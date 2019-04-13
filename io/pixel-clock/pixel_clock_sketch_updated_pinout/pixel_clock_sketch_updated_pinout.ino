byte serialByte;
byte pixel_state[1];
byte acq_trigger_state[1]; 
byte frame_trigger_state[1];
byte registerD_state[1];
byte timer_bytes[4];

unsigned long start_time;
unsigned long last_refresh = 0;
unsigned long time_stamp = 0;
unsigned long time_stamp_internal = 0;

unsigned long target_interval = 1000;// 1 ms interval between writes
unsigned long this_interval;
unsigned long write_count = 0;


int write_flag = 0;

// the setup routine runs once when you press reset:
void setup() { 
  //*UPDATED PINOUT*
  //PIN 2 - LEAVING OPEN FOR INTERRUPT
  //PIN 3-6 PIXEL CLOCK
  //PIN 7 FRAME TRIGGER
  //PIN 8 CAMERA OUTPUT
  
  //I ALSO REMOVED PARTS OF CODE THAT WERE MEANT TO SEND OUTPUT TO PHIDGET IN PORT 4
  //. THIS WAS ACTUALLY NOT BEING USED
  
  // port D maps to Arduino pins 0-7
  DDRD = DDRD | B00000000; //setting pins 0-7 as inputs
                      // NOTE: make sure to leave last 2 bits to 0
                          // these are piins 0 & 1, which are RX & TX. 
                          //changing will lead to problems with serial communication  
  // port B maps to Arduino pins 8-13
  DDRB = DDRB | B00000001;// setting pin 8 as output, 9 to 13 as inputs
  PORTB = B00000000;//set pin 8 to low//UPDATED
  Serial.begin (115200);  //start serial connection
}

// the loop routine runs over and over again forever:
void loop() {
  
   
    while (Serial.available()>0){  
    serialByte=Serial.read();
    if (serialByte=='S'){
      //start recording pixel clock status
      while(1){
        if (write_flag == 0){
          frame_trigger_state[0]=(PIND>>7) &0x1;//bit-shift to the right and mask
          if (frame_trigger_state[0]>0){
            start_time = micros();
            PORTB = B00000001;//set pin 8 to high \\updated
            write_flag = 1; //start streaming data from first time you get acquisition trigger
          }
        }
        else
        {
          frame_trigger_state[0]=(PIND>>7) &0x1;//bit-shift to the right and mask
          
          if (write_count>1){
            this_interval = target_interval-(time_stamp_internal-(target_interval*(write_count-1)));
          }
          else{
            this_interval=target_interval;
          }
          registerD_state[0] = PIND & 0x80;//mask to get only pin 7 \\updated
          pixel_state[0] = PIND & 0x78;//read off D register and mask \\updated
          time_stamp = micros();
          time_stamp_internal = time_stamp -start_time;
          
          while (micros()-last_refresh<this_interval){
          registerD_state[0] = PIND & 0x80;//mask to get only pin 7 \\updated
          pixel_state[0] = PIND & 0x78;//read off D register and mask \\updated
            time_stamp = micros();
            time_stamp_internal = time_stamp-start_time;
          }
          last_refresh = micros();
            //breaking up 32-bit number into 4 bytes
          //**shift bits to right and mask last bit**
          timer_bytes[0] = (time_stamp >> 24) & 0xFF;//4th byte 
          timer_bytes[1] = (time_stamp >> 16) & 0xFF;//3rd byte
          timer_bytes[2] = (time_stamp >> 8) & 0xFF;//2nd byte
          timer_bytes[3] = time_stamp & 0xFF;//1st byte
          //write everything to serial
          Serial.write(registerD_state,1);
          Serial.write(pixel_state,1); 
          Serial.write(timer_bytes,4);
          write_count++;
          
        }
        
        // check for finish trigger
        if (Serial.available()>0){ //Experiment finished - stop recording pixel clock
        serialByte=Serial.read();
        if (serialByte=='F'){
          PORTB = B00000000;//set pin 8 to low \\updated
          write_flag = 0;
          break;
        }
        }
      }
    }
  }
}

