using NetworkPinger;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Simple.NetworkPinger
{
    public class Program
    {
        public static void Main(string[] args)
        {
            string[] phones = new string[]
            {
                "Kellys-iPhone",
                "Galaxy-S8"
            };
            
            NetworkMonitor monitor = new NetworkMonitor(phones);
            monitor.Initialize();


            Console.ReadKey();
        }
    }
}
