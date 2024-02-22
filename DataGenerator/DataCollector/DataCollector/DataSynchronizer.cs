using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Security;
using System.Text;
using System.Threading.Tasks;

namespace DataCollector
{
    public struct CombinedDatum
    {
        public uint Timestamp;
        public ForceDatum ForceDatum;
        public KinematicDatum KinematicDatum;

        public CombinedDatum(uint timestamp, ForceDatum forcedDatum, KinematicDatum kinematicDatum)
        {
            Timestamp = timestamp;
            ForceDatum = forcedDatum;
            KinematicDatum = kinematicDatum;
        }
    }

    public struct NNTrainingDatum
    {
        public uint TrueForceElapsedTime;
        public KinematicDatum CurrKinematicDatum;
        public ForceDatum PrevTrueForceDatum;   //most recent ground truth value
        public ForceDatum PrevForceDatum;
        public ForceDatum ForceDatumToPredict;

        public NNTrainingDatum(uint trueForceElapsedTime, KinematicDatum currKinematicDatum, ForceDatum prevTrueForceDatum, ForceDatum prevForceDatum, ForceDatum forceDatumToPredict)
        {
            TrueForceElapsedTime = trueForceElapsedTime;
            CurrKinematicDatum = currKinematicDatum;
            PrevForceDatum = prevForceDatum;
            ForceDatumToPredict = forceDatumToPredict;
            PrevTrueForceDatum = prevTrueForceDatum;
        }

    }

    public static class DataSynchronizer
    {
        private static int PreviousKinematicTimestampIndex;

        public static List<CombinedDatum> CombinedData = new List<CombinedDatum>();
        public static List<NNTrainingDatum> TrainingData = new List<NNTrainingDatum>();

        static DataSynchronizer()
        {
            PreviousKinematicTimestampIndex = 0;
        }

        public static void OutputData(StreamWriter outputWriter)
        {
            foreach(CombinedDatum datum in CombinedData) 
            {
                outputWriter.Write($"{datum.Timestamp} {datum.KinematicDatum.XPos} {datum.KinematicDatum.YPos} {datum.KinematicDatum.ZPos} {datum.KinematicDatum.XVel} {datum.KinematicDatum.YVel} {datum.KinematicDatum.ZVel} {datum.ForceDatum.XForce} {datum.ForceDatum.YForce} {datum.ForceDatum.ZForce}\n");
            }
        }

        public static void OutputTrainingData(StreamWriter outputWriter)
        {
            foreach(NNTrainingDatum datum in TrainingData)
            {
                outputWriter.Write($"{datum.TrueForceElapsedTime} {datum.CurrKinematicDatum.XPos} {datum.CurrKinematicDatum.YPos} {datum.CurrKinematicDatum.ZPos} {datum.CurrKinematicDatum.XVel} {datum.CurrKinematicDatum.YVel} {datum.CurrKinematicDatum.ZVel} {datum.PrevTrueForceDatum.XForce} {datum.PrevTrueForceDatum.YForce} {datum.PrevTrueForceDatum.ZForce} {datum.PrevForceDatum.XForce} {datum.PrevForceDatum.YForce} {datum.PrevForceDatum.ZForce} {datum.ForceDatumToPredict.XForce} {datum.ForceDatumToPredict.YForce} {datum.ForceDatumToPredict.ZForce}\n");
            }
        }


        /// <summary>
        /// Outputs training data in random order NOTE: deletes all data in TrainingData in the process
        /// </summary>
        /// <param name="ranOutputWriter"></param>
        public static void OutputRandomizedTrainingData(StreamWriter ranOutputWriter, StreamWriter ranNormOutputWriter) 
        {
            Random gen = new Random();
            for (int i = 0; i < TrainingData.Count;)
            {
                var indexToRemove = gen.Next(0, TrainingData.Count);

                var datum = TrainingData[indexToRemove];

                ranOutputWriter.Write($"{datum.TrueForceElapsedTime} {datum.CurrKinematicDatum.XPos} {datum.CurrKinematicDatum.YPos} {datum.CurrKinematicDatum.ZPos} {datum.CurrKinematicDatum.XVel} {datum.CurrKinematicDatum.YVel} {datum.CurrKinematicDatum.ZVel} {datum.PrevTrueForceDatum.XForce} {datum.PrevTrueForceDatum.YForce} {datum.PrevTrueForceDatum.ZForce} {datum.PrevForceDatum.XForce} {datum.PrevForceDatum.YForce} {datum.PrevForceDatum.ZForce} {datum.ForceDatumToPredict.XForce} {datum.ForceDatumToPredict.YForce} {datum.ForceDatumToPredict.ZForce}\n");

                //ranNormOutputWriter.Write($"");

                TrainingData.RemoveAt(indexToRemove);
            }
        }

