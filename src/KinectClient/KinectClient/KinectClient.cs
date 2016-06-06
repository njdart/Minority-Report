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
using System.Runtime.InteropServices;

namespace MinorityReport
{
    public class KinectClient
    {
        private class Configuration
        {
            public IList<IList<float>> matrix;
            public string host;
            public int port;
            public double plane_A;
            public double plane_B;
            public double plane_C;
            public double plane_D;

            public Configuration()
            {
                this.matrix = new IList<float>[3];
                for (int i = 0; i < 3; ++i)
                {
                    this.matrix[i] = new float[3];
                }
            }
        }

        #region Private variables
        private KinectSensor sensor = null;
        private MultiSourceFrameReader multiFrameReader = null;

        private bool samplingColorFrames = false;
        private bool samplingBodyData = false;

        private ushort[] calibrationDepthData;

        private byte[] latestColorPNG = null;
        private string configFile = "config.json";

        private string instanceID;

        private Draw.PointF[] canvasCoords;
        private Matrix<float> perspectiveMatrix = null;
        private double plane_A;
        private double plane_B;
        private double plane_C;
        private double plane_D;

        private IList<ColorSpacePoint> canvasPoints;
        private IList<ColorSpacePoint> mappedCanvasPoints;

        private Timer sensorAvailableTimer;
        private bool sensorTimerElapsed = false;
        private bool testMapping = true;
        private bool calibrationComplete = false;
        private bool boardObstructed = false;
        #endregion

        public string Server { get; set; } = null;
        public int Port { get; set; } = 8088;

        public event EventHandler<bool> BoardObscuredChanged;

