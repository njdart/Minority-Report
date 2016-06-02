using MathNet.Numerics.LinearAlgebra;
using Microsoft.Kinect;
using Newtonsoft.Json;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Timers;
using System.Windows.Media.Imaging;
using System.Windows.Media;
using System.Windows;
using System;

// Yes, this is ugly. Blame Microsoft for creating a class named PointF in two libraries that behave completely
// differently. Seriously, why?
using Draw = System.Drawing;

namespace MinorityReport
{
    public class KinectClient
    {
        private class Configuration
        {
            public IList<IList<float>> matrix;
            public string host;
            public int port;

            public Configuration()
            {
                this.matrix = new IList<float>[3];
                for (int i = 0; i < 3; ++i)
                {
                    this.matrix[i] = new float[3];
                }
            }
        }

        private KinectSensor sensor = null;
        private BodyIndexFrameReader bodyIndexReader = null;
        private ColorFrameReader colorReader = null;

        private bool samplingColorFrames = false;
        private bool samplingBodyData = false;

        private byte[] latestColorPNG = null;
        private Draw.PointF latestPNGDimensions;
        private Matrix<float> perspectiveMatrix = null;
        private string matrixFile = "matrix.json";

        private string instanceID;

        private Draw.PointF[] canvasCoords;
        private bool boardObscured = false;

        private Timer sensorAvailableTimer;
        private bool sensorTimerElapsed = false;

        public string Server { get; set; } = null;
        public int Port { get; set; } = 8088;

        public event EventHandler<bool> BoardObscuredChanged;

