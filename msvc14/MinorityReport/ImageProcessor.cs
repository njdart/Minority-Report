using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Kinect;

using Emgu.CV;
using Emgu.CV.CvEnum;

namespace MinorityReport
{
    class ImageProcessorException : Exception
    {
        #region Constructors

        public ImageProcessorException()
        {
        }

        public ImageProcessorException(string message)
            : base(message)
        {
        }

        public ImageProcessorException(string message, Exception inner)
            : base(message, inner)
        {
        }

        #endregion
    }

    class ImageProcessor
    {
        #region Private members

        // Kinect stuff
        private KinectSensor        m_KinectSensor     = null;
        private ColorFrameReader    m_ColorFrameReader = null;
        private InfraredFrameReader m_IRFrameReader    = null;
        private BodyFrameReader     m_BodyFrameReader  = null;

        // Our webcam handling class
        private WebcamReader        m_WebcamReader     = null;

        #endregion

        #region Properties

        public bool KinectAvailable
        {
            get
            {
                return (m_KinectSensor.IsAvailable);
            }
        }

        public bool WebcamAvailable
        {
            get
            {
                return false;
            }
        }

        #endregion

        #region Constructor

        public ImageProcessor()
        {
            // Get the sensor
            m_KinectSensor = KinectSensor.GetDefault();
            
            // Kinect data streams
            // m_ColorFrameReader = m_KinectSensor.ColorFrameSource.OpenReader();
            // m_IRFrameReader = m_KinectSensor.InfraredFrameSource.OpenReader();
            m_BodyFrameReader = m_KinectSensor.BodyFrameSource.OpenReader();

            // Register handlers
            // m_ColorFrameReader.FrameArrived += c_ColorFrameArrived;
            // m_IRFrameReader.FrameArrived += c_IRFrameArrived;
            m_BodyFrameReader.FrameArrived += c_BodyFrameArrived;
            m_KinectSensor.IsAvailableChanged += c_IsAvailableChanged;

            // Enable!
            m_KinectSensor.Open();
        }

        #endregion

        #region Methods

        /// <summary>
        /// Starts the streaming of data from the Kinect and/or other imaging devices.
        /// </summary>
        public void StartStreaming()
        {
        }

        /// <summary>
        /// Stops the streaming of data from imaging devices.
        /// </summary>
        public void StopStreaming()
        {
        }

        #endregion

        #region Event handlers

        void c_ColorFrameArrived(object sender, ColorFrameArrivedEventArgs evtArgs)
        {
            // Console.Write("Color frame arrived.\n");
        }

        void c_IRFrameArrived(object sender, InfraredFrameArrivedEventArgs evtArgs)
        {
            // Console.Write("Infrared frame arrived.\n");
        }

        private Body[] m_bodies = null;

        void c_BodyFrameArrived(object sender, BodyFrameArrivedEventArgs evtArgs)
        {
            Console.Write("Body frame arrived - getting data... ");
            BodyFrame bodyFrame = evtArgs.FrameReference.AcquireFrame();
            if (bodyFrame != null)
            {
                Console.Write("Non-null return value... ");
                if (m_bodies == null)
                {
                    Console.Write("Initialising m_bodies[{0}]... ", bodyFrame.BodyCount);
                    m_bodies = new Body[bodyFrame.BodyCount];
                }
                bodyFrame.GetAndRefreshBodyData(m_bodies);
                Console.Write("Body data refreshed. Body count of {0}.\n", bodyFrame.BodyCount);
            }
            else
            {
                Console.Write("No data!\n");
            }
        }

        void c_IsAvailableChanged(object sender, IsAvailableChangedEventArgs evtArgs)
        {
            Console.Write("The Kinect became {0}available!\n", evtArgs.IsAvailable ? "" : "un");
        }

        #endregion
    }
}
