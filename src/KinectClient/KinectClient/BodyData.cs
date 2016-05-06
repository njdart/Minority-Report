using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace MinorityReport
{
    class BodyDataSerializer
    {
        struct InternalPointF
        {
            public float x;
            public float y;
        }

        struct InternalGesture
        {
            public string type;
            public InternalPointF origin;
        }

        struct InternalBoundingBox
        {
            public int bodyIndex;
            public InternalPointF topLeft;
            public InternalPointF bottomRight;
        }

        struct InternalBodyData
        {
            public string timestamp;
            public IList<InternalBoundingBox> bodies;
            public IList<InternalGesture> gestures;
        }

        public static string Serialize(IList<BoundingBox> boxes)
        {
            InternalBodyData data = new InternalBodyData();

            // ISO 8601 compliant timestamp
            data.timestamp = DateTime.UtcNow.ToString("o");

            data.gestures = null;
            data.bodies = new List<InternalBoundingBox>();

            foreach (BoundingBox box in boxes)
            {
                InternalBoundingBox b = new InternalBoundingBox();
                b.topLeft.x = box.TopLeft.X;
                b.topLeft.y = box.TopLeft.Y;
                b.bottomRight.x = box.BottomRight.X;
                b.bottomRight.y = box.BottomRight.Y;

                data.bodies.Add(b);
            }
            return JsonConvert.SerializeObject(data);
        }
    }
}
