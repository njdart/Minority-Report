using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Kinect;
using System.Drawing;

namespace MinorityReport
{
    class KinectHandlerException : Exception
    {
        #region Constructors

        public KinectHandlerException()
        {
        }

        public KinectHandlerException(string message)
            : base(message)
        {
        }

        public KinectHandlerException(string message, Exception inner)
            : base(message, inner)
        {
        }

        #endregion
    }

    class KinectHandler
    {
        #region Constants

        #endregion

        #region Private members

        // Kinect sensor objects
        private KinectSensor        m_KinectSensor     = null;
        private ColorFrameReader    m_ColorFrameReader = null;
        private InfraredFrameReader m_IRFrameReader    = null;
        private BodyFrameReader     m_BodyFrameReader  = null;

        // Log4net
        private static readonly log4net.ILog log = log4net.LogManager.GetLogger
     (System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        // Canvas
        private Rectangle m_canvasBounds = Rectangle.Empty;

        // Body tracking data
        private Body[] m_bodies              = null;
        private int    m_bodiesInSight       = 0;
        private bool   m_bodyDataRetrieved   = false;

        // Color data
        private bool   m_waitingForColorData = false;

        // Misc
        private long m_ticksAtInit = System.DateTime.Now.Ticks;
        private long m_ticksSinceInit
        {
            get
            {
                return System.DateTime.Now.Ticks - m_ticksAtInit;
            }
        }

        #endregion

        #region Properties

        public bool IsKinectAvailable
        {
            get
            {
                return (m_KinectSensor.IsAvailable);
            }
        }

        public bool IsWebcamAvailable
        {
            get
            {
                return false;
            }
        }

        public Rectangle CanvasBounds
        {
            get
            {
                if (m_canvasBounds == Rectangle.Empty)
                {
                    GetCanvasBounds();
                }
                return m_canvasBounds;
            }
        }

        public int BodiesInSight
        {
            get
            {
                while (!m_bodyDataRetrieved);
                return m_bodiesInSight;
            }
        }

        #endregion

        #region Constructor

        public KinectHandler()
        {
            // Get the sensor
            m_KinectSensor = KinectSensor.GetDefault();

            // Kinect data streams
            m_ColorFrameReader = m_KinectSensor.ColorFrameSource.OpenReader();
            // m_IRFrameReader = m_KinectSensor.InfraredFrameSource.OpenReader();
            m_BodyFrameReader = m_KinectSensor.BodyFrameSource.OpenReader();

            // Register handlers
            m_ColorFrameReader.FrameArrived += c_ColorFrameArrived;
            // m_IRFrameReader.FrameArrived += c_IRFrameArrived;
            m_BodyFrameReader.FrameArrived += c_BodyFrameArrived;
            m_KinectSensor.IsAvailableChanged += c_IsAvailableChanged;

            // Enable!
            m_KinectSensor.Open();
        }

        #endregion

        #region Public methods

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
            if (m_waitingForColorData)
            {

            }
            m_waitingForColorData = false;
        }

        void c_IRFrameArrived(object sender, InfraredFrameArrivedEventArgs evtArgs)
        {
            // Currently, do nothing. (TODO?)
        }

        void c_BodyFrameArrived(object sender, BodyFrameArrivedEventArgs evtArgs)
        {
            BodyFrame bodyFrame = evtArgs.FrameReference.AcquireFrame();
            bool dataRetrieved = false;

            if (bodyFrame != null)
            {
                if (m_bodies == null)
                {
                    m_bodies = new Body[bodyFrame.BodyCount];
                }
                bodyFrame.GetAndRefreshBodyData(m_bodies);
                dataRetrieved = true;
            }
            bodyFrame.Dispose();

            if (dataRetrieved)
            {
                m_bodiesInSight = 0;
                foreach (Body body in m_bodies)
                {
                    if (body.IsTracked)
                    {
                        m_bodiesInSight++;
                    }
                }
                log.Debug(String.Format("bodies in sight: {0}", m_bodiesInSight));
            }
            m_bodyDataRetrieved = true;
        }

        void c_IsAvailableChanged(object sender, IsAvailableChangedEventArgs evtArgs)
        {
            if (evtArgs.IsAvailable)
            {
                log.Info("Kinect is available.");
            }
            else
            {
                log.Warn("Kinect is unavailable.");
            }
        }

        #endregion

        #region Private methods

        private void GetCanvasBounds()
        {
            log.Info("Attempting to locate the canvas. (May wait for Kinect to become active.)");
            while (!IsKinectAvailable);
            if (BodiesInSight > 0)
            {
                log.Info("Please move out of the Kinect's line of sight.");
            }
            while (BodiesInSight > 0);

            m_waitingForColorData = true;
            while (m_waitingForColorData);

            log.Info("Color data has come through.");
        }

        #endregion
    }
}
