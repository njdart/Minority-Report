using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Emgu.CV;

namespace Minority_Report
{
    public class WhiteBoard
    {
        public List<PostIt> postits;
        public List<Line> arrows;
        public Bitmap img;

        WhiteBoard()
        {

        }

        void AddPostIt(Point[] coords, Color color)
        {
            
        }
    }

    public struct PostIt
    {
        public Point[] coords;
        public Color color;
        public Mat image;
    }

    public struct Line
    {
        public Point[] coords;
    }
}
