using LifxLan.LIFX;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
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

namespace DHClient
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        LightManager manager;

        public MainWindow()
        {
            InitializeComponent();

            Loaded += MainWindow_Loaded;

            this.Status.Content = "Running";
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            
        }

        private void OfficeOneClick(object sender, RoutedEventArgs e)
        {
            string[] officeLights = new string[3]
            {
                "Office One", "Office Two", "Office Three"
            };

            manager = new LightManager(7,
                TimeSpan.FromMilliseconds(30000),
                TimeSpan.FromMilliseconds(200),
                TimeSpan.FromMilliseconds(1000));

            this.Status.Content = "Setting brightness to 100%";
            manager.SetBrightness(1.0, TimeSpan.FromSeconds(10), officeLights);
            Thread.Sleep(10000);

            this.Status.Content = "Turning off lights";
            manager.TurnOff(TimeSpan.FromSeconds(10), officeLights);
            Thread.Sleep(10000);

            this.Status.Content = "Setting brightness to 50%";
            manager.SetBrightness(0.5, TimeSpan.FromSeconds(0), officeLights);

            this.Status.Content = "Turning on lights";
            manager.TurnOn(TimeSpan.FromSeconds(10), officeLights);
            Thread.Sleep(10000);

        }
    }
}
