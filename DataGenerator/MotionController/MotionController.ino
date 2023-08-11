//Pins
const byte XStep = 2;
const byte YStep = 3;
const byte ZStep = 4;
const byte XDir = 5;
const byte YDir = 6;
const byte ZDir = 7;
const byte XLimit = 9;
const byte YLimit = 10;
const byte ZLimit = 11;


//Movement variables
short CurrentXPos;
short CurrentYPos;
short CurrentZPos;

short CurrentXDes;
short CurrentYDes;
short CurrentZDes;

byte CurrentXDir;
byte CurrentYDir;
byte CurrentZDir;

byte XPulseDelay;
byte YPulseDelay;
byte ZPulseDelay;

byte XDelayIndex;
byte YDelayIndex;
byte ZDelayIndex;

int8_t CurrentXVel;
int8_t CurrentYVel;
int8_t CurrentZVel;

short SendXPos;
short SendYPos;
short SendZPos;
int8_t SendXVel;
int8_t SendYVel;
int8_t SendZVel;

const byte DataStart = 255;

//Boundaries
const short XMaxStep = 3632;
const short YMaxStep = 1624;
const short ZLowStep = 1000;

short RoutineState = 0;
short RoutineIteration = 0;
const short RoutineCount = 1;

long sendIntervalStart;
const long sendInterval = 1500;

void Pulse(int StepPin, int microDelay = 250)
{
  digitalWrite(StepPin,HIGH);
  delayMicroseconds(microDelay);
  
  digitalWrite(StepPin,LOW);
  delayMicroseconds(microDelay);
}

void PulseAmount(int StepPin, int Amount, int microDelay = 250)
{
  for(int i = 0; i < Amount; i++)
  {
    Pulse(StepPin, microDelay);
  }
}

void ResetMotors(bool resetX, bool resetY, bool resetZ)
{
  digitalWrite(XDir,LOW);
  digitalWrite(YDir,LOW);
  digitalWrite(ZDir,LOW);

  XPulseDelay = 0;
  YPulseDelay = 0;
  ZPulseDelay = 0;

  XDelayIndex = 0;
  YDelayIndex = 0;
  ZDelayIndex = 0;

  CurrentXVel = 0;
  CurrentYVel = 0;
  CurrentZVel = 0;

  bool XLimitHit = !resetX;
  bool YLimitHit = !resetY;
  bool ZLimitHit = !resetZ;
  
  while(!XLimitHit || !YLimitHit || !ZLimitHit)
  {
    if(digitalRead(XLimit) == 0)
    {
      XLimitHit = true;
      CurrentXPos = 0;
      CurrentXDir = -1;
      CurrentXDes = 0;
    }
    if(digitalRead(YLimit) == 0)
    {
      YLimitHit = true;
      CurrentYPos = 0;
      CurrentYDir = -1;
      CurrentYDes = 0;
    }
    if(digitalRead(ZLimit) == 0)
    {
      ZLimitHit = true;
      CurrentZPos = 0;
      CurrentZDir = -1;
      CurrentZDes = 0;
    }

    if(!XLimitHit)
    {
      Pulse(XStep);
    }
    
    if(!YLimitHit)
    {
      Pulse(YStep);
    }
    
    if(!ZLimitHit) Pulse(ZStep,1000);
  }
  
  if(resetX)
  {
  CurrentXDir = 1;
  digitalWrite(XDir,HIGH);
  PulseAmount(XStep,100);
  CurrentXDes = 100;
  CurrentXPos = 100;
  }

  if(resetY)
  {
  CurrentYDir = 1;
  digitalWrite(YDir,HIGH);
  PulseAmount(YStep,100);
  CurrentYDes = 100;
  CurrentYPos = 100;
  }
}

