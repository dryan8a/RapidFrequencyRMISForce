using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
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

    static class ForceDataCollector
    {
        static SerialPort ForceSerialPort = new SerialPort("COM?", 115200, Parity.None, 8, StopBits.One);
        static Queue<byte> RecievedData = new Queue<byte>();

        const int MaxVoltage = 5000; //mV
        const int MaxInput = 1023;

        public static void Initialize()
        {
            ForceSerialPort.DataReceived += ForceSerialPort_DataReceived;
            if (!ForceSerialPort.IsOpen) ForceSerialPort.Open();
        }

        private static void ForceSerialPort_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            throw new NotImplementedException();
        }

        static int MapInputToVoltage(int input)
        {
            return input * MaxVoltage / MaxInput;
        }


    }
}
