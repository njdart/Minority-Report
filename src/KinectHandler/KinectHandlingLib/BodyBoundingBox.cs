using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Drawing;

namespace MinorityReport
{
    /// <summary>
    /// The bounding box of a body tracked by the Kinect sensor. Stores coordinates in double-precision floating point.
    /// </summary>
    public class BodyBoundingBox
    {
        public int bodyIndex;
        public PointF topLeft;
        public PointF bottomRight;

        public BodyBoundingBox()
        {
            this.topLeft = new PointF();
            this.bottomRight = new PointF();
        }
    }
}