void SetZPos(int ZDes)
{
  CurrentZDes = ZDes;
  
  if(ZDes > CurrentZPos)
  {
    CurrentZDir = 1;
    CurrentZVel = ZPulseDelay;
    digitalWrite(ZDir, HIGH);
  }
  else if(ZDes < CurrentZPos)
  {
    CurrentZDir = -1;
    CurrentZVel = -ZPulseDelay;
    digitalWrite(ZDir, LOW);
  }
  else
  {
    CurrentZVel = 0;
  }
}

void SetXYPos(int XDes, int YDes)
{
  if(XDes > XMaxStep) XDes = XMaxStep;
  else if(XDes < 0) XDes = 0;

  if(YDes > YMaxStep) YDes = YMaxStep;
  else if(YDes < 0) YDes = 0;
  
  CurrentXDes = XDes;
  CurrentYDes = YDes;
  
  if(XDes > CurrentXPos)
  {
    CurrentXDir = 1;
    CurrentXVel = XPulseDelay;
    digitalWrite(XDir, HIGH);
  }
  else if(XDes < CurrentXPos)
  {
    CurrentXDir = -1;
    CurrentXVel = -XPulseDelay;
    digitalWrite(XDir, LOW);
  }
  else
  {
    CurrentXVel = 0;
  }
  
  if(YDes > CurrentYPos)
  {
    CurrentYDir = 1;
    CurrentYVel = YPulseDelay;
    digitalWrite(YDir, HIGH);
  }
  else if(YDes < CurrentYPos)
  {
    CurrentYDir = -1;
    CurrentYVel = -YPulseDelay;
    digitalWrite(YDir, LOW);
  }
  else
  {
    CurrentYVel = 0;
  }
}

bool UpdatePosition() 
{
  bool moving = false;
  
  if(CurrentXPos != CurrentXDes)
  {
    moving = true;
    
    if(XDelayIndex >= XPulseDelay)
    {
      XDelayIndex = 0;  
      Pulse(XStep);
      CurrentXPos += CurrentXDir;
    }
    else
    {
      XDelayIndex++;
    }
  }
  else 
  {
    CurrentXVel = 0;
  }

  if(CurrentYPos != CurrentYDes)
  {
    moving = true;
    
    if(YDelayIndex >= YPulseDelay)
    {
      YDelayIndex = 0;  
      Pulse(YStep);
      CurrentYPos += CurrentYDir;
    }
    else
    {
      YDelayIndex++;
    }
  }
  else 
  {
    CurrentYVel = 0;
  }

  if(CurrentZPos != CurrentZDes)
  {
    moving = true;
    
    if(ZDelayIndex >= ZPulseDelay)
    {
      ZDelayIndex = 0;  
      Pulse(ZStep,1000);
      CurrentZPos += CurrentZDir;
    }
    else
    {
      ZDelayIndex++;
    }
  }
  else 
  {
    CurrentZVel = 0;
  }  

  if(digitalRead(XLimit) == 0 && CurrentXDir < 0)
  {
    CurrentXPos = 1;
    CurrentXDes = 10;
    CurrentXDir = 1;
    digitalWrite(XDir,HIGH);

    Pulse(XStep);
  }
  
  if(digitalRead(YLimit) == 0 && CurrentYDir < 0)
  {
    CurrentYPos = 1;
    CurrentYDes = 10;
    CurrentYDir = 1;
    digitalWrite(YDir,HIGH);

    Pulse(YStep);
  }
  
  if(digitalRead(ZLimit) == 0 && CurrentZDir < 0)
  { 
    CurrentZPos = 0;
    CurrentZDes = 0;
  }

  return moving;
}

void XSpeedTest()
{
  SetXYPos(10,812);
  while(UpdatePosition()){}

  for(int i = 5; i < 25; i++)
  {
    XPulseDelay = i;

    Serial.print(i);
    Serial.print(" ");

    if(i%2 == 1) SetXYPos(XMaxStep-10,812);
    else SetXYPos(10,812);

    long int start = micros();

    while(UpdatePosition()){}

    long int end = micros();

    Serial.println(end - start);
  }
}

