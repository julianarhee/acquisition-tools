int frame = 7; // LED connected to digital pin 13
int bit1 = 8;   // pushbutton connected to digital pin 7
int bit2 = 9;   // pushbutton connected to digital pin 7
int bit3 = 10;   // pushbutton connected to digital pin 7
int bit4 = 11;   // pushbutton connected to digital pin 7

int val1 = 0;     // variable to store the read value
int val2 = 0;     // variable to store the read value
int val3 = 0;     // variable to store the read value
int val4 = 0;     // variable to store the read value

byte port;
byte prev_state;
byte buf[4];

byte serialByte;

int counts = 0;
//int req = 1000; // 8000, this works to get rid of all tiny events
int wait = 4000; // starting at 6ms, rid of shorties; 8ms better (10ms too much)

const unsigned long interval = 200; //1000; // sample every 1ms
unsigned long current_ts;

int counter = 0;       // how many times we have seen new value
byte reading;           // the current value read from the input pin
byte current_state = LOW;    // the debounced input value
int current_frame = 0;
unsigned long current_time;

int debounce_count = 5;

void setup()
{
  pinMode(frame, INPUT);      // sets the digital pin 13 as output
  //pinMode(bit1, INPUT);      // sets the digital pin 7 as input
  //pinMode(bit2, INPUT);      // sets the digital pin 7 as input
  //pinMode(bit3, INPUT);      // sets the digital pin 7 as input
  //pinMode(bit4, INPUT);      // sets the digital pin 7 as input
  DDRB = DDRB | B00000000; // set all pins to INPUT.
  Serial.begin (115200);

}


void loop()
{
    while (Serial.available()>0){  
    serialByte=Serial.read();

    if (serialByte=='S'){      
        while(1){
          current_ts = micros();
          while ((micros() - current_ts) <= interval){
              //port = PINB;
              //port = port & B00001111;
              
              // DEBOUNCE?
<<<<<<< Updated upstream
              current_state = PINB & 0xF;
              current_frame = digitalRead(frame);
=======
//              current_state = PINB;
//              current_frame = digitalRead(frame);
>>>>>>> Stashed changes
              //reading &= B00001111;

              /*
              if(reading == current_state && counter > 0)
              {
                counter--;
              }
              if(reading != current_state)
              {
                 counter++; 
              }
              // If the Input has shown the same value for long enough let's switch it
              if(counter >= debounce_count)
              {
                counter = 0;
                current_state = reading;
              }
              */
                           
          

          /*
          if (current_state != prev_state){
            
            unsigned long strt = micros();
            int counts = 0;
            tmp_state = current_state;
            while (counts <= req) {
              current_state = PINB;

              if (tmp_port == port){
                counts += 1;
              }
              else{
                tmp_state = current_state;
              }
            }

            */
            
            /*
            unsigned long strt = micros();
            while ((micros()-strt) <= wait){
              current_state = PINB;
              //port = port & B00001111;
            }
            */
          }
            current_time = micros();            
            current_state = PINB;
            current_frame = digitalRead(frame);
            /*
            val1 = digitalRead(bit1);
            val2 = digitalRead(bit2);
            val3 = digitalRead(bit3);
            val4 = digitalRead(bit4);
            */
            
            /*
            buf[3] = (byte) (current_state & 0xFF);
            buf[2] = (byte) ((current_state >> 8) & 0xFF);
            buf[1] = (byte) ((current_state >> 16) & 0xFF);
            buf[0] = (byte) ((current_state >> 24) & 0xFF);
            */
    
            Serial.print("_");
            Serial.print(current_frame, DEC);
            //Serial.write(buf, 4);
            Serial.print("*");
            //Serial.print(code, DEC);
            //Serial.print(val1, BIN);
            //Serial.print(val2, BIN);
            //Serial.print(val3, BIN);
            //Serial.print(val4, BIN);
            //Serial.print(current_state, DEC);
            Serial.println(current_state); //, DEC);
            //Serial.write(buf, 4);
            Serial.print("*");
            Serial.print(current_time, DEC);
            Serial.print("_");

            //prev_ts = curr_ts;
            
            //prev_state = current_state;
            //Serial.print(prev_state, DEC);
          //}
      
          
          if (Serial.available()>0){
            serialByte=Serial.read();
            if (serialByte=='F')  break;
          }
          
      }
    }
}
}
