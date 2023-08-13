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
        static SerialPort ForceSerialPort = new SerialPort("COM?", 115200, Parity.None, 8, StopBits.One);
        static Queue<byte> RecievedData = new Queue<byte>();

        public static Dictionary<uint, ForceInputDatum> ForceData = new Dictionary<uint, ForceInputDatum>();

        const double MaxVoltage = 5000; //mV
        const int MaxInput = 1023;
        const int ResistorValue = 10000; //Ohms

        public static void Initialize()
        {
            ForceSerialPort.DataReceived += ForceSerialPort_DataReceived;
            if (!ForceSerialPort.IsOpen) ForceSerialPort.Open();
        }

        private static void ForceSerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            byte[] data = new byte[ForceSerialPort.BytesToRead];
            ForceSerialPort.Read(data, 0, data.Length);

            foreach (byte b in data)
            {
                //Console.WriteLine(b);
                RecievedData.Enqueue(b);
            }
        }

        public static bool TryAppendData()
        {
            if(RecievedData.Count >= 16)
            {
                ushort[] floorData = new ushort[4];
                for(int i = 0; i < 4; i++)
                {
                    floorData[i] = RecievedData.Dequeue();
                }
                //do the rest of this

                return true;
            }
            return false;
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
