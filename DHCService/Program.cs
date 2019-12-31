using System;
using System.Collections.Generic;
using System.Linq;
using System.ServiceProcess;
using System.Text;
using System.Threading.Tasks;

namespace DHCService
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        public static void Main(string[] args)
        {
            if (Environment.UserInteractive)
            {
                DHCService service = new DHCService();
                service.DebugStart(args);
            }
            else
            {
                ServiceBase.Run(new ServiceBase[]
                {
                    new DHCService()
                });
            }
        }


    }
}
