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
            // connected = 5 minutes, disconnected = 30 seconds
            monitor.Initialize(5 * 60 * 1000, 30 * 1000);

            Console.ReadKey();
        }
    }
}
