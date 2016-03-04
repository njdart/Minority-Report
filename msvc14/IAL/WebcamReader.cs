using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Emgu.CV;
using Emgu.CV.VideoStab;

namespace MinorityReport
{
    class WebcamReader
    {
        private Capture            m_Capture;
        private CaptureFrameSource m_CaptureFrameSource;

        public WebcamReader()
        {
            m_Capture = new Capture(0);
            m_CaptureFrameSource = new CaptureFrameSource(m_Capture);
        }

        public Mat GetImage()
        {
            Mat matFrame = m_CaptureFrameSource.NextFrame();
            return matFrame;
        }
    }
}
