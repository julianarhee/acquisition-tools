//int ledPin = 13; // LED connected to digital pin 13
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
byte tmp_port;
byte buf[4];

byte tick;
byte tmp_reading;
int reqs = 1;
byte serialByte;

int counts = 0;
int req = 1000; // 8000, this works to get rid of all tiny events
//int wait = 4000; // starting at 6ms, rid of shorties; 8ms better (10ms too much)
int wait = 6000; // starting at 6ms, rid of shorties; 8ms better (10ms too much)



int counter = 0;       // how many times we have seen new value
byte reading;           // the current value read from the input pin
byte current_state = LOW;    // the debounced input value

int debounce_count = 10;

void setup()
{
  //pinMode(ledPin, OUTPUT);      // sets the digital pin 13 as output
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
          //port = PINB;
          //port = port & B00001111;
          
          // DEBOUNCE?
          reading = PINB;
          //reading &= B00001111;
          
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
      

          
          if (current_state != prev_state){
            
            unsigned long strt = micros();
            int counts = 0;
            tmp_reading = current_state;
            //while (counts <= req) {
            while ((micros() - strt) < wait) {
              current_state = PINB;
              //port = port & B00001111;
              if (tmp_reading == current_state){
                counts += 1;
              }
              else{
                tmp_reading = current_state;
              }
            }
            
            
            /*
            unsigned long strt = micros();
            
            while ((micros()-strt) <= wait){
              current_state = PINB;
              //port = port & B00001111;
            }
            */
            unsigned long curr_time = micros();

            //unsigned long strt = micros();
            
            /*
            val1 = digitalRead(bit1);
            val2 = digitalRead(bit2);
            val3 = digitalRead(bit3);
            val4 = digitalRead(bit4);
            */

            /*
            unsigned long write_num = 4294967290;
            buf[3] = (byte) (write_num & 0xFF);
            buf[2] = (byte) ((write_num >> 8) & 0xFF);
            buf[1] = (byte) ((write_num >> 16) & 0xFF);
            buf[0] = (byte) ((write_num >> 24) & 0xFF);
            */
            
            Serial.print("_");
            //Serial.print(code, DEC);
            //Serial.print(val1, BIN);
            //Serial.print(val2, BIN);
            //Serial.print(val3, BIN);
            //Serial.print(val4, BIN);
            //Serial.print(current_state);
            Serial.print(current_state);
            //Serial.write(buf, 4);
            Serial.print("*");
            Serial.print(curr_time, DEC);
            Serial.print("_");
            
            prev_state = current_state;
            //Serial.print(prev_state, DEC);
          }
      
          
          if (Serial.available()>0){
            serialByte=Serial.read();
            if (serialByte=='F')  break;
          }
          
      }
    }
}
}
