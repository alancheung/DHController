using Common.Logging;
using System;

namespace NetworkPinger
{
    public class NetworkDevice
    {
        /// <summary>
        /// Maximum number of connection attempts before the device is connected disconnected.
        /// </summary>
        private int _maxConnectionAttempts;

        public string HostName { get; set; }

        public string IPAddress { get; set; }

        /// <summary>
        /// Is the device connected?
        /// </summary>
        public bool Connected
        {
            get
            {
                return Attempts <= _maxConnectionAttempts;
            }
        }

        /// <summary>
        /// <see cref="DateTime"/> of the last successful ping.
        /// </summary>
        public DateTime LastConnectedTime { get; set; }

        /// <summary>
        /// Number of attempts since the device was seen.
        /// </summary>
        public int Attempts { get; set; }

        public NetworkDevice(string hostName, int connectionAttemptsBeforeDisconnect)
        {
            _maxConnectionAttempts = connectionAttemptsBeforeDisconnect;

            HostName = hostName;
            LastConnectedTime = DateTime.MinValue;
            Attempts = 0;
        }

        public void MarkAsConnected()
        {
            LastConnectedTime = DateTime.Now;
            Attempts = 0;

            SmartLogger.Log($"Marking device {HostName} as connected.");
        }

        public void MarkAsDisconnected()
        {
            ++Attempts;

            SmartLogger.Log($"Marking device {HostName} as {(Connected ? "still connected" : "disconnected")} with {Attempts} attempts.");
        }

        public override string ToString()
        {
            return $"{nameof(HostName)}: {HostName}" + Environment.NewLine 
                + $"{nameof(IPAddress)}: {IPAddress}" + Environment.NewLine
                + $"{nameof(Connected)}: {Connected}" + Environment.NewLine
                + $"{nameof(LastConnectedTime)}: {LastConnectedTime}" + Environment.NewLine
                + $"{nameof(Attempts)}: {Attempts}" + Environment.NewLine;
        }
    }
}