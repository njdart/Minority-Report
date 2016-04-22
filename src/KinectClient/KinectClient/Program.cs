using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    class MinorityReportApp
    {
        private static readonly log4net.ILog log = log4net.LogManager.GetLogger
   (System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Entry point.
        /// </summary>
        /// <param name="args"></param>
        static void Main(string[] args)
        {
            KinectClient client = new KinectClient(args);
            ShuttingDownReason exitReason = client.Run();
            log.InfoFormat("KinectClient shutdown reason: {0}", exitReason);
            ExitApp();
        }

        /// <summary>
        /// Exit the app with a success error code.
        /// </summary>
        private static void ExitApp()
        {
            log.Info("Exiting...");
            Environment.Exit(0);
        }
    }
}
