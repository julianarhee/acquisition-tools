/*********************************************************
 * Demonstration using bank D pins 0 - 7 and preserving the 
 * values of pins 0 and 1 in the DDRD and PORTD registers.
 *
 * The anode of an LED is connected to pin 7 with 
 * a resistor in series connected to ground. 
 *
 * A pushbutton switch is connected to pin 2 and ground
 * and uses the internal pull-up resistor.
 *
 * The LED lights when the button is pressed.
 *
 *********************************************************/

/**********************************************
 * setup() function
 **********************************************/
void setup()
{

  DDRB = DDRB | B00100000; // set pin13 to output

  // The "|" means a logical OR.
  // We now know that bit 5 is high.
  // And we know bits 0 and 1 are preserved.
  // But we still are not sure of bit 1. 

  DDRB = DDRB & B00100000;

  // We do a logical AND, now we know the status of all the bits.

  // A logical OR against zero or a logical AND against one
  // will not change the status of a bit.

  // This preserved the status of bits 7, 1, and 0.
  // Since bit 1 was ANDed against 0 we know that it is now clear.
  // The DDRD register is now where we want it.
 
  // Now we need to get the PORTD register set the way we want it.

  PORTB = PORTB & B00000000;

  // Bits 0 and 1 are preserved, all others are off.

  PORTB = PORTB | B00001111; // port1 is input

  // Bits 5 is off, the initial state of the LED.
  // Bit 1 is on, because pin 1 is an input turning it's bit
  // on in PORTD turns on the internal pull-up resistor.
}

/**********************************************
 * loop() function
 **********************************************/
 int button = PINB;
 int prev_button = PINB;
  
void loop()
{
  // Read the PIND register.

  int button = PINB;
  // you now have the values of all eight pins in the PIND register
  // contained in a variable. The only pin we care about is pin 2.
  // So we do a logical AND on the button variable to isolate the
  // bit we want.
       
  button = button & B00001111; // isolate port 8,9,100,11

  // Because of the internal pull-up resistor the pin will be high
  // if the button is not pressed, and low if it is.
  // So button will return either 2^2 (4) or zero if it is pressed.

  PORTB = PORTB & B00100000; // turn off?

  // Turn LED off, and preserve bits 0 - 2.
 
  if (button == prev_button) 
  {
    PORTB = B00000000;

    // turn LED on, and preserve bits 0 - 2.
  }
  else{
    PORTB = PORTB | B00100000;
  }
  prev_button = button;
  delay(50);
 
}
