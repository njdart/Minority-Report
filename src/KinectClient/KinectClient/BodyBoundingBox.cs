using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;

namespace MinorityReport
{
    /// <summary>
    /// The bounding box of a body tracked by the Kinect sensor. Stores coordinates in double-precision floating point.
    /// </summary>
    public class BodyBoundingBox
    {
        public int bodyIndex;
        public Point topLeft;
        public Point bottomRight;

        public BodyBoundingBox()
        {
            this.topLeft = new Point();
            this.bottomRight = new Point();
        }
    }
}
