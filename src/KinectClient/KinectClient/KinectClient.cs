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
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Net;
using MathNet.Numerics.LinearAlgebra;

using Draw = System.Drawing;

namespace MinorityReport
{
    public class KinectClient
    {
        private KinectSensor sensor = null;
        private BodyIndexFrameReader bodyIndexReader = null;
        private ColorFrameReader colorReader = null;

        private bool samplingColorFrames = false;
        private bool samplingBodyData = false;

        private byte[] latestColorPNG = null;
        private Draw.PointF latestPNGDimensions;

        private string instanceID;

        private Draw.PointF[] canvasCoords;

        private Timer sensorAvailableTimer;
        private bool sensorTimerElapsed = false;

        public string Server { get; set; } = "localhost";

        public int Port { get; set; } = 8088;

        // public event EventHandler ServerDisconnected;
        // public event EventHandler<BoundingBoxesSampledEventArgs> BoundingBoxesSampled;
        // public event EventHandler<ColorFrameSampledEventArgs> ColorFrameSampled;

        public KinectClient(string server, int port)
        {
            // If this timer elapses, an exception is thrown in Run().
            this.sensorAvailableTimer = new Timer(5000);
            this.sensorAvailableTimer.Elapsed += SensorAvailableTimer_Elapsed;
            this.sensorAvailableTimer.Start();

            this.sensor = KinectSensor.GetDefault();
            this.sensor.IsAvailableChanged += Sensor_IsAvailableChanged;
            this.sensor.Open();

            this.bodyIndexReader = this.sensor.BodyIndexFrameSource.OpenReader();
            this.colorReader = this.sensor.ColorFrameSource.OpenReader();
            this.bodyIndexReader.FrameArrived += this.BodyIndexReader_FrameArrived;
            this.colorReader.FrameArrived += this.ColorReader_FrameArrived;
            this.samplingBodyData = true;
        }
        public void Run()
        {
            bool active = true;
            bool kinectFault = false;
            // Set a background loop to continually check on the status of the Kinect sensor.
            Task sensorTimerTask = new Task(() =>
            {
                while (active)
                {
                    if (this.sensorTimerElapsed)
                    {
                        kinectFault = true;
                        break;
                    }
                }
            });
            sensorTimerTask.Start();

            // Listen to all HTTP requests on port 8080. This requires admin privileges.
            HttpListener listener = new HttpListener();
            HttpListenerPrefixCollection prefixes = listener.Prefixes;
            prefixes.Add("http://+:8080/");
            listener.IgnoreWriteExceptions = true;
            listener.Start();

            Task listenerTask = new Task(() =>
            {
                while (active && !kinectFault)
                {
                    HttpListenerContext context;
                    try
                    {
                        context = listener.GetContext();
                    }
                    catch
                    {
                        // This probably means an exception has been thrown in the calling thread, invalidating the
                        // listener object.
                        active = false;
                        break;
                    }

                    if (context.Request.Url.LocalPath == "/debug")
                    {
                        string body = "debug or something";
                        this.WriteStringResponse(context, body);
                    }
                    else if (context.Request.Url.LocalPath == "/calibrate")
                    {
                        if (context.Request.HttpMethod == "GET")
                        {
                            // save a colour image
                            this.latestColorPNG = null;
                            this.samplingColorFrames = true;
                            while (this.samplingColorFrames) ;

                            // respond with the colour image (PNG)
                            try
                            {
                                context.Response.ContentLength64 = this.latestColorPNG.Length;
                                context.Response.ContentType = "image/png";
                                context.Response.OutputStream.Write(this.latestColorPNG, 0, this.latestColorPNG.Length);
                            }
                            catch (HttpListenerException)
                            {
                                // Do nothing (the client closed the connection)
                            }

                            Console.Write("Sent calibration image to {0}\n", context.Request.RemoteEndPoint.Address);
                        }
                        else if (context.Request.HttpMethod == "POST")
                        {
                            // Get the sent data
                            Console.Write("Received calibration data from {0}\n", context.Request.RemoteEndPoint.Address);
                            MemoryStream mstream = new MemoryStream();
                            context.Request.InputStream.CopyTo(mstream);
                            byte[] data = mstream.GetBuffer();

                            // deserialize the sent data
                            CalibratePOSTData postData = null;
                            bool success = true;
                            try
                            {
                                string content = Encoding.UTF8.GetString(data, 0, (int)context.Request.ContentLength64);
                                Console.Write("\n{0}\n", content);
                                postData = JsonConvert.DeserializeObject<CalibratePOSTData>(content);
                                if (postData.points == null || postData.points.Count != 4)
                                {
                                    Console.Write("Invalid data.\n");
                                    success = false;
                                }
                                else
                                {
                                    // Store the sent coordinates
                                    this.canvasCoords = new Draw.PointF[4];
                                    int i = 0;
                                    Console.Write("Coordinates got:\n");
                                    foreach (IList<float> p in postData.points)
                                    {
                                        this.canvasCoords[i] = new Draw.PointF(p[0], p[1]);
                                        Console.Write("[{0}, {1}]\n", this.canvasCoords[i].X, this.canvasCoords[i].Y);
                                        i += 1;
                                    }

                                    // Calculate perspective matrix
                                    this.canvasCoords = ImageWarping.OrderPoints(this.canvasCoords);
                                }
                            }
                            catch (JsonException e)
                            {
                                Console.Write("Invalid JSON. Exception: {0}\n", e.Message);
                                success = false;
                            }

                            if (!success)
                            {
                                // Handle errors
                                context.Response.StatusCode = (int)HttpStatusCode.BadRequest;
                                string body = "Malformed JSON received";
                                this.WriteStringResponse(context, body);
                            }
                            else
                            {
                                // Success!

                                if (postData.instanceID != null)
                                {
                                    // Store the sent ID
                                    this.instanceID = postData.instanceID;

                                    // echo ID
                                    CalibratePOSTData respData = new CalibratePOSTData();
                                    respData.instanceID = postData.instanceID;
                                    string body = JsonConvert.SerializeObject(respData, Formatting.Indented);
                                    this.WriteStringResponse(context, body);
                                    Console.Write(body + "\n");
                                }
                                else
                                {
                                    // No ID sent to us; send empty object back
                                    this.WriteStringResponse(context, "{ }");
                                }

                                // Store the sent coordinates
                                this.canvasCoords = new Draw.PointF[4];
                                int i = 0;
                                Console.Write("Coordinates got:\n");
                                foreach (IList<float> p in postData.points)
                                {
                                    this.canvasCoords[i] = new Draw.PointF(p[0], p[1]);
                                    Console.Write("[{0}, {1}]\n", this.canvasCoords[i].X, this.canvasCoords[i].Y);
                                    i += 1;
                                }

                                // Calculate perspective matrix
                                this.canvasCoords = ImageWarping.OrderPoints(this.canvasCoords);
                                Draw.PointF[] imageCorners = new Draw.PointF[4] {
                                    new Draw.PointF(0, 0),
                                    new Draw.PointF(0, this.latestPNGDimensions.Y),
                                    new Draw.PointF(this.latestPNGDimensions.X, 0),
                                    new Draw.PointF(this.latestPNGDimensions.X, this.latestPNGDimensions.Y)
                                };
                                imageCorners = ImageWarping.OrderPoints(imageCorners);
                                Matrix<float> perspectiveMatrix = ImageWarping.GetPerspectiveTransform(imageCorners, this.canvasCoords);
                            }
                        }
                    }
                    else if (context.Request.Url.LocalPath == "/quit")
                    {
                        string body = "Goodbye";
                        this.WriteStringResponse(context, body);
                        active = false;
                    }
                    else
                    {
                        context.Response.StatusCode = (int)HttpStatusCode.NotFound;
                        string body = "<html><head><title>KinectClient: 404</title></head><body><h1>404 : Not Found</h1><p>You messed up lol</p></body></html>";
                        this.WriteStringResponse(context, body);
                    }
                    context.Response.Close();
                }
            });
            listenerTask.Start();

            try
            {
                while (active)
                {
                    if (kinectFault)
                    {
                        active = false;
                        throw new Exception("The Kinect sensor is unavailable.");
                    }
                }
            }
            finally
            {
                listener.Stop();
            }
        }

