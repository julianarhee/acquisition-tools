
byte serialByte;
byte pixel_state[1];
byte acq_trigger_state[1];
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
  // port B maps to Arduino pins 8-13
  DDRB = DDRB | B00000000;// setting pins 8 to 13 as inputs
  // port D maps to Arduino pins 0-7
  DDRD = DDRD | B00110000; // setting pins 0 to 4, 6, and 7 as inputs
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
      //start recording pixel clock status
      while(1){
        if (write_flag == 0){
          acq_trigger_state[0]=(PIND>>7) &0x1;//bit-shift to the right and mask
          if (acq_trigger_state[0]>0){
            start_time = micros();
            PORTD |= B00110000;//set pin 5 to high (for camera)
            write_flag = 1; //start streaming data from first time you get acquisition trigger
          }
        }
        else
        {
          if (write_count>1){
            this_interval = target_interval-(time_stamp_internal-(target_interval*(write_count-1)));
          }
          else{
            this_interval=target_interval;
          }
          registerD_state[0] = PIND & 0xC0;//mask to get only pin 6 and 7
          pixel_state[0] = PINB & 0xF;//read off B register
          time_stamp = micros();
          time_stamp_internal = time_stamp -start_time;
          
          while (micros()-last_refresh<this_interval){
            registerD_state[0] = PIND & 0xC0;//mask to get only pin 6 and 7
            pixel_state[0] = PINB &0xF;//read off B registe
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
          PORTD = B00000000;//set pin 5 to low (for camera)
          write_flag = 0;
          break;
        }
        }
      }
    }
  }
}

