int floor1Pin = 0;

int floor2Pin = 1;
int floor3Pin = 7;
int floor4Pin = 4;
int xWall1Pin = 2;
int xWall2Pin = 3;
int yWall1Pin = 5;
int yWall2Pin = 6;

unsigned short floor1Output = 0;
unsigned short floor2Output = 0;
unsigned short floor3Output = 0;
unsigned short floor4Output = 0;
unsigned short xWall1Output = 0;
unsigned short xWall2Output = 0;
unsigned short yWall1Output = 0;
unsigned short yWall2Output = 0;

long timeStart;
long programStart;

void SendAllForceData() {
  floor1Output = (unsigned short)analogRead(floor1Pin);
  floor2Output = (unsigned short)analogRead(floor2Pin);
  floor3Output = (unsigned short)analogRead(floor3Pin);
  floor4Output = (unsigned short)analogRead(floor4Pin);
  xWall1Output = (unsigned short)analogRead(xWall1Pin);
  xWall2Output = (unsigned short)analogRead(xWall2Pin);
  yWall1Output = (unsigned short)analogRead(yWall1Pin);
  yWall2Output = (unsigned short)analogRead(yWall2Pin);

  unsigned long time = micros() - programStart;

  Serial.write(time >> 24);
  Serial.write(time >> 16);
  Serial.write(time >> 8);
  Serial.write(time);

  Serial.write(floor1Output >> 8);
  Serial.write(floor1Output);

  Serial.write(floor2Output >> 8);
  Serial.write(floor2Output);

  Serial.write(floor3Output >> 8);
  Serial.write(floor3Output);

  Serial.write(floor4Output >> 8);
  Serial.write(floor4Output);

  Serial.write(xWall1Output >> 8);
  Serial.write(xWall1Output);

  Serial.write(xWall2Output >> 8);
  Serial.write(xWall2Output);

  Serial.write(yWall1Output >> 8);
  Serial.write(yWall1Output);

  Serial.write(yWall2Output >> 8);
  Serial.write(yWall2Output);
}

void setup() {
  Serial.begin(115200);

  //while(Serial.available()) Serial.read();

  while(!Serial.available()){}
  Serial.read();

  while(analogRead(floor4Pin) == 0) {}
  programStart = micros();

  timeStart = programStart;
}
 
void loop() {
  //if(micros() - timeStart >= 33333) //30 Hz
  if(micros() - timeStart >= 2000) //ends up sending at closer to every 2.2 millis but honestly so does the kinematic stuff so whatever
  {
    timeStart = micros();
    SendAllForceData();
    //Serial.println(timeStart);
  }
}
