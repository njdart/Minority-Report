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
            try
            {
                KinectClient client = new KinectClient("srv", 0);
                client.Run();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "KinectClient");
                Environment.Exit(1);
            }
        }
    }
}
