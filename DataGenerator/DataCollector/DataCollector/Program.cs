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
            KinematicDataCollector.Initialize();
            ForceDataCollector.Initialize();

            Console.WriteLine("Start collection");

            while (true) 
            {
                bool appendingKinData = KinematicDataCollector.TryAppendData();
                bool appendingForData = ForceDataCollector.TryAppendData();

                if (!KinematicDataCollector.IsOpen) ForceDataCollector.StopCollection();

                if(!KinematicDataCollector.IsOpen && !appendingForData && !appendingKinData)
                {
                    break;
                }
            }

            Console.WriteLine("Collection Finished");

            DataSynchronizer.SyncData();

            Console.WriteLine("Data Synced");

            string OutputPath = @"C:\Users\dryan\Documents\PioneerAcademics2023\GenerationOutput.txt";

            StreamWriter outputWriter = new StreamWriter(OutputPath);

            ;
        }


    }
}
