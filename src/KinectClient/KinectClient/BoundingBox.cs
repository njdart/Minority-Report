using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;

namespace MinorityReport
{
    class BoundingBox
    {
        #region Private member properties

        private PointF m_point1;
        private PointF m_point2;

        #endregion

        #region Properties

        /// <summary>
        /// Top-left point of the bounding box.
        /// </summary>
        public PointF TopLeft
        {
            get
            {
                PointF point = new PointF();
                point.X = (m_point1.X >= m_point2.X) ? m_point2.X : m_point1.X;
                point.Y = (m_point1.Y >= m_point2.Y) ? m_point2.Y : m_point1.Y;
                return point;
            }
        }

        /// <summary>
        /// Bottom-right point of the bounding box.
        /// </summary>
        public PointF BottomRight
        {
            get
            {
                PointF point = new PointF();
                point.X = (m_point1.X >= m_point2.X) ? m_point1.X : m_point2.X;
                point.Y = (m_point1.Y >= m_point2.Y) ? m_point1.Y : m_point2.Y;
                return point;
            }
        }

        /// <summary>
        /// Width of the bounding box.
        /// </summary>
        public float Width
        {
            get
            {
                return Math.Abs(m_point2.X - m_point1.X);
            }
        }

        /// <summary>
        /// Height of the bounding box.
        /// </summary>
        public float Height
        {
            get
            {
                return Math.Abs(m_point2.Y - m_point1.Y);
            }
        }

        #endregion

        #region Constructor

        /// <summary>
        /// Constructor for bounding box, specifying coordinates.
        /// </summary>
        /// <remarks>
        /// The bounding box is specified by using opposite (diagonal) points.
        /// </remarks>
        /// <param name="x1">X coordinate of point 1.</param>
        /// <param name="x2">X coordinate of point 2.</param>
        /// <param name="y1">Y coordinate of point 1.</param>
        /// <param name="y2">Y coordinate of point 2.</param>
        public BoundingBox(float x1, float x2, float y1, float y2)
        {
            m_point1 = new PointF(x1, y1);
            m_point2 = new PointF(x2, y2);
        }
        #endregion
    }
}
