using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
using System.Net.Http.Headers;
using System.Text;
using System.Threading.Tasks;
using System.Transactions;

namespace DataCollector
{
    public struct ForceDatum
    {
        public double XForce;
        public double YForce;
        public double ZForce;

        public ForceDatum(double xForce, double yForce, double zForce)
        {
            XForce = xForce;
            YForce = yForce;
            ZForce = zForce;
        }
    }

    public struct ForceInputDatum
    {
        public ushort XInputForce;
        public ushort YInputForce;
        public ushort ZInputForce;

        public ForceInputDatum(ushort xInputForce, ushort yInputForce, ushort zInputForce)
        {
            XInputForce = xInputForce;
            YInputForce = yInputForce;
            ZInputForce = zInputForce;
        }
    }

    static class ForceDataCollector
    {
        static SerialPort ForceSerialPort = new SerialPort("COM4", 115200);
        static Queue<byte> RecievedData = new Queue<byte>();

        public static Dictionary<uint, ForceInputDatum> ForceData = new Dictionary<uint, ForceInputDatum>();

        private static bool Paused = false;
        private static int PostPauseCount = 21;
        private static bool FoundNonZero = true;

        const double MaxVoltage = 5000; //mV
        const int MaxInput = 1023;
        const int ResistorValue = 10000; //Ohms

        public static void Initialize()
        {
            if (!ForceSerialPort.IsOpen) ForceSerialPort.Open();

            ForceSerialPort.DiscardInBuffer();
            ForceSerialPort.DiscardOutBuffer();

            ForceSerialPort.Write(new byte[] { 111 }, 0, 1);
        }

        public static void StopCollection()
        {
            ForceSerialPort.Close();
        }

        public static void TogglePause()
        {
            Paused = !Paused;
            //RecievedData.Clear();
            PostPauseCount = 0;
            FoundNonZero = false;
        }

        public static bool TryAppendData()
        {
            bool isTrying = false;

            if (ForceSerialPort.IsOpen && ForceSerialPort.BytesToRead >= 20)
            {
                isTrying = true;

                int div, rem;

                (div, rem) = Math.DivRem(ForceSerialPort.BytesToRead, 20);

                byte[] data = new byte[div*20];
                ForceSerialPort.Read(data, 0, data.Length);

                if (ForceData.Count == 0 && RecievedData.Count == 0 && data[0] == 128)
                {
                    data = data[1..];
                }

                if (Paused) return true;


                foreach (byte b in data)
                {
                    //Console.WriteLine(b);
                    if (!Paused)
                    {
                        PostPauseCount++;
                    }

                    if (!Paused && !(PostPauseCount <= 20 && b == 0 && !FoundNonZero))
                    {
                        RecievedData.Enqueue(b);
                        FoundNonZero = true;
                    }
                }
            }

            //if (Paused && RecievedData.Count > 0 && RecievedData.Count < 20)
            //{
            //    Console.WriteLine("Force Data Recieved Cleared");
            //    RecievedData.Clear();
            //}

            if (RecievedData.Count >= 20)
            {
                isTrying = true;

                uint timestamp = 0;
                for (int i = 3; i >= 0; i--)
                {
                    timestamp += (uint)(RecievedData.Dequeue() << (8 * i));
                }

                ushort[] floorData = new ushort[4] { 0, 0, 0, 0 };
                for(int floor = 0; floor < 4; floor++)
                {
                    for (int i = 1; i >= 0; i--)
                    {
                        floorData[floor] += (ushort)(RecievedData.Dequeue() << (8 * i));
                    }
                }

                ushort zInputForce = ushort.Max(floorData[0],ushort.Max(floorData[1],ushort.Max(floorData[2], floorData[3])));

                ushort xWall1 = (ushort)(RecievedData.Dequeue() << 8);
                xWall1 += RecievedData.Dequeue();

                ushort xWall2 = (ushort)(RecievedData.Dequeue() << 8);
                xWall2 += RecievedData.Dequeue();

                ushort xInputForce = ushort.Max(xWall1, xWall2);

                ushort yWall1 = (ushort)(RecievedData.Dequeue() << 8);
                yWall1 += RecievedData.Dequeue();

                ushort yWall2 = (ushort)(RecievedData.Dequeue() << 8);
                yWall2 += RecievedData.Dequeue();

                ushort yInputForce = ushort.Max(yWall1, yWall2);

                ForceData.Add(timestamp, new ForceInputDatum(xInputForce, yInputForce, zInputForce));

                Console.WriteLine($"{timestamp} {xInputForce} {yInputForce} {zInputForce}");
            }
            return isTrying;
        }

        public static ForceDatum InputToForce(ForceInputDatum input)
        {
            var xForce = VoltageToNewtons(MapInputToVoltage(input.XInputForce));
            var yForce = VoltageToNewtons(MapInputToVoltage(input.YInputForce));
            var zForce = VoltageToNewtons(MapInputToVoltage(input.ZInputForce));

            return new ForceDatum(xForce, yForce, zForce);
        }

        static double MapInputToVoltage(int input)
        {
            return input * MaxVoltage / MaxInput;
        }

        static double VoltageToNewtons(double voltage)
        {
            if (voltage == 0) return 0;

            double resistance = (5000 - voltage) * ResistorValue / voltage;

            double conductance = 1000000 / resistance;  //microMhos

            //please enjoy the following unexplained math magic
            double force;

            if (conductance <= 1000) force = conductance / 80;
            else force = (conductance - 1000) / 30;


            return force;
        }
    }
}
