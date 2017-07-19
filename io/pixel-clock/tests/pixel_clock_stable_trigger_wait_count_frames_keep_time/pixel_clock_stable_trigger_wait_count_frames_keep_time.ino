
byte serialByte;
byte current_pixel_state;
byte prev_pixel_state;
int current_frame_state;
int prev_frame_state;
unsigned long stable_time = 5000;//microsecs to get the same read to record pixel clock change
unsigned long change_time;
unsigned long stable_timer;
unsigned long start_time;

int counter_array[2];// counter for data and display frames
int first_change = 0;
int write_flag = 0;
int change_flag = 0;

// the setup routine runs once when you press reset:
void setup() { 
  // port B maps to Arduino pins 8-13
  DDRB = DDRB | B00000000;// setting pins 8 to 13 as inputs
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
    if (serialByte=='S'){
      //start recording pixel clock status
      while(1){
        current_pixel_state = PINB;//read off B register
        current_frame_state = (int) PIND>127;// read off D register
        
        //update frame counter if pin 7 went from LOW to HIGH
        if ((current_frame_state - prev_frame_state) == 1){
          if (first_change == 0){
            start_time = micros();
            first_change ++;
            }
          change_time = micros()-start_time;
          stable_timer = micros();
          change_flag = 1;
        }
        //update screen_counter if pixel clock status changed, only if trigger received
        if (current_pixel_state != prev_pixel_state){
           if (first_change == 0){
            start_time = micros();
            first_change ++;
            }
            change_time = micros()-start_time;
            stable_timer = micros();
            change_flag = 2;
        }
      // make sure detected change is stable before writing to file and increasing counters
        if (((micros()-stable_timer)>stable_time) && change_flag>0){ 
   //     Serial.print('*');
    //    Serial.println(micros()-stable_timer, DEC);
        counter_array[change_flag-1]++;
        change_flag = 0;
        write_flag = 1;
        }
        // output to serial
        if (write_flag==1){
       
          Serial.println(counter_array[0], DEC);
          Serial.println(current_frame_state, DEC);
          Serial.println(counter_array[1], DEC);
          //pad with leading zeros
          if (current_pixel_state < 2) Serial.print(B0);
          if (current_pixel_state < 4) Serial.print(B0);
          if (current_pixel_state < 8) Serial.print(B0);
          Serial.println(current_pixel_state, BIN);
          Serial.println(current_pixel_state, DEC);
          Serial.println(change_time, DEC);
          write_flag = 0;
        }
        //update counters
        prev_pixel_state = current_pixel_state;
        prev_frame_state = current_frame_state;
        
        
        // check for finish trigger
        if (Serial.available()>0){ //Experiment finished - stop recording pixel clock
        serialByte=Serial.read();
        if (serialByte=='F'){
          counter_array[0] = 0;
          counter_array[1] = 0;
          first_change=0;
          break;
        }
        }
      }
    }
  }
}

