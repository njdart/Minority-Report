using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Emgu.CV;
using Emgu.CV.CvEnum;

namespace Minority_Report
{
    public class GraphExtractorTest
    {
        public static void Execute()
        {
            GraphExtractor ge = new GraphExtractor(CvInvoke.Imread("postits1.jpg", LoadImageType.Color));
            ge.ExtractGraph();
        }
    }
}