        public static void SyncData()
        {
            foreach(var forDatumPair in ForceDataCollector.ForceData)
            {
                var timestampIndex = GetClosestKinematicTimestampIndex(forDatumPair.Key);
                var kinDatum = ApproximateCorrectedKinematicDatum(forDatumPair.Key, timestampIndex);

                var forDatum = ForceDataCollector.InputToForce(forDatumPair.Value);

                var combinedDatum = new CombinedDatum(forDatumPair.Key, forDatum, kinDatum);

                CombinedData.Add(combinedDatum);
            }
        }

        /// <summary>
        /// Compiles training data after being synced into the Neural Network Training data format
        /// </summary>
        /// <param name="groundTruthInterval">in microseconds</param>
        public static void CompileTrainingData(uint groundTruthInterval)
        {
            int currentGroundTruthIndex = 0;
            for(int i = 1; i < CombinedData.Count; i++) 
            {
                if (CombinedData[i].Timestamp - CombinedData[currentGroundTruthIndex].Timestamp > groundTruthInterval)
                {
                    currentGroundTruthIndex = i - 1;
                }
                TrainingData.Add(new NNTrainingDatum(CombinedData[i].Timestamp - CombinedData[currentGroundTruthIndex].Timestamp, CombinedData[i].KinematicDatum, CombinedData[currentGroundTruthIndex].ForceDatum, CombinedData[i - 1].ForceDatum, CombinedData[i].ForceDatum));
            }
        }

        public static int GetClosestKinematicTimestampIndex(uint timestamp)
        {
            for(int i = PreviousKinematicTimestampIndex;; i++)
            {
                if(i == KinematicDataCollector.Timestamps.Count - 1)
                {
                    return i;
                }

                if (timestamp >= KinematicDataCollector.Timestamps[i] && timestamp <= KinematicDataCollector.Timestamps[i+1])
                {
                    PreviousKinematicTimestampIndex = i;
                    return i;
                }
            }
        }

        public static KinematicDatum ApproximateCorrectedKinematicDatum(uint timestamp, int ClosestKinematicTimestampIndex)
        {
            uint befTimestamp, aftTimestamp, kinematicElapsed;
            double xVel, yVel, zVel;

            if (ClosestKinematicTimestampIndex >= KinematicDataCollector.Timestamps.Count - 1)
            {
                Console.WriteLine("More force than kin");

                befTimestamp = KinematicDataCollector.Timestamps[^2]; //second to last timestamp
                aftTimestamp = KinematicDataCollector.Timestamps[^1]; //last timestamp
                kinematicElapsed = aftTimestamp - befTimestamp;

                xVel = (double)(KinematicDataCollector.KinematicData[aftTimestamp].XPos - KinematicDataCollector.KinematicData[befTimestamp].XPos) / kinematicElapsed;
                yVel = (double)(KinematicDataCollector.KinematicData[aftTimestamp].YPos - KinematicDataCollector.KinematicData[befTimestamp].YPos) / kinematicElapsed;
                zVel = (double)(KinematicDataCollector.KinematicData[aftTimestamp].ZPos - KinematicDataCollector.KinematicData[befTimestamp].ZPos) / kinematicElapsed;

                return new KinematicDatum(KinematicDataCollector.KinematicData[aftTimestamp], xVel,yVel,zVel);
            }

            befTimestamp = KinematicDataCollector.Timestamps[ClosestKinematicTimestampIndex];
            aftTimestamp = KinematicDataCollector.Timestamps[ClosestKinematicTimestampIndex + 1];
            kinematicElapsed = aftTimestamp - befTimestamp;
            uint timeDistanceToClosest = timestamp - befTimestamp;

            //approximates data at given time based on closest data
            xVel = (double)(KinematicDataCollector.KinematicData[aftTimestamp].XPos - KinematicDataCollector.KinematicData[befTimestamp].XPos) / kinematicElapsed;
            yVel = (double)(KinematicDataCollector.KinematicData[aftTimestamp].YPos - KinematicDataCollector.KinematicData[befTimestamp].YPos) / kinematicElapsed;
            zVel = (double)(KinematicDataCollector.KinematicData[aftTimestamp].ZPos - KinematicDataCollector.KinematicData[befTimestamp].ZPos) / kinematicElapsed;

            ushort xPos = (ushort)(xVel * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].XPos);
            ushort yPos = (ushort)(yVel * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].YPos);
            ushort zPos = (ushort)(zVel * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].ZPos);
            

            return new KinematicDatum(xPos,yPos, zPos, xVel, yVel, zVel);
        }
    }
}
