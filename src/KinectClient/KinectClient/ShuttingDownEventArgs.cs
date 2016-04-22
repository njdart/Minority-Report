using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    public enum ShuttingDownReason
    {
        KinectUnavailable,
        UserAbort
    }

    public class ShuttingDownEventArgs : EventArgs
    {
        public ShuttingDownEventArgs(ShuttingDownReason reason)
        {
            m_reason = reason;
        }

        public ShuttingDownReason Reason { get { return m_reason; } }

        private ShuttingDownReason m_reason;
    }
}
