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
        uint Timestamp;
        ForceDatum ForceDatum;
        KinematicDatum KinematicDatum;

        public CombinedDatum(uint timestamp, ForceDatum forcedDatum, KinematicDatum kinematicDatum)
        {
            Timestamp = timestamp;
            ForceDatum = forcedDatum;
            KinematicDatum = kinematicDatum;
        }
    }

    public static class DataSynchronizer
    {
        private static int PreviousKinematicTimestampIndex;

        public static List<CombinedDatum> CombinedData = new List<CombinedDatum>();

        static DataSynchronizer()
        {
            PreviousKinematicTimestampIndex = 0;
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

            return new KinematicDatum(xPos,yPos, zPos, xVel, yVel, zVel);
        }
    }
}
