byte current_pixel_state;

void setup() {
    // port B maps to Arduino pins 8-13
  DDRB = DDRB | B00000000;// setting pins 8 to 13 as inputs
  Serial.begin (115200);  //start serial connection

}

void loop() {
  // put your main code here, to run repeatedly:
  current_pixel_state = PINB;//read off B register
  Serial.println(current_pixel_state, DEC);
  delay(100);

}
