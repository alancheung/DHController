using Common.Logging;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;
using System.Timers;

namespace NetworkPinger
{
    public class NetworkMonitor
    {
        /// <summary>
        /// All found devices on the network key'd by their host name.
        /// </summary>
        public Dictionary<string, NetworkDevice> NetworkDevices;
        public IEnumerable<NetworkDevice> ConnectedDevices => NetworkDevices.Where(d => d.Value.Connected == true).Select(valueSelector => valueSelector.Value);
        public IEnumerable<NetworkDevice> DisconnectedDevices => NetworkDevices.Where(d => d.Value.Connected == false).Select(valueSelector => valueSelector.Value);

        public NetworkMonitor(string[] hostNames)
        {
            NetworkDevices = new Dictionary<string, NetworkDevice>();

            foreach (string host in hostNames)
            {
                NetworkDevices.Add(host, new NetworkDevice(host, 3));
            }
        }

        public void Initialize()
        {
            // First attempt to connect to all devices specified.
            PingAllDevices();

            // 5 minute timer for connected devices
            Timer connectedTimer = new Timer(5 * 60 * 1000);
            connectedTimer.Elapsed += ConnectedTimer_Elapsed;
            connectedTimer.Enabled = true;
            connectedTimer.AutoReset = true;

            // 30 second timer for disconnected devices
            Timer disconnectedTimer = new Timer(30 * 1000);
            disconnectedTimer.Elapsed += DisconnectedTimer_Elapsed;
            disconnectedTimer.Enabled = true;
            disconnectedTimer.AutoReset = true;
        }

        public void PingDevice(string hostOrAddress)
        {
            Ping p = new Ping();
            p.PingCompleted += new PingCompletedEventHandler(OnPingCompleted);
            p.SendAsync(hostOrAddress, 1000, hostOrAddress);
        }

        public void PingAllDevices()
        {
            foreach (string host in NetworkDevices.Keys)
            {
                Ping p = new Ping();
                p.PingCompleted += new PingCompletedEventHandler(OnPingCompleted);
                p.SendAsync(host, 1000, host);
            }
        }

        private void OnPingCompleted(object sender, PingCompletedEventArgs e)
        {
            string hostName = (string)e.UserState;
            NetworkDevice device = NetworkDevices[hostName];

            if (e.Reply?.Status == IPStatus.Success)
            {
                IPAddress[] addresses;
                try
                {
                    addresses = Dns.GetHostAddresses(hostName);
                }
                catch (SocketException)
                {
                    addresses = null;
                }

                string addr = addresses == null ? "Exception Occurred" : string.Join(", ", addresses.Select(a => a.ToString()));
                device.IPAddress = addr;
                device.MarkAsConnected();
            }
            else
            {
                device.MarkAsDisconnected();
            }
        }

        private void ConnectedTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            foreach (NetworkDevice device in ConnectedDevices)
            {
                SmartLogger.Log($"Sending message to connected device." +
                    $"{Environment.NewLine}{device.ToString()}");

                PingDevice(device.HostName);
            }
        }

        private void DisconnectedTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            foreach (NetworkDevice device in DisconnectedDevices)
            {
                SmartLogger.Log($"Sending message to disconnected device." +
                    $"{Environment.NewLine}{device.ToString()}");

                PingDevice(device.HostName);
            }
        }
    }
}
