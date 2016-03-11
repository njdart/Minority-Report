using System;
using System.Drawing;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Emgu.CV;

namespace Minority_Report
{
    public static class ImageProcessor
    {
        public static List<PostIt> extractPostIts(bool showDebug = false, double sigma = 0.8, int minPostitArea = 3000,
            int maxPostItArea = 20000, double lenTolerance = 0.15, int minColourThresh = 64, int maxColourThresh = 200)
        {
            List<PostIt> foundPostits = new List<PostIt>();

            return foundPostits;
        }

        public static Rectangle findCanvas()
        {
            return new Rectangle();
        }
    }
}