void ZSpeedTest()
{
  SetZPos(1);
  while(UpdatePosition()) {}

  for(int i = 0; i < 20; i++)
  {
    ZPulseDelay = i;

    Serial.print(i);
    Serial.print(" ");

    if(i%2 == 1) SetZPos(ZLowStep);
    else SetZPos(1);

    long int start = millis();

    while(UpdatePosition()){}

    long int end = millis();

    Serial.println(end - start);
  }
}

void UpdateRoutine(bool isMoving)
{
  if(isMoving) return;
  switch(RoutineState)
  {
    case -3:
      RoutineState = -2;
      break;
    case -2:
      break;

    case -1:
      RoutineIteration++;
    case 0:
      if(RoutineIteration >= RoutineCount)
      {
        RoutineState = -2;
      }
      RoutineState = 1;
      break;

    case 1:
      XPulseDelay = 5;
      YPulseDelay = 3;
      SetXYPos(1816,812);
      RoutineState++;
      break;

    case 2:
      ZPulseDelay = 9;
      SetZPos(500);
      RoutineState = -3;
      break;
  }
}

void SendAllKinematicData()
{
  unsigned long time = micros();

  Serial.write(time >> 24);
  Serial.write(time >> 16);
  Serial.write(time >> 8);
  Serial.write(time);

  Serial.write(CurrentXPos >> 8);
  Serial.write(CurrentXPos);

  Serial.write(CurrentYPos >> 8); 
  Serial.write(CurrentYPos);

  Serial.write(CurrentZPos >> 8);
  Serial.write(CurrentZPos); 

  Serial.write(CurrentXVel);
  Serial.write(CurrentYVel);
  Serial.write(CurrentZVel);
  /*
  Serial.print(CurrentXPos);
  Serial.print(' ');
  Serial.print(CurrentYPos);
  Serial.print(' ');
  Serial.print(CurrentZPos);
  Serial.print(' ');
  Serial.print(CurrentXVel);
  Serial.print(' ');
  Serial.print(CurrentYVel);
  Serial.print(' ');
  Serial.println(CurrentZVel);
  Serial.print(' ');
  */
}

void SendPartKinematicData(int loopCount)
{
  if(RoutineState == -2) return;
  switch(loopCount)
  {
    case 1:
      SendZPos = CurrentZPos;
      SendXVel = CurrentXVel;
      SendYVel = CurrentYVel;
      SendZVel = CurrentZVel;
      Serial.write((CurrentXPos << 16) | CurrentYPos);
      break;
    case 2:
      Serial.write((CurrentZPos << 16) | (SendXVel << 8) | SendYVel);
      Serial.write(SendZVel);
      break;
    default:
      break;
  }
}

void setup() {
  pinMode(XStep,OUTPUT);
  pinMode(XDir,OUTPUT);
  pinMode(YStep,OUTPUT);
  pinMode(YDir,OUTPUT);
  pinMode(ZStep,OUTPUT);
  pinMode(ZDir,OUTPUT);

  pinMode(XLimit,INPUT_PULLUP);
  pinMode(YLimit,INPUT_PULLUP);
  pinMode(ZLimit,INPUT_PULLUP);

  Serial.begin(115200);

  ResetMotors(true, true, false);

  ResetMotors(false, false, true);

  sendIntervalStart = micros();
}

int loopCount = 0;

void loop(){
  UpdateRoutine(UpdatePosition());
  loopCount++;

  //SendPartKinematicData(loopCount);
  //Serial.println((uint32_t)micros());

  if(micros() - sendIntervalStart >= sendInterval && RoutineState != -2)
  {
    SendAllKinematicData();
    //Serial.println(micros() - sendIntervalStart);
    //Serial.println(loopCount);
    loopCount = 0;
    sendIntervalStart = micros();
  }
}