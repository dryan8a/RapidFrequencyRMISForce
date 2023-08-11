using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DataCollector
{
    public static class DataSynchronizer
    {
        private static int PreviousKinematicTimestampIndex;

        static DataSynchronizer()
        {
            PreviousKinematicTimestampIndex = 0;
        }

        public static int GetClosestKinematicTimestampIndex(uint timestamp)
        {
            for(int i = PreviousKinematicTimestampIndex;; i++)
            {
                if(i == KinematicDataCollector.Timestamps.Count - 1)
                {
                    return i;
                }

                if (timestamp - KinematicDataCollector.Timestamps[i] >= 0 && timestamp - KinematicDataCollector.Timestamps[i+1] <= 0)
                {
                    PreviousKinematicTimestampIndex = i;
                    return i;
                }
            }
        }

        public static KinematicDatum ApproximateCorrectedKinematicDatum(uint timestamp, int ClosestKinematicTimestampIndex)
        {
            uint befTimestamp = KinematicDataCollector.Timestamps[ClosestKinematicTimestampIndex];
            uint aftTimestamp = KinematicDataCollector.Timestamps[ClosestKinematicTimestampIndex + 1];

            ushort xPos = (ushort)(((double)(KinematicDataCollector.KinematicData[aftTimestamp].XPos - KinematicDataCollector.KinematicData[befTimestamp].XPos) / (aftTimestamp - befTimestamp)) * (timestamp - befTimestamp) + KinematicDataCollector.KinematicData[befTimestamp].XPos);

            throw new NotImplementedException();
        }
    }
}
