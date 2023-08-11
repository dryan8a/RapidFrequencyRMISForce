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
        static Queue<byte> RecievedKinematicData = new Queue<byte>();

        public static List<uint> Timestamps = new List<uint>();
        public static Dictionary<uint, KinematicDatum> KinematicData = new Dictionary<uint, KinematicDatum>();


        [STAThread]
        public static void Initialize()
        {
            MotorSerialPort.DataReceived += MotorSerialPort_DataReceived;
            if(!MotorSerialPort.IsOpen) MotorSerialPort.Open();
        }

        public static void StopCollection()
        {
            MotorSerialPort.Close();
        }
        

        private static void MotorSerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            byte[] data = new byte[MotorSerialPort.BytesToRead];
            MotorSerialPort.Read(data, 0, data.Length);

            foreach (byte b in data)
            {
                //Console.WriteLine(b);
                RecievedKinematicData.Enqueue(b);
            }
        }
        public static void test()
        {
            int testing = 0;
        }
        public static bool TryAppendData()
        {
            if(RecievedKinematicData.Count >= 13)
            {
                uint timestamp = 0;
                for(int i = 3; i >= 0; i--)
                {
                   timestamp += (uint)(RecievedKinematicData.Dequeue() << (8*i));
                }

                ushort xPos = (ushort)(RecievedKinematicData.Dequeue() << 8);
                xPos += RecievedKinematicData.Dequeue();

                ushort yPos = (ushort)(RecievedKinematicData.Dequeue() << 8);
                yPos += RecievedKinematicData.Dequeue();

                ushort zPos = (ushort)(RecievedKinematicData.Dequeue() << 8);
                zPos += RecievedKinematicData.Dequeue();

                byte xVel = RecievedKinematicData.Dequeue();
                byte yVel = RecievedKinematicData.Dequeue();
                byte zVel = RecievedKinematicData.Dequeue();

                KinematicData.Add(timestamp,new KinematicDatum(xPos,yPos,zPos,xVel,yVel,zVel));
                Timestamps.Add(timestamp);
                return true;
            }
            return false;
        }
    }
}
