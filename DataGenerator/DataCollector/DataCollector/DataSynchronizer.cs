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
        public KinematicDatum CurrKinematicDatum;
        public ForceDatum PrevForceDatum;
        public ForceDatum ForceDatumToPredict;

        public NNTrainingDatum(KinematicDatum currKinematicDatum, ForceDatum prevForceDatum, ForceDatum forceDatumToPredict)
        {
            CurrKinematicDatum = currKinematicDatum;
            PrevForceDatum = prevForceDatum;
            ForceDatumToPredict = forceDatumToPredict;
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
                outputWriter.Write($"{datum.CurrKinematicDatum.XPos} {datum.CurrKinematicDatum.YPos} {datum.CurrKinematicDatum.ZPos} {datum.CurrKinematicDatum.XVel} {datum.CurrKinematicDatum.YVel} {datum.CurrKinematicDatum.ZVel} {datum.PrevForceDatum.XForce} {datum.PrevForceDatum.YForce} {datum.PrevForceDatum.ZForce} {datum.ForceDatumToPredict.XForce} {datum.ForceDatumToPredict.YForce} {datum.ForceDatumToPredict.ZForce}\n");
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

                ranOutputWriter.Write($"{datum.CurrKinematicDatum.XPos} {datum.CurrKinematicDatum.YPos} {datum.CurrKinematicDatum.ZPos} {datum.CurrKinematicDatum.XVel} {datum.CurrKinematicDatum.YVel} {datum.CurrKinematicDatum.ZVel} {datum.PrevForceDatum.XForce} {datum.PrevForceDatum.YForce} {datum.PrevForceDatum.ZForce} {datum.ForceDatumToPredict.XForce} {datum.ForceDatumToPredict.YForce} {datum.ForceDatumToPredict.ZForce}\n");

                //ranNormOutputWriter.Write($"");

                TrainingData.RemoveAt(indexToRemove);
            }
        }

        public static void SyncData()
        {
            foreach(var forDatumPair in ForceDataCollector.ForceData)
            {
                var timestampIndex = GetClosestKinematicTimestampIndex(forDatumPair.Key);
                var kinDatum = KinematicDataCollector.InputToKinematic(ApproximateCorrectedKinematicDatum(forDatumPair.Key, timestampIndex));

                var forDatum = ForceDataCollector.InputToForce(forDatumPair.Value);

                var combinedDatum = new CombinedDatum(forDatumPair.Key, forDatum, kinDatum);

                CombinedData.Add(combinedDatum);
            }
        }

        public static void CompileTrainingData()
        {
            for(int i = 1; i < CombinedData.Count; i++) 
            {
                TrainingData.Add(new NNTrainingDatum(CombinedData[i].KinematicDatum, CombinedData[i - 1].ForceDatum, CombinedData[i].ForceDatum));
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

        public static KinematicInputDatum ApproximateCorrectedKinematicDatum(uint timestamp, int ClosestKinematicTimestampIndex)
        {
            if (ClosestKinematicTimestampIndex >= KinematicDataCollector.Timestamps.Count - 1)
            {
                Console.WriteLine("More force than kin");
                return KinematicDataCollector.KinematicData.Values.Last();
            }

            uint befTimestamp = KinematicDataCollector.Timestamps[ClosestKinematicTimestampIndex];
            uint aftTimestamp = KinematicDataCollector.Timestamps[ClosestKinematicTimestampIndex + 1];
            uint kinematicElapsed = aftTimestamp - befTimestamp;
            uint timeDistanceToClosest = timestamp - befTimestamp;

            //approximates data at given time based on closest data
            ushort xPos = (ushort)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].XPos - KinematicDataCollector.KinematicData[befTimestamp].XPos) / kinematicElapsed) * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].XPos);
            ushort yPos = (ushort)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].YPos - KinematicDataCollector.KinematicData[befTimestamp].YPos) / kinematicElapsed) * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].YPos);
            ushort zPos = (ushort)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].ZPos - KinematicDataCollector.KinematicData[befTimestamp].ZPos) / kinematicElapsed) * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].ZPos);
            sbyte xVel = (sbyte)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].XVel - KinematicDataCollector.KinematicData[befTimestamp].XVel) / kinematicElapsed) * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].XVel);
            sbyte yVel = (sbyte)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].YVel - KinematicDataCollector.KinematicData[befTimestamp].YVel) / kinematicElapsed) * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].YVel);
            sbyte zVel = (sbyte)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].ZVel - KinematicDataCollector.KinematicData[befTimestamp].ZVel) / kinematicElapsed) * timeDistanceToClosest + KinematicDataCollector.KinematicData[befTimestamp].ZVel);

            return new KinematicInputDatum(xPos,yPos, zPos, xVel, yVel, zVel);
        }
    }
}
