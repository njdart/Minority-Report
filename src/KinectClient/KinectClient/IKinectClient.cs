using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    public interface IKinectClient
    {
        string Server { get; set; }
        int Port { get; set; }

        void BeginSampling();
        void StopSampling();

        event EventHandler ServerDisconnected;
    }
}