        public KinectClient(string server, int port)
        {
            // If this timer elapses, an exception is thrown in Run().
            this.sensorAvailableTimer = new Timer(5000);
            this.sensorAvailableTimer.Elapsed += this.SensorAvailableTimer_Elapsed;
            this.sensorAvailableTimer.Start();

            this.sensor = KinectSensor.GetDefault();
            this.sensor.IsAvailableChanged += Sensor_IsAvailableChanged;
            this.sensor.Open();

            this.bodyIndexReader = this.sensor.BodyIndexFrameSource.OpenReader();
            this.colorReader = this.sensor.ColorFrameSource.OpenReader();
            this.bodyIndexReader.FrameArrived += this.BodyIndexReader_FrameArrived;
            this.colorReader.FrameArrived += this.ColorReader_FrameArrived;
            this.samplingBodyData = true;

            this.BoardObscuredChanged += this.KinectClient_BoardObscuredChanged;

            if (this.ConfigurationFromFile())
            {
                Console.Write("Calibrated perspective matrix retrieved from file saved in previous session.\n");
            }
            else
            {
                Console.Write("Kinect application is not calibrated.\n");
            }
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

                                // Calculate perspective matrix, which maps between color space and canvas space.
                                this.canvasCoords = ImageWarping.OrderPoints(this.canvasCoords);
                                Draw.PointF[] outputBounds = new Draw.PointF[4] {
                                    new Draw.PointF(0, 0),
                                    new Draw.PointF(0, 1079),
                                    new Draw.PointF(1919, 0),
                                    new Draw.PointF(1919, 1079)
                                };
                                outputBounds = ImageWarping.OrderPoints(outputBounds);
                                this.perspectiveMatrix = ImageWarping.GetPerspectiveTransform(this.canvasCoords, outputBounds);
                                this.ConfigurationToFile();
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

        private bool ConfigurationFromFile()
        {
            FileStream f;

            try
            {
                f = new FileStream(this.matrixFile, FileMode.Open);
            }
            catch (FileNotFoundException)
            {
                return false;
            }

            byte[] data = new byte[f.Length];
            f.Read(data, 0, (int)f.Length);
            Configuration config = JsonConvert.DeserializeObject<Configuration>(Encoding.UTF8.GetString(data));
            if (config == null)
            {
                return false;
            }

            this.perspectiveMatrix = CreateMatrix.Dense<float>(3, 3);
            for (int j = 0; j < 3; ++j)
            {
                for (int i = 0; i < 3; ++i)
                {
                    this.perspectiveMatrix[i, j] = config.matrix[i][j];
                }
            }
            this.Server = config.host;
            this.Port = config.port;
            f.Close();

            return true;
        }

        private void ConfigurationToFile()
        {
            FileStream f;
            f = new FileStream(this.matrixFile, FileMode.Create);
            Configuration config = new Configuration();
            for (int j = 0; j < 3; ++j)
            {
                for (int i = 0; i < 3; ++i)
                {
                    config.matrix[i][j] = this.perspectiveMatrix[i, j];
                }
            }
            config.host = this.Server;
            config.port = this.Port;
            byte[] data = Encoding.UTF8.GetBytes(JsonConvert.SerializeObject(config));
            f.Write(data, 0, data.Length);
            f.Close();
        }

        private Vector<float> TransformToCanvasSpace(Vector<float> vec)
        {
            if (this.perspectiveMatrix != null)
            {
                // The perspective matrix maps between color frame space and canvas space. Points within the canvas area
                // are mapped to coordinates between (0, 0) and (1920, 1080).
                Vector<float> output = this.perspectiveMatrix.Multiply(vec);

                // This is a 2D perspective transformation done in a "virtual" 3D space, so there is a 3rd coordinate
                // involved. To convert the vector into the 2D canvas space, the 2D coordinates are divided by the
                // third coordinate (named the "homogeneous" coordinate).
                output.Divide(output[2]);
                return output;
            }
            return null;
        }

        private bool IsVectorObstructingCanvas(Vector<float> transformedVec)
        {
            // This method expects transformedVec to contain 2D coordinates in canvas space.
            if (transformedVec[0] > 0 && transformedVec[0] < 1920 &&
                transformedVec[1] > 0 && transformedVec[1] < 1080)
            {
                return true;
            }
            return false;
        }

        private void SensorAvailableTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            // If this timer has elapsed, the Kinect sensor has been unavailable for too long...
            Console.Write("Kinect has been unavailable for {0} seconds.\n", ((Timer)sender).Interval / 1000);
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
            try
            {
                context.Response.ContentLength64 = data.Length;
                context.Response.OutputStream.Write(data, 0, data.Length);
            }
            catch (HttpListenerException)
            {
                return false;
            }
            return true;
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

                    // Iterate over every pixel, top to bottom, left to right
                    for (int y = 0; y < frame.FrameDescription.Height && !obscured; ++y)
                    {
                        for (int x = 0; x < frame.FrameDescription.Width && !obscured; ++x)
                        {
                            int bufIdx = y * frame.FrameDescription.Width + x;
                            int bodyIdx = frameBuf[bufIdx];
                            if (bodyIdx <= 5 && bodyIdx >= 0)
                            {
                                // Pixel is part of an identified body
                                float ratioX = 2.86f;
                                float ratioY = 2.86f;
                                float offsetX = 253;
                                float offsetY = -35;

                                // This translates the pixel's coordinates from body index frame space to color frame
                                // space (the two frames have different resolutions and fields of view).
                                float xf = x * ratioX + offsetX;
                                float yf = y * ratioY + offsetY;

                                // Transform from color space to canvas space.
                                Vector<float> v = CreateVector.Dense<float>(3);
                                v[0] = xf;
                                v[1] = yf;
                                v[2] = 1;
                                Vector<float> vout = this.TransformToCanvasSpace(v);

                                if (this.IsVectorObstructingCanvas(vout))
                                {
                                    // The coordinate (in canvas space) lies within the bounds of the canvas; between
                                    // (0, 0) and (1920, 1080). Therefore, a body is obscuring the board.
                                    obscured = true;
                                    break;
                                }
                            }
                        }
                    }

                    if (obscured != this.boardObscured)
                    {
                        // If the state has changed, raise the event.
                        if (this.BoardObscuredChanged != null) this.BoardObscuredChanged.Invoke(this, obscured);
                    }
                    this.boardObscured = obscured;
                }
            }
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
    }
}