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

short CurrentXDir;
short CurrentYDir;
short CurrentZDir;


//Boundaries
const short XMaxStep = 3632;
const short YMaxStep = 1624;
const short ZLowStep = 300; //Step position that moves touchscreen out of reach


//Movement to pixels (as coordinates)
const short XCoordMin = 502;
const short XCoordMax = 2779;

const short YCoordMin = 55;
const short YCoordMax = 1342;

const short CoordStep = 99;


//Queue 
byte queueIn[300];
byte queueOut[300];
short queueInIndex;
short queueOutIndex;


//State machine variables
int state = 0;
byte instr1 = 0;
byte instr2 = 0;
byte instr3 = 0;

byte HelloMessage[] = {0xDA, 0xDA};

//float slope;
//float error;
//bool vertical = false;


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
    digitalWrite(ZDir, HIGH);
  }
  else
  {
    CurrentZDir = -1;
    digitalWrite(ZDir, LOW);
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
    digitalWrite(XDir, HIGH);
  }
  else
  {
    CurrentXDir = -1;
    digitalWrite(XDir, LOW);
  }
  
  if(YDes > CurrentYPos)
  {
    CurrentYDir = 1;
    digitalWrite(YDir, HIGH);
  }
  else
  {
    CurrentYDir = -1;
    digitalWrite(YDir, LOW);
  }
}

int gcd(int a, int b)
{
  int t;
  while (b != 0)
  {
    t = b;
    b = a % b;
    a = t;
  }
  return a;
}

void SetXYCoord(int XCoord, int YCoord)
{
  if(XCoord > 23) XCoord = 23;
  if(XCoord < 0) XCoord = 0;
  if(YCoord > 13) YCoord = 13;
  if(YCoord < 0) YCoord = 0;

  int XDes = CoordStep * XCoord + XCoordMin;
  int YDes = CoordStep * YCoord + YCoordMin;

  //if (XDes == CurrentXPos)
  //{
  //  vertical = true;
  //}
  //else
  //{
  //  vertical = false;
    
  //  slope = (float)abs(YDes - CurrentYPos)/(float)abs(XDes - CurrentXPos);
  //  error = (float)CoordStep / 2;
  //}
  
  SetXYPos(XDes, YDes);
}

//returns whether any of the motors are currently moving
bool UpdatePosition() 
{
  bool moving = false;
  
  if(CurrentXPos != CurrentXDes) //&& CurrentYPos == CurrentYDes && !vertical)
  {
    moving = true;
    
    Pulse(XStep);
    CurrentXPos += CurrentXDir;
    //error += slope;

    //while (error > CoordStep)
    //{
    //  error -= CoordStep;
    //  CurrentYDes += CoordStep;
    //  delay(10);
    //}
  }
  if(CurrentYPos != CurrentYDes)
  {
    moving = true;
    
    Pulse(YStep);
    CurrentYPos += CurrentYDir;
  }
  if(CurrentZPos != CurrentZDes)
  {
    moving = true;
    
    Pulse(ZStep,1000);
    CurrentZPos += CurrentZDir;
  }
  
  if(digitalRead(XLimit) == 0 && CurrentXDir < 0)
  {
    CurrentXPos = 10;
    CurrentXDes = 10;
    CurrentXDir = 1;
      digitalWrite(XDir,HIGH);

    PulseAmount(XStep,10);
  }
  
  if(digitalRead(YLimit) == 0 && CurrentYDir < 0)
  {
    CurrentYPos = 10;
    CurrentYDes = 10;
    CurrentYDir = 1;
      digitalWrite(YDir,HIGH);
    PulseAmount(YStep,10);
  }
  
  if(digitalRead(ZLimit) == 0 && CurrentZDir < 0)
  { 
    CurrentZPos = 0;
    CurrentZDes = 0;
  }

  return moving;
}

void Enqueue(byte datum)
{
  queueInIndex++;
  queueIn[queueInIndex] = datum;
}

byte Dequeue()
{
  if(queueOutIndex < 0)
  {
    for(int i = queueInIndex; i > -1; i--)
    {
      queueOutIndex++;
      queueOut[queueOutIndex] = queueIn[i];
    }
    queueInIndex = -1;
  }
  
  byte datum = queueOut[queueOutIndex];
  queueOutIndex--;
  
  return datum;
}

int QueueCount()
{
  return queueOutIndex + queueInIndex + 2;
}

void ReadOneByte(byte b)
{
    Serial.write(b);
    switch (state)
    {
        case 0:
            if (b == 0xCA)
            {
                state = 1;
            }
            break;
        case 1:
            if (b == 0xFE)
            {
                state = 2;
                break;
            }
            state = 0;
            break;
        case 2:
            if (b == 0xBA)
            {
                state = 3;
                break;
            }
            state = 0;
            break;
        case 3:
            if (b == 0xBE)
            {
                state = 4;
                break;
            }
            state = 0;
            break;
        case 4:
            instr1 = b;
            state = 7;
            if (b == 0x03)
            {
                state = 5;
            }
            else if (b == 0 || b > 0x03)
            {
                state = 0;
            }
            break;
        case 5:
            //if (b > 23)
            //{
            //    state = 0;
            //    break;
            //}
            
            instr2 = b;
            state = 6;
            break;
        case 6:
            //if (b > 13)
            //{
            //    state = 0;
            //    break;
            //}

            instr3 = b;
            state = 7;
            break;
        case 7:
            if (b == 0xBE)
            {
                state = 8;
                break;
            }

            state = 0;
            break;
        case 8:
            if (b == 0xBE)
            {
                state = 9;
                break;
            }

            state = 0;
            break;
        case 9:
            if (b == 0xBA)
            {
                state = 10;
                break;
            }

            state = 0;
            break;
        case 10:
            state = 0;
            if (b != 0xBA)
            {
                break;
            }

            Enqueue(instr1);

            if (instr1 == 0x03)
            {
                Enqueue(instr2);
                Enqueue(instr3);
            }
            
            //Serial.write(0xFF);
            break;
    }
    //Serial.write((byte)state);
}

void setup()
{
  pinMode(XStep,OUTPUT);
  pinMode(XDir,OUTPUT);
  pinMode(YStep,OUTPUT);
  pinMode(YDir,OUTPUT);
  pinMode(ZStep,OUTPUT);
  pinMode(ZDir,OUTPUT);

  pinMode(XLimit,INPUT_PULLUP);
  pinMode(YLimit,INPUT_PULLUP);
  pinMode(ZLimit,INPUT_PULLUP);

  queueInIndex = -1;
  queueOutIndex = -1;
  
  Serial.begin(9600);
  
  //digitalWrite(ZDir, HIGH);
  //PulseAmount(ZStep, ZLowStep, 1000);
  
  ResetMotors(true, true, false);

  ResetMotors(false, false, true);
  
  SetZPos(ZLowStep);

  while(UpdatePosition()) {}
  
  //Serial.write(HelloMessage,2);

  SetXYPos(1816,812);
  while(UpdatePosition()){}

  SetZPos(0);
  while(UpdatePosition()){}

  SetXYPos(2200,1624);
  while(UpdatePosition()){}
}

void loop()
{
  /*if(Serial.available() > 0) ReadOneByte(Serial.read());
  bool moving = UpdatePosition();

  if(!moving && QueueCount() > 0)
  {
    byte inst = Dequeue();
    switch(inst)
    {
      case 1:
        SetZPos(0);
        break;
      
      case 2:
        SetZPos(ZLowStep);
        break;
      
      case 3:
        byte x = Dequeue();
        byte y = Dequeue();

        SetXYCoord(x,y);
        break;
    }
  }
  */
}
