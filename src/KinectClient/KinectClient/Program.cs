using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    static class Program
    {
        static void Main()
        {
            IKinectClient client = new KinectClient("srv", 0);
            client.BeginSampling();
            while (true);
        }
    }
}
