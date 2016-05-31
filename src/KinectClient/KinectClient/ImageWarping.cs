using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using MathNet.Numerics.LinearAlgebra;
using MoreLinq;

namespace MinorityReport
{
    public static class ImageWarping
    {
        public static Matrix<float> GetPerspectiveTransform(PointF[] src, PointF[] dst)
        {
            // Credit to OpenCV for the following algorithm...
            // https://github.com/Itseez/opencv/blob/f4e00bd60fd710ede010a37078cd6c2e6306688e/modules/imgproc/src/imgwarp.cpp#L6400

            // Calculates coefficients of perspective transformation
            // which maps (xi,yi) to (ui,vi), (i=1,2,3,4):
            //
            //      c00*xi + c01*yi + c02
            // ui = ---------------------
            //      c20*xi + c21*yi + c22
            //
            //      c10*xi + c11*yi + c12
            // vi = ---------------------
            //      c20*xi + c21*yi + c22
            //
            // Coefficients are calculated by solving linear system:
            // / x0 y0  1  0  0  0 -x0*u0 -y0*u0 \ /c00\ /u0\
            // | x1 y1  1  0  0  0 -x1*u1 -y1*u1 | |c01| |u1|
            // | x2 y2  1  0  0  0 -x2*u2 -y2*u2 | |c02| |u2|
            // | x3 y3  1  0  0  0 -x3*u3 -y3*u3 |.|c10|=|u3|,
            // |  0  0  0 x0 y0  1 -x0*v0 -y0*v0 | |c11| |v0|
            // |  0  0  0 x1 y1  1 -x1*v1 -y1*v1 | |c12| |v1|
            // |  0  0  0 x2 y2  1 -x2*v2 -y2*v2 | |c20| |v2|
            // \  0  0  0 x3 y3  1 -x3*v3 -y3*v3 / \c21/ \v3/
            //
            // or,
            // A . X = B,
            // in the code below;
            //
            // where:
            //   cij - matrix coefficients, c22 = 1

            if (src.Length != 4 || dst.Length != 4)
            {
                return null;
            }

            // Construct input matrix, input vector, and solution vector
            Matrix<float> A = CreateMatrix.Dense<float>(8, 8);
            Vector<float> B = CreateVector.Dense<float>(8);
            Vector<float> X;
            for (int i = 0; i < 4; ++i)
            {
                A[i, 0] = A[i + 4, 3] = src[i].X;
                A[i, 1] = A[i + 4, 4] = src[i].Y;
                A[i, 2] = A[i + 4, 5] = 1;
                A[i, 3] = A[i, 4] = A[i, 5] = A[i + 4, 0] = A[i + 4, 1] = A[i + 4, 2] = 0;
                A[i, 6] = -src[i].X * dst[i].X;
                A[i, 7] = -src[i].Y * dst[i].X;
                A[i + 4, 6] = -src[i].X * dst[i].Y;
                A[i + 4, 7] = -src[i].Y * dst[i].Y;

                B[i]     = dst[i].X;
                B[i + 4] = dst[i].Y;
            }

            // Solve for X
            X = A.Solve(B);

            // We have calculated the coefficients of the perspective matrix; now to construct the matrix.
            Matrix<float> M = CreateMatrix.Dense<float>(3, 3);
            for (int i = 0; i < 3; ++i)
            {
                for (int j = 0; (j < 3) && (i * 3 + j < 8); ++j)
                {
                    M[i, j] = X[i * 3 + j];
                }
            }
            // c22 = 1
            M[2, 2] = 1;

            return M;
        }

        public static PointF[] OrderPoints(PointF[] points)
        {
            // Thanks to Adrian Rosebrock for this algorithm.
            // http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
            if (points.Length != 4)
            {
                return null;
            }

            PointF[] ordered = new PointF[4];

            // The top-left point has the smallest sum; the bottom-right point has the largest sum.
            ordered[0] = points.MinBy(p => p.X + p.Y);
            ordered[2] = points.MaxBy(p => p.X + p.Y);

            // The top-right point has the largest (x - y); the bottom-left point has the smallest (x - y).
            ordered[1] = points.Select(p => new { Diff = p.X - p.Y, Point = p }).MaxBy(obj => obj.Diff).Point;
            ordered[3] = points.Select(p => new { Diff = p.X - p.Y, Point = p }).MinBy(obj => obj.Diff).Point;

            return ordered;
        }
    }
}
