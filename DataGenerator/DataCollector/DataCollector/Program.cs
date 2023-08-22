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
            string TrainingPath = @"C:\Users\dryan\Documents\PioneerAcademics2023\TrainingData.txt";
            string RanTrainingPath = @"C:\Users\dryan\Documents\PioneerAcademics2023\RandomizedTrainingData.txt";
            string RanNormTrainingPath = @"C:\Users\dryan\Documents\PioneerAcademics2023\RandomizedNormalizedTrainingData.txt";


            StreamWriter outputWriter = new StreamWriter(OutputPath);
            DataSynchronizer.OutputData(outputWriter);
            outputWriter.Close();

            DataSynchronizer.CompileTrainingData();

            StreamWriter trainingWriter = new StreamWriter(TrainingPath);
            DataSynchronizer.OutputTrainingData(trainingWriter);
            trainingWriter.Close();

            StreamWriter ranTrainingWriter = new StreamWriter(RanTrainingPath);
            StreamWriter ranNormTrainingWriter = new StreamWriter(RanNormTrainingPath);
            DataSynchronizer.OutputRandomizedTrainingData(ranTrainingWriter, ranNormTrainingWriter);
            ranTrainingWriter.Close();
            ranNormTrainingWriter.Close();
            
            Console.WriteLine("Output Data");
        }


    }
}
