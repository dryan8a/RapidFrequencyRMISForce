using System;
using System.Collections.Generic;
using System.IO.Ports;

namespace DataCollector
{
    class Program
    {
        
        [STAThread]
        public static void Main(string[] args)
        {
            Console.WriteLine("Start search");

            //KinematicDataCollector.Initialize();
            ForceDataCollector.Initialize();
            
            while (true) 
            {
                //KinematicDataCollector.TryAppendData();
                ForceDataCollector.TryAppendData();
            }
        }


    }
}
