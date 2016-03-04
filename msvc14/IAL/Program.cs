using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Minority_Report.Input_Abstraction
{
    class MinorityReportApp
    {
        static void Main(string[] args)
        {
            log.Info("The Input Abstraction Layer's test program is starting up.");
            KinectHandler kinectHandler = new KinectHandler();

            log.Debug("Attempting to retrieve canvas bounds...");
            System.Drawing.Rectangle rect = kinectHandler.CanvasBounds;
            
            for (;;)
            {
                // Do nothing.
            }
        }

        private static readonly log4net.ILog log = log4net.LogManager.GetLogger
   (System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);
    }
}
