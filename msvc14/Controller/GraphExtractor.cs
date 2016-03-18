using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using Emgu.CV;
using Emgu.CV.CvEnum;
using Emgu.CV.Util;
using Emgu.CV.Structure;

namespace Minority_Report
{
    public class GraphExtractor
    {
        #region Private members

        private bool             m_debugPlot;
        private Mat              m_image;
        private Mat              m_rawImage;
        private IList<Rectangle> m_postitPos;
        private IList<Mat>       m_postitImage;
        private IList<Color>     m_postitColour;
        // private IList<...> m_lineEnds;

        private IList<ColourThresholds> m_colourThresholds;

        #endregion

        #region Constructor

        public GraphExtractor(Mat image)
        {
            m_debugPlot = false;
            m_rawImage = image;
            m_image = image;
            m_postitPos = new List<Rectangle>();
            m_postitImage = new List<Mat>();
            m_postitColour = new List<Color>();

            m_colourThresholds = new List<ColourThresholds>()
            {
                new ColourThresholds("ORANGE",
                                     0,
                                     70,
                                     60,
                                     150,
                                     25,
                                     100),
                new ColourThresholds("YELLOW",
                                     -30,
                                     15,
                                     35,
                                     120,
                                     40,
                                     125),
                new ColourThresholds("BLUE",
                                     -80,
                                     -20,
                                     -120,
                                     -40,
                                     -45,
                                     0),
                new ColourThresholds("MAGENTA",
                                     40,
                                     135,
                                     25,
                                     90,
                                     -55,
                                     -10),
            };
        }

        #endregion

        #region Public methods

        public DirectedGraph ExtractGraph(bool   showDebug       = false,
                                          double sigma           = 0.8,
                                          int    minPostitArea   = 3000,
                                          int    maxPostitArea   = 20000,
                                          double lenTolerance    = 0.15,
                                          int    minColourThresh = 64,
                                          int    maxColourThresh = 200)
        {
            //this.Display(m_image);

            IList<PostIt> postits = this.ExtractPostits(showDebug,
                                                       sigma,
                                                       minPostitArea,
                                                       maxPostitArea,
                                                       lenTolerance,
                                                       minColourThresh,
                                                       maxColourThresh);

            IList<Line> lines = this.ExtractLines(postits, showDebug);

            return new DirectedGraph(postits, lines);
        }

        #endregion

        #region Private methods

        private IList<PostIt> ExtractPostits(bool showDebug,
                                             double sigma,
                                             int minPostitArea,
                                             int maxPostitArea,
                                             double lenTolerance,
                                             int minColourThresh,
                                             int maxColourThresh)
        {
            IList<PostIt> foundPostits = new List<PostIt>();
            Mat img = m_image.Clone();
            Mat boxedImg = m_image.Clone();
            Mat edgeGray = this.EdgeDetect(img, false);

            VectorOfVectorOfPoint contours = new VectorOfVectorOfPoint();

            CvInvoke.FindContours(edgeGray.Clone(), contours, null,
                                  RetrType.External,
                                  ChainApproxMethod.ChainApproxNone);

            for (int i = 0; i < contours.Size; i++)
            {
                VectorOfPoint contour = contours[i];
                PointF[] box = CvInvoke.BoxPoints(CvInvoke.MinAreaRect(contour));
                PointF[][] boxes = { box };
                VectorOfVectorOfPointF boxVecVec = new VectorOfVectorOfPointF(boxes);
                CvInvoke.DrawContours(boxedImg,
                                      boxVecVec,
                                      -1,
                                      new MCvScalar(0, 255, 0),
                                      3);

                this.Display(boxedImg);
            }
            return foundPostits;
        }

        private IList<Line> ExtractLines(IList<PostIt> postits, bool showDebug)
        {
            //throw new NotImplementedException();
            return new List<Line>();
        }

        private Mat EdgeDetect(Mat img, bool line)
        {
            Mat imgOut = img.Clone();

            CvInvoke.MedianBlur(imgOut, imgOut, 9);
            //this.Display(imgOut);

            if (!line)
            {
                CvInvoke.Threshold(imgOut, imgOut, 90, 255, ThresholdType.Binary);
                this.Display(imgOut);
            }

            CvInvoke.CvtColor(imgOut, imgOut, ColorConversion.Rgb2Gray);
            this.Display(imgOut);

            CvInvoke.Canny(imgOut, imgOut, 1, 30);
            this.Display(imgOut);

            return imgOut;
        }

        private void Display(Mat img)
        {
            Mat imgDisplay = new Mat();
            CvInvoke.Resize(img, imgDisplay, new Size(0, 0), 0.3, 0.3, Inter.Area);
            CvInvoke.Imshow("Image", imgDisplay);
            CvInvoke.WaitKey(0);
        }

        #endregion
    }
}
