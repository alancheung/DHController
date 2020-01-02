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

        public void Initialize(double connectedPingTimeMs, double disconnectedPingTimeMs)
        {
            // First attempt to connect to all devices specified.
            PingAllDevices();

            Timer connectedTimer = new Timer(connectedPingTimeMs);
            connectedTimer.Elapsed += ConnectedTimer_Elapsed;
            connectedTimer.Enabled = true;
            connectedTimer.AutoReset = true;

            Timer disconnectedTimer = new Timer(disconnectedPingTimeMs);
            disconnectedTimer.Elapsed += DisconnectedTimer_Elapsed;
            disconnectedTimer.Enabled = true;
            disconnectedTimer.AutoReset = true;
        }

        private void ConnectedTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            foreach (NetworkDevice device in ConnectedDevices)
            {
                SmartLogger.Log($"Sending message to connected device:" +
                    $"{Environment.NewLine}{device.ToString()}");

                PingDevice(device.HostName);
            }
        }

        private void DisconnectedTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            foreach (NetworkDevice device in DisconnectedDevices)
            {
                SmartLogger.Log($"Sending message to disconnected device:" +
                    $"{Environment.NewLine}{device.ToString()}");

                PingDevice(device.HostName);
            }
        }

        /// <summary>
        /// Ping all known devices.
        /// </summary>
        public void PingAllDevices()
        {
            foreach (string host in NetworkDevices.Keys)
            {
                PingDevice(host);
            }
        }

        /// <summary>
        /// Ping a single device with a given host name or IP address. The address must be known.
        /// </summary>
        /// <param name="hostName"></param>
        private void PingDevice(string hostName)
        {
            Ping p = new Ping();
            p.PingCompleted += new PingCompletedEventHandler(OnPingCompleted);
            p.SendAsync(hostName, 1000, hostName);
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
    }
}
