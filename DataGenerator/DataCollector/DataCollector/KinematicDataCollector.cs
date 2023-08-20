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
        public sbyte XVel;
        public sbyte YVel;
        public sbyte ZVel;
        public KinematicDatum() { }
        public KinematicDatum(ushort xPos,ushort yPos,ushort zPos,sbyte xVel,sbyte yVel,sbyte zVel)
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

        public static bool IsOpen => MotorSerialPort.IsOpen;

        public static List<uint> Timestamps = new List<uint>();
        public static Dictionary<uint, KinematicDatum> KinematicData = new Dictionary<uint, KinematicDatum>();

        private static int EndSequenceCount = 0;

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

                    //Console.WriteLine(b);
                    RecievedData.Enqueue(b);

                    if (EndSequenceCount >= 4)
                    {
                        StopCollection();
                        break;
                    }
                }
            }

            if (RecievedData.Count >= 13)
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

                sbyte xVel = (sbyte)RecievedData.Dequeue();
                sbyte yVel = (sbyte)RecievedData.Dequeue();
                sbyte zVel = (sbyte)RecievedData.Dequeue();

                KinematicData.Add(timestamp,new KinematicDatum(xPos,yPos,zPos,xVel,yVel,zVel));
                Timestamps.Add(timestamp);
            }

            return isTrying;
        }
    }
}
