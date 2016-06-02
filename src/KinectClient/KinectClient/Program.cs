using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace MinorityReport
{
    static class Program
    {
        static void Main()
        {
            KinectClient client = new KinectClient("srv", 0);
            client.Run();
        }
    }
}
