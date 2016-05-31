using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Kinect;
using System.Windows.Media.Imaging;
using System.Windows.Media;
using System.Windows;
using System.IO;

namespace SensorTesting
{
    class SensorTesting
    {
        private KinectSensor sensor;
        private ColorFrameReader colorReader;
        private BodyIndexFrameReader bodyIndexReader;

        int numImagesCaptured;

        public SensorTesting()
        {
            Console.Write("Waiting on sensor...\n");

            sensor = KinectSensor.GetDefault();
            sensor.Open();

            colorReader = sensor.ColorFrameSource.OpenReader();
            bodyIndexReader = sensor.BodyIndexFrameSource.OpenReader();

            while (!sensor.IsAvailable) ;
            Console.Write("Sensor available.\n");

            while (true)
            {
                Console.Write("Enter to capture image: ");
                Console.ReadLine();
                CaptureImages();
            }
        }

        private void CaptureImages()
        {
            ColorFrame colorFrame = colorReader.AcquireLatestFrame();
            BodyIndexFrame bodyIndexFrame = bodyIndexReader.AcquireLatestFrame();

            if (colorFrame == null || bodyIndexFrame == null)
            {
                Console.Write("Null frame.\n");
            }

            byte[] pixels = new byte[colorFrame.FrameDescription.Width * colorFrame.FrameDescription.Height * 4];
            colorFrame.CopyConvertedFrameDataToArray(pixels, ColorImageFormat.Bgra);

            // Create a bitmap structure to hold data
            WriteableBitmap bmp = new WriteableBitmap(colorFrame.FrameDescription.Width,
                                                           colorFrame.FrameDescription.Height,
                                                           96.0, 96.0,
                                                           PixelFormats.Bgr32,
                                                           null);

            // Write data into a bitmap structure
            using (KinectBuffer buf = colorFrame.LockRawImageBuffer())
            {
                bmp.Lock();
                colorFrame.CopyConvertedFrameDataToIntPtr(bmp.BackBuffer,
                                                     (uint)colorFrame.FrameDescription.LengthInPixels * 4,
                                                     ColorImageFormat.Bgra);
                bmp.AddDirtyRect(new Int32Rect(0, 0, bmp.PixelHeight, bmp.PixelHeight));
                bmp.Unlock();
            }

            // Encode the data into a BMP file format
            PngBitmapEncoder encoder = new PngBitmapEncoder();
            encoder.Frames.Add(BitmapFrame.Create(bmp));

            using (MemoryStream stream = new MemoryStream())
            {
                encoder.Save(stream);
                byte[] latestColorPNG = stream.ToArray();
            }



            if (colorFrame != null) colorFrame.Dispose();
            if (bodyIndexFrame != null) bodyIndexFrame.Dispose();
        }

    }
}
