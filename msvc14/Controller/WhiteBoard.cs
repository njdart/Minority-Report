using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Minority_Report
{
    class WhiteBoard
    {
        List<PostIt> postits;
        List<Arrow> arrows;
        Bitmap img;

        WhiteBoard()
        {

        }

        void AddPostIt(Point[] coords, Color color)
        {
            
        }
    }

    class PostIt
    {
        Point[] coords;
        Color color;
    }

    class Arrow
    {
        Point[] coords;
    }
}
