using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Schema;

namespace DataCollector
{
    public struct KinematicInputDatum
    {
        public ushort XPos;
        public ushort YPos;
        public ushort ZPos;

        public KinematicInputDatum() { }
        public KinematicInputDatum(ushort xPos,ushort yPos,ushort zPos)
        {
            XPos = xPos;
            YPos = yPos;
            ZPos = zPos;
        }
    }
    public struct KinematicDatum
    {
        public ushort XPos;
        public ushort YPos;
        public ushort ZPos;
        public double XVel;
        public double YVel;
        public double ZVel;
        public KinematicDatum() { }
        public KinematicDatum(ushort xPos, ushort yPos, ushort zPos, double xVel, double yVel, double zVel)
        {
            XPos = xPos;
            YPos = yPos;
            ZPos = zPos;
            XVel = xVel;
            YVel = yVel;
            ZVel = zVel;
        }
        public KinematicDatum(KinematicInputDatum inputDatum, double xVel, double yVel, double zVel)
        {
            XPos = inputDatum.XPos;
            YPos = inputDatum.YPos;
            ZPos = inputDatum.ZPos;
            XVel = xVel;
            YVel = yVel;
            ZVel = zVel;
        }
    }

    public static class KinematicDataCollector
    {
        static SerialPort MotorSerialPort = new SerialPort("COM5", 115200, Parity.None, 8, StopBits.One);
        static Queue<byte> RecievedData = new Queue<byte>();

        public static bool IsOpen => MotorSerialPort.IsOpen;

        public static List<uint> Timestamps = new List<uint>();
        public static Dictionary<uint, KinematicInputDatum> KinematicData = new Dictionary<uint, KinematicInputDatum>();

        private static int EndSequenceCount = 0;
        private static int PauseSequenceCount = 0;
        private static bool Paused = false;

        public const ushort XMin = 1100;
        public const ushort YMin = 300;
        public const ushort ZMin = 0;

        [STAThread]
        public static void Initialize()
        {
            if(!MotorSerialPort.IsOpen) MotorSerialPort.Open();

            MotorSerialPort.Write(new byte[] { 111 }, 0, 1);
        }

        public static void StopCollection()
        {
            MotorSerialPort.Close();
        }
        
        public static bool TryAppendData()
        {
            bool isTrying = false;
            if (MotorSerialPort.IsOpen && MotorSerialPort.BytesToRead > 0)
            {
                isTrying = true;

                byte[] data = new byte[MotorSerialPort.BytesToRead];
                MotorSerialPort.Read(data, 0, data.Length);

                foreach (byte b in data)
                {
                    if (b == 0xFF) EndSequenceCount++;
                    else EndSequenceCount = 0;
                    if (b == 0xFE) PauseSequenceCount++;
                    else PauseSequenceCount = 0;
                    

                    if (PauseSequenceCount >= 4)
                    {
                        PauseSequenceCount = 0;
                        Paused = !Paused;
                        
                        ForceDataCollector.TogglePause();
                        Console.WriteLine("Paused");
                        if (Paused)
                        {
                            RecievedData.Clear();
                            break;
                        }
                        else continue;
                    }

                    //Console.WriteLine(b);
                    if (!Paused) RecievedData.Enqueue(b);

                    if (EndSequenceCount >= 4)
                    {
                        StopCollection();
                        break;
                    }
                }
            }

            if (RecievedData.Count >= 10)
            {
                isTrying = true;

                uint timestamp = 0;
                for(int i = 3; i >= 0; i--)
                {
                   timestamp += (uint)(RecievedData.Dequeue() << (8*i));
                }

                ushort xPos = (ushort)(RecievedData.Dequeue() << 8);
                xPos += RecievedData.Dequeue();

                ushort yPos = (ushort)(RecievedData.Dequeue() << 8);
                yPos += RecievedData.Dequeue();

                ushort zPos = (ushort)(RecievedData.Dequeue() << 8);
                zPos += RecievedData.Dequeue();

                //Hardware "velocity"
                //sbyte xVel = (sbyte)RecievedData.Dequeue();
                //sbyte yVel = (sbyte)RecievedData.Dequeue();
                //sbyte zVel = (sbyte)RecievedData.Dequeue();

                KinematicData.Add(timestamp,new KinematicInputDatum(xPos,yPos,zPos));
                Timestamps.Add(timestamp);
            }

            return isTrying;
        }

        //old hardware "velcoity" conversion
        //public static KinematicDatum InputToKinematic(KinematicInputDatum input)
        //{
        //    var xPos = (ushort)(input.XPos - XMin);
        //    var yPos = (ushort)(input.YPos - YMin);

        //    var xVel = input.XVel == 0 ? 0 : 1.0 / input.XVel;
        //    var yVel = input.YVel == 0 ? 0 : 1.0 / input.YVel;
        //    var zVel = input.ZVel == 0 ? 0 : 1.0 / input.ZVel;

        //    return new KinematicDatum(xPos, yPos, input.ZPos, xVel, yVel, zVel);
        //}
    }
}
