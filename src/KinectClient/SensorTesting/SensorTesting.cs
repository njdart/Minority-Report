using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Kinect;

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
            while (!sensor.IsAvailable) ;

            Console.Write("Sensor available.\n");

            colorReader = sensor.ColorFrameSource.OpenReader();
            bodyIndexReader = sensor.BodyIndexFrameSource.OpenReader();

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
        }
    }
}
