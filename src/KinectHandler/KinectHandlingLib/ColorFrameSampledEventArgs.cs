using System.Windows.Media.Imaging;

namespace MinorityReport
{
    public class ColorFrameSampledEventArgs
    {
        public WriteableBitmap bitmap { get; }

        public ColorFrameSampledEventArgs(WriteableBitmap bitmap)
        {
            this.bitmap = bitmap;
        }
    }
}