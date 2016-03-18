using System.Collections.Generic;

namespace Minority_Report
{
    public class DirectedGraph
    {
        public IList<PostIt> PostIts;
        public IList<Line> Lines;

        public DirectedGraph(IList<PostIt> postIts, IList<Line> lines)
        {
            PostIts = postIts;
            Lines = lines;
        }

        public DirectedGraph()
        {
            PostIts = new List<PostIt>();
            Lines = new List<Line>();
        }
    }
}