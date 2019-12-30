using Emgu.CV;
using Emgu.CV.Structure;
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
using System.Drawing;

namespace InfraredKinectOpenCv
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private VideoCapture _capture = null;
        private CascadeClassifier _cascadeclassifier = null;
        private bool _captureInProgress;
        private Mat _frame;
        private Mat _grayFrame;
        private Mat _smallGrayFrame;
        private Mat _smoothedGrayFrame;
        private Mat _cannyFrame;
        Image<Gray, byte> gray = null;
        Image<Bgr, byte> capimageframe = null;

        public MainWindow()
        {
            InitializeComponent();
            Loaded += Form1_Load;
        }

        private void ProcessFrame(object sender, EventArgs e)
        {
            if (_capture != null && _capture.Ptr != IntPtr.Zero)
            {
                _capture.Retrieve(_frame, 0);
                using (Image<Bgr, byte> capimage = _frame.ToImage<Bgr, byte>())
                {
                    if (capimage != null)
                    {

                        gray = _frame.ToImage<Gray, Byte>();
                        _cascadeclassifier = new CascadeClassifier(@"haarcascade_frontalface_default.xml");
                        var faces = _cascadeclassifier.DetectMultiScale(gray, 1.1, 10, System.Drawing.Size.Empty);
                        foreach (var face in faces)
                        {
                            capimage.Draw(face, new Bgr(System.Drawing.Color.BurlyWood), 3);

                        }
                    }
                    //imageBox1.Image = capimage;

                }


            }

        }
        private void Form1_Load(object sender, EventArgs e)
        {
            CvInvoke.UseOpenCL = false;
            try
            {
                _capture = new VideoCapture();
                _capture.ImageGrabbed += ProcessFrame;
            }
            catch (NullReferenceException excpt)
            {
                MessageBox.Show(excpt.Message);
                throw;
            }

            _frame = new Mat();
            _grayFrame = new Mat();

            if (_capture != null)
            {
                if (_captureInProgress)
                {
                    _capture.Pause();
                }
                else
                {
                    _capture.Start();
                }

                _captureInProgress = !_captureInProgress;
            }

        }

    }
}




