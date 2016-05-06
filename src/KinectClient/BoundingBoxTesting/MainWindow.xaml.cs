using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using MinorityReport;

namespace BoundingBoxTesting
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private KinectClient kinectClient = null;

        private DrawingGroup drawingGrp;
        private DrawingImage drawingImg;

        public ImageSource ImageSource
        {
            get
            {
                return drawingImg;
            }
        }

        public MainWindow()
        {
            this.kinectClient = new KinectClient("server", 8088);
            this.kinectClient.BoundingBoxesSampled += KinectClient_BoundingBoxesSampled;
            this.kinectClient.BeginSampling();

            InitializeComponent();

            this.drawingGrp = new DrawingGroup();
            this.drawingImg = new DrawingImage(this.drawingGrp);
            this.mainCanvas.DataContext = this;
        }

        private void KinectClient_BoundingBoxesSampled(object sender, BoundingBoxesEventArgs e)
        {
            this.Dispatcher.Invoke((Action)(() =>
            {
                using (DrawingContext dc = this.drawingGrp.Open())
                {
                    dc.DrawRectangle(Brushes.White, null, new Rect(new Size(512.0, 424.0)));

                    foreach (BodyBoundingBox box in e.BoundingBoxes.Where(x => x != null))
                    {
                        Rect r = new Rect(box.topLeft, box.bottomRight);
                        dc.DrawRectangle(Brushes.Blue, null, r);
                    }
                }
            }));
        }
    }
}
