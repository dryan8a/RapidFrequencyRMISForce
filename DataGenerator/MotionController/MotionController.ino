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

int8_t CurrentXDir;
int8_t CurrentYDir;
int8_t CurrentZDir;

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

//Boundaries
const short XMaxStep = 3632;
const short YMaxStep = 1624;
const short ZLowStep = 1700;
const short ZStartStep = 500;
const short ZSyncStep = 220;

short RoutineState = 0;
short RoutineIteration = 0;
const short RoutineCount = 10;

long sendIntervalStart;
long programStart;
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

void SendEndData()
{
  for(int i = 0; i < 4; i++)
  {
    Serial.write(255);
  }
}

void SendPauseData()
{
  for(int i = 0; i < 4; i++)
  {
    Serial.write(254);
  }
}

void UpdateRoutine(bool isMoving)
{
  if(isMoving) return;
  switch(RoutineState)
  {
    case -3:
      RoutineState = -2;
      SendEndData();
      break;
    case -2:
      break;

    case -1:
      RoutineIteration++;
    case 0:
      if(RoutineIteration >= RoutineCount)
      {
        RoutineState = -3;
      }
      else if(RoutineIteration > 0)
      {
        SendPauseData();

        ResetMotors(true,false,false);
        ResetMotors(false,true,false);

        SetXYPos(5,812);
        while(UpdatePosition()){}
        SetXYPos(1812,816);
        while(UpdatePosition()){}
        RoutineIteration++;
        RoutineState = 1;
        SendPauseData();
        SetZPos(ZSyncStep);
      }
      else
      {
        RoutineIteration++;
        RoutineState = 1;
      }
      break;

    case 1:
      ZPulseDelay = 3;
      SetZPos(400);
      RoutineState++;
      break;

    case 2:
      XPulseDelay = 7;
      YPulseDelay = 5;
      SetXYPos(2120, 700);
      RoutineState++;
      break;

    case 3:
      ZPulseDelay = 2;
      SetZPos(160);
      RoutineState++;
      break;
    
    case 4:
      ZPulseDelay = 10;
      SetZPos(300);
      RoutineState++;
      break;
    
    case 5:
      XPulseDelay = 4;
      YPulseDelay = 9;
      SetXYPos(1900,485);
      SetZPos(150);
      RoutineState++;
      break;
    
    case 6:
      XPulseDelay = 9;
      YPulseDelay = 2;
      ZPulseDelay = 6;
      SetXYPos(1400,800);
      SetZPos(500);
      RoutineState++;
      break;

    case 7:
      XPulseDelay = 11;
      YPulseDelay = 11;
      SetXYPos(1400,465);
      RoutineState++;
      break;
    
    case 8:
      XPulseDelay = 7;
      YPulseDelay = 12;
      SetXYPos(1300,470);
      RoutineState++;
      break;

    case 9:
      XPulseDelay = 5;
      YPulseDelay = 3;
      ZPulseDelay = 8;
      SetXYPos(1450,1200);
      SetZPos(100);
      RoutineState++;
      break;

    case 10:
      XPulseDelay = 2;
      ZPulseDelay = 2;
      SetXYPos(2130,1200);
      SetZPos(375);
      RoutineState++;
      break;
    
    case 11:
      XPulseDelay = 2;
      YPulseDelay = 3;
      SetXYPos(1750,480);
      SetZPos(475);
      RoutineState++;
      break;
    
    case 12:
      XPulseDelay = 4;
      YPulseDelay = 1;
      ZPulseDelay = 1;
      SetXYPos(1800,600);
      SetZPos(150);
      RoutineState++;
      break;
    
    case 13:
      SetXYPos(1850,620);
      SetZPos(250);
      RoutineState++;
      break;
    
    case 14:
      SetZPos(100);
      RoutineState++;
      break;
    
    case 15:
      ZPulseDelay = 10;
      SetZPos(300);
      RoutineState++;
      break;

    case 16:
      ZPulseDelay = 6;
      SetZPos(10);
      RoutineState++;
      break;
    
    case 17:
      SetXYPos(1820,440);
      SetZPos(300);
      RoutineState++;
      break;

    case 18:
      ZPulseDelay = 14;
      SetXYPos(2145,600);
      SetZPos(320);
      RoutineState++;
      break;
    
    case 19:
      SetXYPos(2150,700);
      RoutineState++;
      break;
    
    case 20:
      XPulseDelay++;
      YPulseDelay += 2;
      SetXYPos(1900,460);
      RoutineState++;
      break;
    
    case 21:
      ZPulseDelay = 7;
      SetZPos(40);
      RoutineState++;
      break;
    
    case 22:
      XPulseDelay++;
      YPulseDelay++;
      ZPulseDelay -= 3;
      SetXYPos(1800, 800);
      SetZPos(320);
      RoutineState++;
      break;
    
    case 23:
      SetXYPos(2130,450);
      SetZPos(405);
      RoutineState++;
      break;
    
    case 24:
      SetXYPos(1816,812);
      RoutineState++;
      break;

    case 25:
      XPulseDelay++;
      YPulseDelay = 2;
      ZPulseDelay = 3;
      SetXYPos(1350,700);
      SetZPos(175);
      RoutineState++;
      break;

    case 26:
      SetXYPos(1365, 420);
      SetZPos(250);
      RoutineState++;
      break;
    
    case 27:
      SetXYPos(1365,550);
      SetZPos(300);
      RoutineState++;
      break;
    
    case 28:
      SetXYPos(1365,425);
      RoutineState++;
      break;
    
    case 29:
      YPulseDelay = 4;
      SetXYPos(1365,525);
      RoutineState++;
      break;
    
    case 30:
      SetXYPos(1365,425);
      RoutineState++;
      break;
    
    case 31:
      SetXYPos(1375,600);
      SetZPos(150);
      RoutineState++;
      break;
    
    case 32: 
      XPulseDelay = 3;
      YPulseDelay = 5;
      ZPulseDelay = 6;
      SetXYPos(2140,1150);
      SetZPos(380);
      RoutineState++;
      break;
    
    case 33:
      SetXYPos(2000,1100); 
      SetZPos(130);
      RoutineState++;
      break;
    
    case 34:
      XPulseDelay = 4;
      ZPulseDelay = 2;
      SetXYPos(2135,1050);
      SetZPos(175);
      RoutineState++;
      break;
    
    case 35:
      YPulseDelay = 6;
      SetXYPos(2050,430);
      SetZPos(250);
      RoutineState++;
      break;

    case 36:
      XPulseDelay++;
      YPulseDelay--;
      ZPulseDelay = 1;
      SetXYPos(1750,900);
      SetZPos(120);
      RoutineState++;
      break;
    
    case 37:
      SetXYPos(1812,816);
      SetZPos(400);
      RoutineState = 0;
      break;
  }
}

void SendAllKinematicData()
{
  unsigned long time = micros() - programStart;

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

  //Serial.write(CurrentXVel);
  //Serial.write(CurrentYVel);
  //Serial.write(CurrentZVel);

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

  ResetMotors(true, false, false);
  ResetMotors(false, true, false);

  ResetMotors(false, false, true);

  SetZPos(ZLowStep);
  while(UpdatePosition()){}

  SetXYPos(1816,812);
  while(UpdatePosition()){}

  SetZPos(ZStartStep);  
  while(UpdatePosition()){}

  ZPulseDelay = 9;

  while(!Serial.available()){}
  Serial.read();

  SetZPos(ZSyncStep);
  while(UpdatePosition()){}

  programStart = micros();
  sendIntervalStart = programStart;
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