        private void SensorAvailableTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            // If this timer has elapsed, the Kinect sensor has been unavailable for too long...
            Console.Write("Kinect has been unavailable for {0} seconds.", ((Timer)sender).Interval / 1000);
            this.sensorTimerElapsed = true;
        }

        private void Sensor_IsAvailableChanged(object sender, IsAvailableChangedEventArgs e)
        {
            // If the sensor becomes unavailable, a timer is started. If the sensor becomes available before the timer
            // elapses, everything is fine. Otherwise, we regard this as an error, treating the Kinect as permanently
            // unavailable.
            if (e.IsAvailable)
            {
                this.sensorAvailableTimer.Stop();
            }
            else
            {
                this.sensorAvailableTimer.Start();
            }
        }

        private bool WriteStringResponse(HttpListenerContext context, string str)
        {
            byte[] data = Encoding.UTF8.GetBytes(str);
            bool retval;
            try
            {
                context.Response.ContentLength64 = data.Length;
                context.Response.OutputStream.Write(data, 0, data.Length);
            }
            catch (HttpListenerException)
            {
                retval = false;
            }
            retval = true;
            return retval;
        }

        private void BodyIndexReader_FrameArrived(object sender, BodyIndexFrameArrivedEventArgs e)
        {
            // Do this logic in a separate thread (the logic is quite intensive)
            using (BodyIndexFrame frame = e.FrameReference.AcquireFrame())
            {
                if (frame == null)
                {
                    Console.Write("Null body index frame acquired.\n");
                    return;
                }

                // Console.Write(DateTime.Now.ToString("o") + "\tbody index frame\n");

                if (this.samplingBodyData)
                {
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
                                    boundingBoxes[bodyIdx].topLeft = new System.Windows.Point(x, y);
                                    boundingBoxes[bodyIdx].bottomRight = new System.Windows.Point(x + 1, y + 1);
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
                    this.SendBoundingBoxes(boundingBoxesJson);
                }
            }
        }

