using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;

namespace DHCService
{
    public partial class DHCService : ServiceBase
    {
        public DHCService()
        {
            InitializeComponent();
        }

        public void DebugStart(string[] args)
        {
            OnStart(args);
            Console.Read();
            OnStop();
        }

        protected override void OnStart(string[] args)
        {
        }

        protected override void OnStop()
        {

        }
    }
}