        public KinectClient(string server, int port)
        {
            if (this.ConfigurationFromFile())
            {
                Console.Write("Calibrated perspective matrix retrieved from file saved in previous session.\n");
            }
            else
            {
                Console.Write("Kinect application is not calibrated.\n");
            }

            // If this timer elapses, an exception is thrown in Run().
            this.sensorAvailableTimer = new Timer(5000);
            this.sensorAvailableTimer.Elapsed += this.SensorAvailableTimer_Elapsed;
            this.sensorAvailableTimer.Start();

            this.sensor = KinectSensor.GetDefault();
            this.sensor.IsAvailableChanged += Sensor_IsAvailableChanged;
            this.sensor.Open();

            // this.bodyIndexReader = this.sensor.BodyIndexFrameSource.OpenReader();
            // this.colorReader = this.sensor.ColorFrameSource.OpenReader();
            this.multiFrameReader = this.sensor.OpenMultiSourceFrameReader(FrameSourceTypes.BodyIndex |
                                                                           FrameSourceTypes.Color     |
                                                                           FrameSourceTypes.Depth     |
                                                                           FrameSourceTypes.Body);

            // this.bodyIndexReader.FrameArrived += this.BodyIndexReader_FrameArrived;
            // this.colorReader.FrameArrived += this.ColorReader_FrameArrived;
            this.multiFrameReader.MultiSourceFrameArrived += this.MultiFrameReader_MultiSourceFrameArrived;
            this.samplingBodyData = true;

            this.BoardObscuredChanged += this.KinectClient_BoardObscuredChanged;
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

                                this.ListCanvasPixels();

                                // Convert the depth image to camera space (X,Y,Z; Z extending from the front of the IR
                                // sensor), at 1080p (so each pixel in color space can be assigned a 3D camera space
                                // point).
                                CoordinateMapper mapper = this.sensor.CoordinateMapper;
                                CameraSpacePoint[] cameraPoints = new CameraSpacePoint[1920 * 1080];
                                mapper.MapColorFrameToCameraSpace(this.calibrationDepthData, cameraPoints);

                                // Get the camera space points at the canvas corners
                                Vector<float>[] canvasPoints3D = new Vector<float>[3];
                                for (int i = 0; i < 3; ++i)
                                {
                                    int x = (int)Math.Floor(this.canvasCoords[i].X);
                                    int y = (int)Math.Floor(this.canvasCoords[i].Y);
                                    Console.Write("({0}, {1}, {2})\n", cameraPoints[x + y * 1920].X, cameraPoints[x + y * 1920].Y, cameraPoints[x + y * 1920].Z);

                                    canvasPoints3D[i] = CreateVector.Dense<float>(3);
                                    canvasPoints3D[i][0] = cameraPoints[x + y * 1920].X;
                                    canvasPoints3D[i][1] = cameraPoints[x + y * 1920].Y;
                                    canvasPoints3D[i][2] = cameraPoints[x + y * 1920].Z;
                                }
                                Console.Write("(Skipping the final point.)\n");

                                // Calculate the normal of the plane of the canvas.
                                Vector<float> U = canvasPoints3D[0] - canvasPoints3D[1];
                                Vector<float> V = canvasPoints3D[1] - canvasPoints3D[2];
                                Vector<float> N = CreateVector.Dense<float>(3);
                                N[0] = U[1] * V[2] - U[2] * V[1];
                                N[1] = U[2] * V[0] - U[0] * V[2];
                                N[2] = U[0] * V[1] - U[1] * V[0];
                                Console.Write("Normal: ({0}, {1}, {2})\n", N[0], N[1], N[2]);

                                // Calculate the parameters of the plane in the form: ax + by + cz + d = 0
                                Vector<float> X = canvasPoints3D[0];
                                this.plane_A = N[0];
                                this.plane_B = N[1];
                                this.plane_C = N[2];
                                this.plane_D = -(N[0] * X[0] + N[1] * X[1] + N[2] * X[2]);

                                this.ConfigurationToFile();
                                this.calibrationComplete = true;
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
                }
            });
            listenerTask.Start();

            while (active)
            {
                if (kinectFault)
                {
                    active = false;
                    throw new Exception("The Kinect sensor is unavailable.");
                }
            }
        }

        private void MultiFrameReader_MultiSourceFrameArrived(object sender, MultiSourceFrameArrivedEventArgs e)
        {
            BodyIndexFrame bodyIndexFrame = null;
            ColorFrame colorFrame = null;
            DepthFrame depthFrame = null;
            BodyFrame bodyFrame = null;

            try
            {
                MultiSourceFrameReference multiFrameRef = e.FrameReference;
                MultiSourceFrame multiFrame = multiFrameRef.AcquireFrame();

                BodyIndexFrameReference bodyIndexFrameRef = multiFrame.BodyIndexFrameReference;
                ColorFrameReference colorFrameRef = multiFrame.ColorFrameReference;
                DepthFrameReference depthFrameRef = multiFrame.DepthFrameReference;
                BodyFrameReference bodyFrameRef = multiFrame.BodyFrameReference;

                bodyIndexFrame = bodyIndexFrameRef.AcquireFrame();
                colorFrame = colorFrameRef.AcquireFrame();
                depthFrame = depthFrameRef.AcquireFrame();
                bodyFrame = bodyFrameRef.AcquireFrame();

                if (bodyIndexFrame == null || colorFrame == null || depthFrame == null || bodyFrame == null)
                {
                    return;
                }

                ushort[] depthData = new ushort[depthFrame.FrameDescription.LengthInPixels];
                depthFrame.CopyFrameDataToArray(depthData);

                if (this.samplingColorFrames)
                {
                    this.SaveColorImage(colorFrame);
                    this.calibrationDepthData = depthData;
                    this.samplingColorFrames = false;
                }

                // The block below is for debug purposes - it runs only once, upon the first received MultiSourceFrame.
                if (this.testMapping)
                {
                    // Save color image to PNG file
                    this.SaveColorImage(colorFrame);
                    FileStream colorImgFile = new FileStream("color_img_debug.png", FileMode.Create);
                    colorImgFile.Write(this.latestColorPNG, 0, this.latestColorPNG.Length);
                    colorImgFile.Close();

                    // Map each depth point to a point in 'color space'
                    CoordinateMapper mapper = this.sensor.CoordinateMapper;
                    ColorSpacePoint[] mappedColorPoints = new ColorSpacePoint[depthData.Length];
                    mapper.MapDepthFrameToColorSpace(depthData, mappedColorPoints);

                    // Produce a BGRA image of the depth data at 1080p
                    byte[] depthImg = new byte[1920 * 1080 * 4];
                    for (int i = 0; i < depthData.Length; ++i)
                    {
                        int x = (int)Math.Floor(mappedColorPoints[i].X);
                        int y = (int)Math.Floor(mappedColorPoints[i].Y);

                        if (x >= 0 && x < 1920 && y >= 0 && y < 1080)
                        {
                            int idx = 4 * (x + y * 1920);
                            depthImg[idx] = 255;
                            depthImg[idx + 1] = 255;
                            depthImg[idx + 2] = 255;
                            depthImg[idx + 3] = 255;
                        }
                    }

                    // Save the produced depth image to PNG file
                    WriteableBitmap bmp = new WriteableBitmap(1920, 1080, 96, 96, PixelFormats.Bgra32, null);
                    bmp.Lock();
                    Marshal.Copy(depthImg, 0, bmp.BackBuffer, depthImg.Length);
                    bmp.AddDirtyRect(new Int32Rect(0, 0, 1920, 1080));
                    bmp.Unlock();
                    PngBitmapEncoder pngEncode = new PngBitmapEncoder();
                    pngEncode.Frames.Add(BitmapFrame.Create(bmp));
                    FileStream depthImgFile = new FileStream("depth_img_debug.png", FileMode.Create);
                    pngEncode.Save(depthImgFile);
                    depthImgFile.Close();

                    // Map depth points into color space, then each color space point into camera space
                    CameraSpacePoint[] cameraSpacePoints = new CameraSpacePoint[1920 * 1080];
                    this.sensor.CoordinateMapper.MapColorFrameToCameraSpace(depthData, cameraSpacePoints);

                    // Set colour in 1080p image depending on Z value.
                    byte[] cameraImg = new byte[cameraSpacePoints.Length];
                    for (int i = 0; i < cameraSpacePoints.Length; ++i)
                    {
                        // Map from 0 to 4 metres.
                        int z = (int)Math.Floor((cameraSpacePoints[i].Z - 2) * (256));
                        if (z > 255) z = 255;
                        else if (z < 0) z = 0;
                        cameraImg[i] = (byte)z;
                    }

                    // Save produced camera image to PNG file
                    bmp = new WriteableBitmap(1920, 1080, 96, 96, PixelFormats.Gray8, null);
                    bmp.Lock();
                    Marshal.Copy(cameraImg, 0, bmp.BackBuffer, cameraImg.Length);
                    bmp.AddDirtyRect(new Int32Rect(0, 0, 1920, 1080));
                    bmp.Unlock();
                    pngEncode = new PngBitmapEncoder();
                    pngEncode.Frames.Add(BitmapFrame.Create(bmp));
                    FileStream cameraImgFile = new FileStream("camera_img_debug.png", FileMode.Create);
                    pngEncode.Save(cameraImgFile);
                    cameraImgFile.Close();

                    this.testMapping = false;
                }

                if (this.samplingBodyData && this.perspectiveMatrix != null && this.calibrationComplete)
                {
                    // Detect board obstruction
                    {
                        // Get 3D point of every pixel in color frame
                        CameraSpacePoint[] cameraPoints = new CameraSpacePoint[1920 * 1080];
                        CoordinateMapper mapper = this.sensor.CoordinateMapper;
                        mapper.MapColorFrameToCameraSpace(depthData, cameraPoints);

                        // FileStream f = new FileStream("keke.txt", FileMode.Create);
                        // StreamWriter s = new StreamWriter(f);

                        Vector<float> V = CreateVector.Dense<float>(3);
                        bool obstructed = false;

                        // Iterate over every pixel that is part of the canvas
                        // Console.Write("there are {0} canvas points.\n", this.canvasPoints.Count);
                        for (int i = 0; i < this.canvasPoints.Count; ++i)
                        {
                            // Get the 3D point corresponding to the pixel.
                            int x = (int)Math.Floor(this.canvasPoints[i].X);
                            int y = (int)Math.Floor(this.canvasPoints[i].Y);
                            int idx = x + y * 1920;
                            V[0] = cameraPoints[idx].X;
                            V[1] = cameraPoints[idx].Y;
                            V[2] = cameraPoints[idx].Z;

                            // Get the direct distance between the plane of the canvas and the point.
                            float dist = this.ShortestDistanceToCanvasPlane(V);

                            // s.Write("{0}\n", dist);

                            if (dist > 0.10)
                            {
                                obstructed = true;
                                // Console.Write("Pixel ({0}, {1}) is obscuring the board ({2}m from board).\n", x, y, dist);
                                break;
                            }
                        }
                        if (this.BoardObscuredChanged != null && obstructed != this.boardObstructed)
                        {
                            this.BoardObscuredChanged.Invoke(this, obstructed);
                            this.boardObstructed = obstructed;
                        }
                    }

                    // Detect hands near whiteboard
                    if (bodyFrame.BodyCount > 0)
                    {
                        IList<Body> bodies = new Body[bodyFrame.BodyCount];
                        bodyFrame.GetAndRefreshBodyData(bodies);

                        for (int i = 0; i < bodies.Count; ++i)
                        {
                            Body body = bodies[i];
                            Joint handTipRight = body.Joints[JointType.HandTipRight];
                            if (handTipRight.TrackingState != TrackingState.NotTracked)
                            {
                                CameraSpacePoint pos = handTipRight.Position;
                                Vector<float> V = CreateVector.Dense<float>(3);
                                V[0] = pos.X;
                                V[1] = pos.Y;
                                V[2] = pos.Z;
                                float dist = this.ShortestDistanceToCanvasPlane(V);
                                if (dist < 0.10)
                                {
                                    // Console.Write("Body {0}'s HandTipRight is {1} centimetres from the whiteboard.\n", i, dist * 100);
                                }
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Write("Exception occurred in MultiFrameReader_MultiSourceFrameArrived: {0}", ex.ToString());
            }
            finally
            {
                if (bodyIndexFrame != null) bodyIndexFrame.Dispose();
                if (colorFrame != null) colorFrame.Dispose();
                if (depthFrame != null) depthFrame.Dispose();
                if (bodyFrame != null) bodyFrame.Dispose();
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

        private float ShortestDistanceToCanvasPlane(Vector<float> vec)
        {
            float dist = (float)Math.Abs(
                this.plane_A * vec[0] +
                this.plane_B * vec[1] +
                this.plane_C * vec[2] +
                this.plane_D);
            dist /= (float)Math.Sqrt(
                Math.Pow(this.plane_A, 2) +
                Math.Pow(this.plane_B, 2) +
                Math.Pow(this.plane_C, 2));

            return dist;
        }

        private void ListCanvasPixels()
        {
            // Get list of color pixels which lie within the canvas
            this.canvasPoints = new List<ColorSpacePoint>();
            this.mappedCanvasPoints = new List<ColorSpacePoint>();
            for (int x = 0; x < 1920; ++x)
            {
                for (int y = 0; y < 1080; ++y)
                {
                    Vector<float> v = CreateVector.Dense<float>(3);
                    v[0] = x;
                    v[1] = y;
                    v[2] = 1;
                    v = this.TransformToCanvasSpace(v);
                    if (this.IsVectorObstructingCanvas(v))
                    {
                        ColorSpacePoint p1 = new ColorSpacePoint();
                        ColorSpacePoint p2 = new ColorSpacePoint();
                        p1.X = x;
                        p1.Y = y;
                        p2.X = v[0];
                        p2.Y = v[1];
                        this.canvasPoints.Add(p1);
                        this.mappedCanvasPoints.Add(p2);
                    }
                }
            }

            // Produce 1080p image (grayscale) where white pixels are within the canvas bounds
            WriteableBitmap bmp;
            PngBitmapEncoder pngEncode;

            byte[] canvasPixelsImg = new byte[1920 * 1080];
            foreach (ColorSpacePoint p in this.canvasPoints)
            {
                int x = (int)Math.Floor(p.X);
                int y = (int)Math.Floor(p.Y);
                canvasPixelsImg[x + 1920 * y] = 255;
            }
            bmp = new WriteableBitmap(1920, 1080, 96, 96, PixelFormats.Gray8, null);
            bmp.Lock();
            Marshal.Copy(canvasPixelsImg, 0, bmp.BackBuffer, canvasPixelsImg.Length);
            bmp.AddDirtyRect(new Int32Rect(0, 0, 1920, 1080));
            bmp.Unlock();
            pngEncode = new PngBitmapEncoder();
            pngEncode.Frames.Add(BitmapFrame.Create(bmp));
            FileStream canvasPixelsImgFile = new FileStream("canvas_pixels_img_debug.png", FileMode.Create);
            pngEncode.Save(canvasPixelsImgFile);
            canvasPixelsImgFile.Close();
        }

        private bool ConfigurationFromFile()
        {
            FileStream f;

            try
            {
                f = new FileStream(this.configFile, FileMode.Open);
            }
            catch (FileNotFoundException)
            {
                return false;
            }

            byte[] data = new byte[f.Length];
            f.Read(data, 0, (int)f.Length);
            f.Close();
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
            this.plane_A = config.plane_A;
            this.plane_B = config.plane_B;
            this.plane_C = config.plane_C;
            this.plane_D = config.plane_D;

            this.ListCanvasPixels();

            this.calibrationComplete = true;
            return true;
        }

        private void ConfigurationToFile()
        {
            FileStream f;
            f = new FileStream(this.configFile, FileMode.Create);
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
            config.plane_A = this.plane_A;
            config.plane_B = this.plane_B;
            config.plane_C = this.plane_C;
            config.plane_D = this.plane_D;
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
                output = output.Divide(output[2]);
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

        private void SaveColorImage(ColorFrame colorFrame)
        {
            if (colorFrame == null)
            {
                return;
            }

            // Get pixel data
            byte[] pixels = new byte[colorFrame.FrameDescription.Width * colorFrame.FrameDescription.Height * 4];
            colorFrame.CopyConvertedFrameDataToArray(pixels, ColorImageFormat.Bgra);

            // Create a bitmap structure to hold data
            WriteableBitmap bmp = new WriteableBitmap(colorFrame.FrameDescription.Width,
                                                           colorFrame.FrameDescription.Height,
                                                           96.0, 96.0,
                                                           PixelFormats.Bgr32,
                                                           null);

            // Write data into a bitmap structure
            using (KinectBuffer buf = colorFrame.LockRawImageBuffer())
            {
                bmp.Lock();
                colorFrame.CopyConvertedFrameDataToIntPtr(bmp.BackBuffer,
                                                     (uint)colorFrame.FrameDescription.LengthInPixels * 4,
                                                     ColorImageFormat.Bgra);
                bmp.AddDirtyRect(new Int32Rect(0, 0, bmp.PixelHeight, bmp.PixelHeight));
                bmp.Unlock();
            }

            // Encode the data into a PNG file format
            PngBitmapEncoder encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(bmp));

            using (MemoryStream stream = new MemoryStream())
            {
                encoder.Save(stream);
                this.latestColorPNG = stream.ToArray();
            }
        }
    }
}
