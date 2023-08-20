using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataCollector
{
    public struct KinematicDatum
    {
        public ushort XPos;
        public ushort YPos;
        public ushort ZPos;
        public byte XVel;
        public byte YVel;
        public byte ZVel;
        public KinematicDatum() { }
        public KinematicDatum(ushort xPos,ushort yPos,ushort zPos,byte xVel,byte yVel,byte zVel)
        {
            XPos = xPos;
            YPos = yPos;
            ZPos = zPos;
            XVel = xVel;
            YVel = yVel;
            ZVel = zVel;
        }
    }

    public static class KinematicDataCollector
    {
        static SerialPort MotorSerialPort = new SerialPort("COM3", 115200, Parity.None, 8, StopBits.One);
        static Queue<byte> RecievedData = new Queue<byte>();

        public static List<uint> Timestamps = new List<uint>();
        public static Dictionary<uint, KinematicDatum> KinematicData = new Dictionary<uint, KinematicDatum>();


        [STAThread]
        public static void Initialize()
        {
            if(!MotorSerialPort.IsOpen) MotorSerialPort.Open();
        }

        public static void StopCollection()
        {
            MotorSerialPort.Close();
        }
        
        public static bool TryAppendData()
        {
            if (MotorSerialPort.BytesToRead > 0)
            {
                byte[] data = new byte[MotorSerialPort.BytesToRead];
                MotorSerialPort.Read(data, 0, data.Length);

                foreach (byte b in data)
                {
                    //Console.WriteLine(b);
                    RecievedData.Enqueue(b);
                }
            }

            if (RecievedData.Count >= 13)
            {
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

                byte xVel = RecievedData.Dequeue();
                byte yVel = RecievedData.Dequeue();
                byte zVel = RecievedData.Dequeue();

                KinematicData.Add(timestamp,new KinematicDatum(xPos,yPos,zPos,xVel,yVel,zVel));
                Timestamps.Add(timestamp);
                return true;
            }
            return false;
        }
    }
}