        private void SendBoundingBoxes(string data)
        {
            return;
        }

        private void ColorReader_FrameArrived(object sender, ColorFrameArrivedEventArgs e)
        {
            using (ColorFrame frame = e.FrameReference.AcquireFrame())
            {
                if (frame == null)
                {
                    Console.Write("Null color frame acquired.\n");
                    return;
                }

                // Console.Write("color frame\n");

                if (this.samplingColorFrames)
                {
                    // Get pixel data
                    byte[] pixels = new byte[frame.FrameDescription.Width * frame.FrameDescription.Height * 4];
                    frame.CopyConvertedFrameDataToArray(pixels, ColorImageFormat.Bgra);

                    // Store dimensions
                    this.latestPNGDimensions = new Draw.PointF(frame.FrameDescription.Width,
                                                               frame.FrameDescription.Height);

                    // Create a bitmap structure to hold data
                    WriteableBitmap bmp = new WriteableBitmap(frame.FrameDescription.Width,
                                                                   frame.FrameDescription.Height,
                                                                   96.0, 96.0,
                                                                   PixelFormats.Bgr32,
                                                                   null);

                    // Write data into a bitmap structure
                    using (KinectBuffer buf = frame.LockRawImageBuffer())
                    {
                        bmp.Lock();
                        frame.CopyConvertedFrameDataToIntPtr(bmp.BackBuffer,
                                                             (uint)frame.FrameDescription.LengthInPixels * 4,
                                                             ColorImageFormat.Bgra);
                        bmp.AddDirtyRect(new Int32Rect(0, 0, bmp.PixelHeight, bmp.PixelHeight));
                        bmp.Unlock();
                    }

                    // Encode the data into a BMP file format
                    PngBitmapEncoder encoder = new PngBitmapEncoder();
                    encoder.Frames.Add(BitmapFrame.Create(bmp));

                    using (MemoryStream stream = new MemoryStream())
                    {
                        encoder.Save(stream);
                        this.latestColorPNG = stream.ToArray();
                    }
                    this.samplingColorFrames = false;
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