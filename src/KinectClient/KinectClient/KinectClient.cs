using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Kinect;
using System.Timers;
using Newtonsoft.Json;
using System.IO;
using System.Windows;

namespace MinorityReport
{
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

    public class BoundingBoxesEventArgs: EventArgs
    {
        public IList<BodyBoundingBox> BoundingBoxes { get; set; }

        public BoundingBoxesEventArgs(IList<BodyBoundingBox> boundingBoxes)
        {
            this.BoundingBoxes = boundingBoxes;
        }
    }

    public class KinectClient : IKinectClient
    {
        private KinectSensor sensor = null;
        private BodyIndexFrameReader bodyIndexReader = null;

        public string Server { get; set; }
            = "localhost";

        public int Port { get; set; }
            = 8088;

        public event EventHandler ServerDisconnected;
        public event EventHandler<BoundingBoxesEventArgs> BoundingBoxesSampled;

        public KinectClient(string server, int port)
        {
            this.sensor = KinectSensor.GetDefault();
            this.sensor.Open();

            this.bodyIndexReader = this.sensor.BodyIndexFrameSource.OpenReader();
        }

        public void BeginSampling()
        {
            this.bodyIndexReader.FrameArrived += this.BodyIndexReader_FrameArrived;
        }

        public void StopSampling()
        {
            this.bodyIndexReader.FrameArrived -= this.BodyIndexReader_FrameArrived;
        }

        private void BodyIndexReader_FrameArrived(object sender, BodyIndexFrameArrivedEventArgs e)
        {
            using (BodyIndexFrame frame = e.FrameReference.AcquireFrame())
            {
                if (frame == null)
                {
                    Console.Write("Null frame acquired.\n");
                    return;
                }

                Console.Write("acquired\n");

                // Initialize our bounding boxes as null.
                IList<BodyBoundingBox> boundingBoxes = new BodyBoundingBox[this.sensor.BodyFrameSource.BodyCount];
                for (int i = 0; i < boundingBoxes.Count; ++i)
                {
                    boundingBoxes[i] = null;
                }

                // Copy frame into accessible buffer
                byte[] frameBuf = new byte[frame.FrameDescription.Width * frame.FrameDescription.Height];
                frame.CopyFrameDataToArray(frameBuf);

                // Iterate over every pixel, top to bottom, left to right
                for (int y = 0; y < frame.FrameDescription.Height; ++y)
                {
                    for (int x = 0; x < frame.FrameDescription.Width; ++x)
                    {
                        // Get the value at the pixel
                        int bufIdx = y * frame.FrameDescription.Width + x;
                        int bodyIdx = frameBuf[bufIdx];
                        if (bodyIdx >= 0 && bodyIdx < boundingBoxes.Count)
                        {
                            // The pixel is part of a body, so record
                            if (boundingBoxes[bodyIdx] == null)
                            {
                                // Create a new bounding box since this is the first time we have seen the body
                                boundingBoxes[bodyIdx] = new BodyBoundingBox();
                                boundingBoxes[bodyIdx].bodyIndex = bodyIdx;

                                // Set up initial coordinates.
                                //
                                // Note: topLeft.y is guaranteed to be this coordinate because we are scanning from
                                // top to bottom, so we never try to update it later.
                                //
                                // Note: the maximum values are set to absolute minimum so that they are later
                                // guaranteed to be updated.
                                boundingBoxes[bodyIdx].topLeft = new Point(x, y);
                                boundingBoxes[bodyIdx].bottomRight = new Point(x + 1, y + 1);
                            }
                            else
                            {
                                // Update the minimum x-coordinate if it is a minimum.
                                boundingBoxes[bodyIdx].topLeft.X = Math.Min(boundingBoxes[bodyIdx].topLeft.X, x);

                                // Update the maximum x-coordinate if it is a maximum.
                                boundingBoxes[bodyIdx].bottomRight.X = Math.Max(boundingBoxes[bodyIdx].bottomRight.X, x);

                                // The y-coordinate is guaranteed to be a maximum since we are scanning top to bottom.
                                boundingBoxes[bodyIdx].bottomRight.Y = y;
                            }
                        }
                    }
                }

                string boundingBoxesJson = this.SerializeBoundingBoxes(boundingBoxes);

                if (this.BoundingBoxesSampled != null)
                {
                    this.BoundingBoxesSampled.Invoke(this, new BoundingBoxesEventArgs(boundingBoxes));
                }
            }
        }

        private string SerializeBoundingBoxes(IList<BodyBoundingBox> boundingBoxes)
        {
            // Setup serialization into a string
            TextWriter stringWriter = new StringWriter();
            JsonWriter jsonWriter = new JsonTextWriter(stringWriter);
            JsonSerializer jsonSerializer = JsonSerializer.Create();

            // Make it neat
            jsonWriter.Formatting = Formatting.Indented;
            jsonSerializer.Formatting = Formatting.Indented;

            jsonWriter.WritePropertyName("bodies");
            jsonWriter.WriteStartArray();

            // Ignore null entries.
            foreach (BodyBoundingBox boundingBox in boundingBoxes.Where(x => x != null))
            {
                // Conveniently, BodyBoundingBox fits the spec when serialized...
                jsonSerializer.Serialize(jsonWriter, boundingBox);
            }

            jsonWriter.WriteEndArray();

            if (boundingBoxes.Where(x => x != null).Count() > 1)
            {
                Console.Write(stringWriter.ToString() + "\n\n");
            }

            return stringWriter.ToString();
        }
    }
}