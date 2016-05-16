using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    /// <summary>
    /// Argument type for BoundingBoxesSampled event handler.
    /// </summary>
    public class BoundingBoxesSampledEventArgs: EventArgs
    {
        public IList<BodyBoundingBox> BoundingBoxes { get; }

        public BoundingBoxesSampledEventArgs(IList<BodyBoundingBox> boundingBoxes)
        {
            this.BoundingBoxes = boundingBoxes;
        }
    }
}
