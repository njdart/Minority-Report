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
using System.Net.Http;

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

        private Matrix<float> perspectiveMatrix = null;

        private string instanceID;

        private Draw.PointF[] canvasCoords;
        private bool boardObscured = false;

        private Timer sensorAvailableTimer;
        private bool sensorTimerElapsed = false;

        private Timer boardNonObscuredTimer;

        public string Server { get; set; } = null;

        public int Port { get; set; } = 8088;

        // public event EventHandler ServerDisconnected;
        // public event EventHandler<BoundingBoxesSampledEventArgs> BoundingBoxesSampled;
        // public event EventHandler<ColorFrameSampledEventArgs> ColorFrameSampled;
        public event EventHandler<bool> BoardObscuredChanged;

        public KinectClient(string server, int port)
        {
            // If this timer elapses, an exception is thrown in Run().
            this.sensorAvailableTimer = new Timer(5000);
            this.sensorAvailableTimer.Elapsed += this.SensorAvailableTimer_Elapsed;
            this.sensorAvailableTimer.Start();

            // If this timer elapses, the server is signalled that the board is non-obscured.
            this.boardNonObscuredTimer = new Timer(500);
            this.boardNonObscuredTimer.Elapsed += this.BoardNonObscuredTimer_Elapsed;

            this.sensor = KinectSensor.GetDefault();
            this.sensor.IsAvailableChanged += Sensor_IsAvailableChanged;
            this.sensor.Open();

            this.bodyIndexReader = this.sensor.BodyIndexFrameSource.OpenReader();
            this.colorReader = this.sensor.ColorFrameSource.OpenReader();
            this.bodyIndexReader.FrameArrived += this.BodyIndexReader_FrameArrived;
            this.colorReader.FrameArrived += this.ColorReader_FrameArrived;
            this.samplingBodyData = true;

            this.BoardObscuredChanged += this.KinectClient_BoardObscuredChanged;
        }

        private void BoardNonObscuredTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            throw new NotImplementedException();
        }

        private void KinectClient_BoardObscuredChanged(object sender, bool obscured)
        {
            Console.Write("Board " + ((!obscured) ? "no longer " : "") + "obscured!\n");

            //tell server
            HttpClient client = new HttpClient();

            string payload = String.Format("{{ \"boardObscured\" : {0}, \"kinectID\" : \"{1}\" }}", obscured ? "true" : "false", this.instanceID);
            StringContent content = new StringContent(payload);

            if (content.Headers.Contains("Content-Type")) content.Headers.Remove("Content-Type");
            content.Headers.Add("Content-Type", "application/json");

            string uri = String.Format("http://{0}:{1}/boardObscured", this.Server, this.Port);

            Console.Write("Sending to {1} :\n{0}\n", payload, uri);
            Task<HttpResponseMessage> req;
            try
            {
                req = client.PostAsync(uri, content);
                req.Wait();
            }
            catch (AggregateException e)
            {
                Console.Write("Error occurred sending data to the server:\n");
                Console.Write(e.ToString());
                return;
            }

            Task<byte[]> dataTask = req.Result.Content.ReadAsByteArrayAsync();
            dataTask.Wait();
            string data = Encoding.UTF8.GetString(dataTask.Result);
            Console.Write("Response (status {1}): {0}.\n", data, req.Result.StatusCode);
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

            // Listen to all HTTP requests on port 8081. This requires the URI http://+:8081 to be reserved for the
            // current user.
            HttpListener listener = new HttpListener();
            HttpListenerPrefixCollection prefixes = listener.Prefixes;
            prefixes.Add("http://+:8081/");
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

                            // save image to file for debug purposes
                            string pngname = String.Format("{0}.png", DateTime.Now.ToString("o")).Replace(":", ".");
                            FileStream debugPNG = new FileStream(pngname, FileMode.CreateNew);
                            debugPNG.Write(this.latestColorPNG, 0, this.latestColorPNG.Length);
                            debugPNG.Close();

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
                                string body = "Bad request innit haha";
                                this.WriteStringResponse(context, body);
                            }
                            else
                            {
                                // Success!

                                if (postData.instanceID != null)
                                {
                                    // Store the sent ID
                                    this.instanceID = postData.instanceID;

                                    // Store the server details (assume port 8088).
                                    this.Server = context.Request.RemoteEndPoint.Address.ToString();
                                    this.Port = 8088;
                                    if (this.Server == "::1")
                                    {
                                        // lel hack lel
                                        this.Server = "127.0.0.1";
                                    }
                                    Console.Write("Data POSTed from {0}.\n", this.Server);

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
                                Console.Write("Coordinates got:\n");
                                for (int i = 0; i < postData.points.Count; ++i)
                                {
                                    IList<float> p = postData.points[i];
                                    this.canvasCoords[i] = new Draw.PointF(p[0], p[1]);
                                    Console.Write("[{0}, {1}]\n", this.canvasCoords[i].X, this.canvasCoords[i].Y);
                                }

                                // Calculate perspective matrix
                                this.canvasCoords = ImageWarping.OrderPoints(this.canvasCoords);
                                Draw.PointF[] imageCorners = new Draw.PointF[4] {
                                    new Draw.PointF(0, 0),
                                    new Draw.PointF(0, this.latestPNGDimensions.Y - 1),
                                    new Draw.PointF(this.latestPNGDimensions.X - 1, 0),
                                    new Draw.PointF(this.latestPNGDimensions.X - 1, this.latestPNGDimensions.Y - 1)
                                };
                                imageCorners = ImageWarping.OrderPoints(imageCorners);
                                this.perspectiveMatrix = ImageWarping.GetPerspectiveTransform(this.canvasCoords, imageCorners);

                                // Console.Write("Matrix generated:\n");
                                // for (int i = 0; i < 3; ++i)
                                // {
                                //     for (int j = 0; j < 3; ++j)
                                //     {
                                //         Console.Write("{0} ", perspectiveMatrix[i, j]);
                                //     }
                                //     Console.Write("\n");
                                // }

                                // Console.Write("Transforming canvas coords.\n");
                                // foreach (Draw.PointF coord in this.canvasCoords)
                                // {
                                //     Vector<float> vec = CreateVector.Dense<float>(3);
                                //     vec[0] = coord.X;
                                //     vec[1] = coord.Y;
                                //     vec[2] = 1;
                                //     Vector<float> output = perspectiveMatrix.Multiply(vec);
                                //     foreach (float thing in vec)
                                //     {
                                //         Console.Write("{0}, ", thing);
                                //     }
                                //     Console.Write("\n");
                                //     foreach (float thing in output)
                                //     {
                                //         Console.Write("{0}, ", thing);
                                //     }
                                //     Console.Write("\n");
                                // }
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

        private Vector<float> TransformToCanvasSpace(Vector<float> vec)
        {
            if (this.perspectiveMatrix != null)
            {
                Vector<float> output = this.perspectiveMatrix.Multiply(vec);
                // Divide by third, homogeneous, coordinate
                output.Divide(output[2]);
                return output;
            }
            else
            {
                return null;
            }
        }

        private bool IsVectorObstructingCanvas(Vector<float> transformedVec)
        {
            // this function expects transformedVec to have 3 components; the 2D components have already been divided
            // through by the 3rd ("homogeneous") component.

            // this is ridiculously simple and i'm just lazy
            if (transformedVec[0] > 0 && transformedVec[0] < 1920 &&
                transformedVec[1] > 0 && transformedVec[1] < 1080)
            {
                return true;
            }
            else
            {
                return false;
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

                if (this.samplingBodyData && this.perspectiveMatrix != null)
                {
                    // Copy frame into accessible buffer
                    byte[] frameBuf = new byte[frame.FrameDescription.Width * frame.FrameDescription.Height];
                    frame.CopyFrameDataToArray(frameBuf);

                    bool obscured = false;

                    string kekname = string.Format("KEK-{0}.txt", DateTime.Now.ToString("hh-mm-ss-ffffff"));
                    FileStream debugOut = new FileStream(kekname, FileMode.CreateNew);

                    string matrix = "";
                    for (int j = 0; j < 3; ++j)
                    {
                        for (int i = 0; i < 3; ++i)
                        {
                            matrix += string.Format("{0}, ", this.perspectiveMatrix[i, j]);
                        }
                        matrix += "\n\n";
                    }
                    debugOut.Write(Encoding.UTF8.GetBytes(matrix), 0, matrix.Length);

                    // Iterate over every pixel, top to bottom, left to right
                    for (int y = 0; y < frame.FrameDescription.Height && !obscured; ++y)
                    {
                        for (int x = 0; x < frame.FrameDescription.Width && !obscured; ++x)
                        {
                            // Get the value at the pixel
                            int bufIdx = y * frame.FrameDescription.Width + x;
                            int bodyIdx = frameBuf[bufIdx];
                            if (bodyIdx <= 5 && bodyIdx >= 0)
                            {
                                // is this within the canvas?
                                // float ratioX = 686 / 512;
                                // float ratioY = 567 / 424;
                                float ratioX = 2.86f;
                                float ratioY = 2.86f;
                                float offsetX = 253;
                                float offsetY = -35;

                                float xf = x * ratioX + offsetX;
                                float yf = y * ratioY + offsetY;
                                Vector<float> v = CreateVector.Dense<float>(3);
                                v[0] = xf;
                                v[1] = yf;
                                v[2] = 1;

                                Vector<float> vout = this.TransformToCanvasSpace(v);

                                string line = string.Format("({0}, {1}) -> ({2}, {3})\n",
                                    x, y,
                                    vout[0], vout[1]);
                                debugOut.Write(Encoding.UTF8.GetBytes(line), 0, line.Length);

                                if (this.IsVectorObstructingCanvas(vout))
                                {
                                    debugOut.Write(Encoding.UTF8.GetBytes("Obscured.\n"), 0, "Obscured.\n".Length);
                                    obscured = true;
                                    break;
                                }
                            }
                        }
                    }

                    debugOut.Close();
                    if (obscured != this.boardObscured)
                    {
                        if (this.BoardObscuredChanged != null) this.BoardObscuredChanged.Invoke(this, obscured);
                    }
                    this.boardObscured = obscured;

                    // if (this.perspectiveMatrix != null)
                    // {
                    //     bool obscured = false;
                    //     foreach (BodyBoundingBox bounds in boundingBoxes)
                    //     {
                    //         if (bounds != null)
                    //         {
                    //             // Console.Write("transforming coords\n");

                    //             Vector<float> tl, tr, bl, br;
                    //             tl = this.PointFToVector(bounds.topLeft);
                    //             br = this.PointFToVector(bounds.bottomRight);

                    //             float ratioX = 686 / 512;
                    //             float ratioY = 567 / 424;
                    //             float offsetX = 137;
                    //             float offsetY = -19;

                    //             tl[0] *= ratioX;
                    //             br[0] *= ratioX;

                    //             tl[1] *= ratioY;
                    //             br[1] *= ratioY;

                    //             tl[0] += offsetX;
                    //             br[0] += offsetX;

                    //             tl[1] += offsetY;
                    //             br[1] += offsetY;

                    //             tl = this.TransformToCanvasSpace(tl);
                    //             br = this.TransformToCanvasSpace(br);

                    //             tr = CreateVector.Dense<float>(3);
                    //             tr[0] = br[0];
                    //             tr[1] = tl[1];
                    //             tr[2] = 1;

                    //             bl = CreateVector.Dense<float>(3);
                    //             bl[0] = tl[0];
                    //             bl[1] = br[1];
                    //             tr[2] = 1;

                    //             Console.Write("{0}, {1}\n", tl[0], tl[1]);

                    //             if (this.IsVectorObstructingCanvas(tl) ||
                    //                 this.IsVectorObstructingCanvas(tr) ||
                    //                 this.IsVectorObstructingCanvas(bl) ||
                    //                 this.IsVectorObstructingCanvas(br))
                    //             {
                    //                 obscured = true;
                    //                 break;
                    //             }
                    //         }
                    //     }

                    //     string boundingBoxesJson = this.SerializeBoundingBoxes(boundingBoxes, obscured);
                    //     this.SendBoundingBoxes(boundingBoxesJson);
                    // }
                }
            }
        }

        private Vector<float> PointFToVector(Draw.PointF point)
        {
            Vector<float> v = CreateVector.Dense<float>(3);
            v[0] = point.X;
            v[1] = point.Y;
            v[2] = 1;
            return v;
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

        private string SerializeBoundingBoxes(IList<BodyBoundingBox> boundingBoxes, bool obscuredCanvas)
        {
            // Setup serialization into a string
            TextWriter stringWriter = new StringWriter();
            JsonWriter jsonWriter = new JsonTextWriter(stringWriter);
            JsonSerializer jsonSerializer = JsonSerializer.Create();

            // Make it neat
            jsonWriter.Formatting = Formatting.Indented;
            jsonSerializer.Formatting = Formatting.Indented;

            jsonWriter.WriteStartObject();

            jsonWriter.WritePropertyName("canvasObscured");
            jsonWriter.WriteValue(obscuredCanvas);

            jsonWriter.WritePropertyName("bodies");
            jsonWriter.WriteStartArray();

            // Ignore null entries.
            foreach (BodyBoundingBox boundingBox in boundingBoxes.Where(x => x != null))
            {
                // Conveniently, BodyBoundingBox fits the spec when serialized...
                jsonSerializer.Serialize(jsonWriter, boundingBox);
            }

            jsonWriter.WriteEndArray();
            jsonWriter.WriteEndObject();

            if (boundingBoxes.Where(x => x != null).Count() > 1)
            {
                Console.Write(stringWriter.ToString() + "\n\n");
            }

            return stringWriter.ToString();
        }
    }
}