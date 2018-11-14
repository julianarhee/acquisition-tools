#include "Timer.h"

Timer t;

int frame = 7; // LED connected to digital pin 13

int val1 = 0;     // variable to store the read value
int val2 = 0;     // variable to store the read value
int val3 = 0;     // variable to store the read value
int val4 = 0;     // variable to store the read value

byte port;
byte prev_state;
byte buf[4];

byte serialByte;

const unsigned long interval = 1; //200; //1000; // sample every 1ms
unsigned long prev_ts;

int counter = 0;       // how many times we have seen new value
byte reading;           // the current value read from the input pin
byte current_state = LOW;    // the debounced input value
int current_frame = 0;
unsigned long current_time; 

void setup()
{
  pinMode(frame, INPUT);      // sets the digital pin 13 as output
  //pinMode(bit1, INPUT);      // sets the digital pin 7 as input
  //pinMode(bit2, INPUT);      // sets the digital pin 7 as input
  //pinMode(bit3, INPUT);      // sets the digital pin 7 as input
  //pinMode(bit4, INPUT);      // sets the digital pin 7 as input
  DDRB = DDRB | B00000000; // set all pins to INPUT.
  Serial.begin (115200);

  t.every(interval, printdata);

}

void loop()
{
    while (Serial.available()>0){  
    serialByte=Serial.read();

    if (serialByte=='S'){      
        while(1){
          current_time = micros();    
          current_state = PINB;
          current_frame = digitalRead(frame);
              //reading &= B00001111;
          t.update();
          
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

          if (Serial.available()>0){
            serialByte=Serial.read();
            if (serialByte=='F')  break;
          }
        } 
      }
    }
}


void printdata(){
    Serial.print("_");
    Serial.print(current_frame, DEC);
    //Serial.write(buf, 4);
    Serial.print("*");
    //Serial.print(code, DEC);
    //Serial.print(val1, BIN);
    //Serial.print(val2, BIN);
    //Serial.print(val3, BIN);
    //Serial.print(val4, BIN);
    Serial.print(current_state, DEC);
    //Serial.write(buf, 4);
    Serial.print("*");
    Serial.print(current_time, DEC);
    Serial.print("_");
      
}

