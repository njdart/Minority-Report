using System;
using MinorityReport;

namespace KinectHandlerApp
{
    class Program
    {
        static KinectClient client;

        static void Main()
        {
            Console.CancelKeyPress += Console_CancelKeyPress;
            client = new KinectClient("srv", 0);
            client.Run();
        }

        private static void Console_CancelKeyPress(object sender, ConsoleCancelEventArgs e)
        {
            client.Quit();
            while (client.Running) ;
        }
    }
}
