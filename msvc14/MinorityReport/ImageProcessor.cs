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
        private KinectSensor        m_KinectSensor;
        private ColorFrameReader    m_ColorFrameReader;
        private InfraredFrameReader m_IRFrameReader;
        private BodyFrameReader     m_BodyFrameReader;

        // Our webcam handling class
        private WebcamReader        m_WebcamReader;

        #endregion

        #region Properties

        public bool KinectAvailable
        {
            get
            {
                return m_KinectSensor.IsOpen && m_KinectSensor.IsAvailable;
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
            if (!m_KinectSensor.IsOpen || !m_KinectSensor.IsAvailable)
            {
                throw new ImageProcessorException();
            }
            
            // Kinect data streams
            m_ColorFrameReader = m_KinectSensor.ColorFrameSource.OpenReader();
            m_IRFrameReader = m_KinectSensor.InfraredFrameSource.OpenReader();
            m_BodyFrameReader = m_KinectSensor.BodyFrameSource.OpenReader();

            // Register frame-arrived handler
            m_ColorFrameReader.FrameArrived += c_FrameArrived;
            m_IRFrameReader.FrameArrived += c_FrameArrived;
            m_BodyFrameReader.FrameArrived += c_FrameArrived;
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

        void c_FrameArrived(object sender, EventArgs evtArgs)
        {
            if (sender == m_BodyFrameReader)
            {
                // We have received body data. Determine whether a high-resolution image should be taken.
                BodyFrameArrivedEventArgs data = (BodyFrameArrivedEventArgs)evtArgs;
                BodyFrame frame = data.FrameReference.AcquireFrame();
                List<Body> bodies = new List<Body>(frame.BodyCount);
                frame.GetAndRefreshBodyData(bodies);

                foreach (Body body in bodies)
                {
                    // TODO: Do something useful
                }

            }
        }

        #endregion
    }
}
