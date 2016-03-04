using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Drawing;
using System.Drawing.Imaging;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using Emgu.CV;

namespace Minority_Report
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void button_Click(object sender, RoutedEventArgs e)
        {
            List<PostIt> p = ImageProcessor.extractPostIts();
            Bitmap b = setImage();
        }

        public Bitmap setImage()
        {
            Mat test = CvInvoke.Imread("postits1.jpg", Emgu.CV.CvEnum.LoadImageType.AnyColor);
            Bitmap img = test.Bitmap;
            using(MemoryStream memory = new MemoryStream())
            {
                img.Save(memory, ImageFormat.Bmp);
                memory.Position = 0;
                BitmapImage b = new BitmapImage();
                b.BeginInit();
                b.StreamSource = memory;
                b.CacheOption = BitmapCacheOption.OnLoad;
                b.EndInit();
                image.Source = b;
            }
            return img;
        }
    }
}
