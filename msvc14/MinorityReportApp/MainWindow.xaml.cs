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
using Minority_Report;

namespace MinorityReportApp
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private bool m_started;

        public MainWindow()
        {
            m_started = false;
            InitializeComponent();
        }

        private void button_Click(object sender, RoutedEventArgs e)
        {
            if (!m_started)
            {
                m_started = true;
                if (ConsoleHelper.Create() != 0)
                {
                    log.Error("Failed to allocate console!");
                    this.Close();
                    return;
                }
                log.Info("GO button clicked. Executing a test.");

                GraphExtractorTest.Execute();
            }
        }

        private static readonly log4net.ILog log = log4net.LogManager.GetLogger
   (System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);
    }
}
