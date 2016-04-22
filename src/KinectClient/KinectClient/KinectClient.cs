using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Net.Http;
using Microsoft.Kinect;

namespace MinorityReport
{
    public class KinectClient
    {
        #region Constants

        // Number of milliseconds of Kinect unavailability before the Kinect is assumed to be disconnected.
        const int KINECT_TIMEOUT_MS = 5000;

        // Number of milliseconds to wait for the sensor to open.
        const int KINECT_OPEN_DELAY_MS = 1000;
        #endregion

        #region Private members

        // Settings
        private string m_serverHost;
        private int    m_serverPort;

        // Status
        private bool m_initSuccessful;
        private bool m_shuttingDown;
        private ShuttingDownReason m_shutdownReason;

        // Member objects
        private HttpClient m_httpClient;
        private KinectSensor m_kinectSensor;
        private BodyIndexFrameReader m_bodyIndexFrameReader;

        // Log4net
        private static readonly log4net.ILog m_log = log4net.LogManager.GetLogger
     (System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        #endregion

        #region Properties

        public bool InitSuccessful { get { return m_initSuccessful; } }

        #endregion

        #region Constructor

        /// <summary>
        /// Constructor. Takes command-line arguments.
        /// </summary>
        /// <param name="args">Array of command-line arguments.</param>
        public KinectClient(string[] args)
        {
            // Default status and settings
            m_initSuccessful = false;
            m_shuttingDown = false;
            m_shutdownReason = ShuttingDownReason.UserAbort;
            m_serverHost = "";
            m_serverPort = -1;

            m_log.Debug("Hello from KinectClient.");

            // Parse command line arguments.
            m_initSuccessful = ParseArgs(args);
            if (!m_initSuccessful)
            {
                m_shuttingDown = true;
                return;
            }

            // Open the Kinect sensor and set event handlers.
            m_kinectSensor = KinectSensor.GetDefault();
            m_kinectSensor.Open();
            m_kinectSensor.IsAvailableChanged += m_kinectSensor_IsAvailableChanged;
            m_bodyIndexFrameReader = m_kinectSensor.BodyIndexFrameSource.OpenReader();
            m_bodyIndexFrameReader.FrameArrived += BodyIndexFrameReader_FrameArrived;

            // Check initial availability of the sensor; give it 1 second to connect first.
            Thread.Sleep(KINECT_OPEN_DELAY_MS);
            if (!m_kinectSensor.IsAvailable)
            {
                Task.Run(() => DetectKinectTimeout());
            }

            m_log.Debug("Initialisation complete.");
        }

        #endregion

        #region Events

        #endregion

        #region Public methods

        public ShuttingDownReason Run()
        {
            m_log.Debug("Starting KinectClient execution.");

            // Wait...
            while (!m_shuttingDown) ;

            m_log.Debug("Shutting down.");
            return m_shutdownReason;
        }

        #endregion

        #region Private methods

        private bool ParseArgs(string[] args)
        {
            foreach (string arg in args)
            {
                if ((arg.Substring(0, 7) == "--host=") &&
                    (arg.Length > 7))
                {
                    if (m_serverHost != "")
                    {
                        m_log.Error("Host cannot be specified more than once.");
                        return false;
                    }
                    m_serverHost = arg.Substring(7);
                }

                else if ((arg.Substring(0, 7) == "--port=") &&
                         (arg.Length > 7))
                {
                    if (m_serverPort != -1)
                    {
                        m_log.Error("Port cannot be specified more than once.");
                        return false;
                    }
                    try
                    {
                        m_serverPort = Int32.Parse(arg.Substring(7));
                    }
                    catch (Exception ex)
                    {
                        if (ex is FormatException || ex is OverflowException)
                        {
                            m_log.Error("Invalid port specified.");
                            return false;
                        }
                        throw;
                    }
                    if (m_serverPort < 0)
                    {
                        m_log.Error("Invalid port specified.");
                        return false;
                    }
                }
                else
                {
                    m_log.WarnFormat("Arg '{0}' unrecognised.", arg);
                }
            }

            bool retval = true;
            if (m_serverHost == "")
            {
                m_log.Error("No server host specified.");
                retval = false;
            }
            if (m_serverPort == -1)
            {
                m_log.Error("No server port specified.");
                retval = false;
            }
            return retval;
        }

        private void BodyIndexFrameReader_FrameArrived(object sender, BodyIndexFrameArrivedEventArgs e)
        {
            using (BodyIndexFrame bodyIndexFrame = e.FrameReference.AcquireFrame())
            {
                m_log.DebugFormat("Body index frame arrived; width: {0}; height: {1}",
                    bodyIndexFrame.FrameDescription.Width,
                    bodyIndexFrame.FrameDescription.Height);

                int width = bodyIndexFrame.FrameDescription.Width;
                int height = bodyIndexFrame.FrameDescription.Height;
                int maxBodyCount = m_kinectSensor.BodyFrameSource.BodyCount;

                byte[] frameData = new byte[width * height];
                bodyIndexFrame.CopyFrameDataToArray(frameData);

                // Indicator of the bodies found
                bool[] bodiesFound = new bool[maxBodyCount];
                for (int i = 0; i < maxBodyCount; ++i)
                {
                    bodiesFound[i] = false;
                }

                // Format of the boundingPoints array:
                //
                //              |-------|-------|-------|-------|
                //              | Min X | Max X | Min Y | Max Y |
                // |------------|-------|-------|-------|-------|
                // | Body 1     | [0,0] | [0,1] | [0,2] | [0,3] | etc.
                // |------------|-------|-------|-------|-------|
                // | Body 2     |       |       |       |       |
                // |------------|-------|-------|-------|-------|
                // | Body 3     |       |       |       |       |
                // |------------|-------|-------|-------|-------|
                // | Body 4     |       |       |       |       |
                // |------------|-------|-------|-------|-------|
                // | ...        |       |       |       |       |
                // |------------|-------|-------|-------|-------|
                //
                int[,] boundingPoints = new int[maxBodyCount, 4];
                for (int i = 0; i < maxBodyCount; ++i)
                {
                    boundingPoints[i,0] = width;
                    boundingPoints[i,1] = -1;
                    boundingPoints[i,2] = height;
                    boundingPoints[i,3] = -1;
                }

                for (int x = 0; x < width; ++x)
                {
                    for (int y = 0; y < height; ++y)
                    {
                        int bodyIndex = frameData[x + y * width];
                        if (bodyIndex < maxBodyCount)
                        {
                            bodiesFound[bodyIndex] = true;
                            // Min X
                            if (x < boundingPoints[bodyIndex, 0])
                            {
                                boundingPoints[bodyIndex, 0] = x;
                            }
                            // Max X
                            if (x > boundingPoints[bodyIndex, 1])
                            {
                                boundingPoints[bodyIndex, 1] = x;
                            }
                            // Min Y
                            if (y < boundingPoints[bodyIndex, 2])
                            {
                                boundingPoints[bodyIndex, 2] = y;
                            }
                            // Max Y
                            if (y > boundingPoints[bodyIndex, 3])
                            {
                                boundingPoints[bodyIndex, 3] = y;
                            }
                        }
                    }
                }
                for (int i = 0; i < maxBodyCount; ++i)
                {
                    if (bodiesFound[i])
                    {
                        m_log.DebugFormat("Found a body (index {0}) with bounding box: ({1}, {2}); ({3}, {4}).",
                            i,
                            boundingPoints[i, 0],
                            boundingPoints[i, 2],
                            boundingPoints[i, 1],
                            boundingPoints[i, 3]);
                    }
                }
            }
        }

        private void m_kinectSensor_IsAvailableChanged(object sender, IsAvailableChangedEventArgs e)
        {
            if (!e.IsAvailable)
            {
                m_log.Debug("Kinect unavailable.");
                // The Kinect is unavailable, but this might just be temporary. Asynchronously run DetectKinectTimeout.
                Task.Run(() => DetectKinectTimeout());
            }
        }

        private void DetectKinectTimeout()
        {
            m_log.Debug("Kinect timeout detection started.");

            CancellationTokenSource ctSource = new CancellationTokenSource();
            CancellationToken ct = ctSource.Token;
            ctSource.CancelAfter(KINECT_TIMEOUT_MS);

            // Until the timeout is reached, poll availability of the sensor.
            while (!ct.IsCancellationRequested)
            {
                if (m_kinectSensor.IsAvailable)
                {
                    m_log.Debug("Kinect availability returned.");
                    return;
                }
            }

            // The timeout was reached and the Kinect is still unavailable, so shut down.
            m_shuttingDown = true;
            m_shutdownReason = ShuttingDownReason.KinectUnavailable;
            m_log.Debug("Kinect timed out.");
        }

        /// <summary>
        /// Check if the server is alive.
        /// </summary>
        /// <returns>True if server is alive, false otherwise.</returns>
        private async Task<bool> PollServerAlive()
        {
            string uriStr = string.Format("http://{0}:{1}/alive",
                                          m_serverHost,
                                          m_serverPort);

            HttpRequestMessage msg = new HttpRequestMessage();
            msg.Method     = HttpMethod.Get;
            msg.RequestUri = new Uri(uriStr);

            try
            {
                HttpResponseMessage response = await m_httpClient.SendAsync(msg);
            }
            catch (HttpRequestException)
            {
                return false;
            }

            return true;
        }

        #endregion
    }
}