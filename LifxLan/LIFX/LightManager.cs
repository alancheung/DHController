using LifxNet;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace LifxLan.LIFX
{
    public class LightManager
    {
        public static readonly TimeSpan COMMAND_DELAY = TimeSpan.FromMilliseconds(5);
        public static readonly TimeSpan COMMAND_TIMEOUT = TimeSpan.FromSeconds(10);
        public static readonly TimeSpan DISCOVERY_TIMEOUT = TimeSpan.FromSeconds(20);

        public LifxClient Client { get; private set; }

        public Dictionary<string, LightAndState> LightAndStates { get; }
        public List<LightBulb> Lights => LightAndStates.Select(l => l.Value.Light).ToList();

        public DelayedTaskSender CommandHandler { get; }

        public LightManager(int numLights)
        {
            LightAndStates = new Dictionary<string, LightAndState>();
            CommandHandler = new DelayedTaskSender(COMMAND_DELAY, COMMAND_TIMEOUT);

            if (numLights > 0 && !Initialize(numLights))
            {
                throw new TimeoutException("Did not discover all lights within timeout!");
            }
        }

        private bool Initialize(int numLightsExpected)
        {
            Stopwatch sw = new Stopwatch();
            sw.Start();

            // Create the client
            Task<LifxClient> createTask = LifxClient.CreateAsync();
            createTask.Wait(DISCOVERY_TIMEOUT);
            Client = createTask.Result;

            // Discover all bulbs
            bool allLightsDiscoverd = false;
            Client.DeviceDiscovered += RegisterLight;
            Client.DeviceLost += UnregisterLight;
            Client.StartDeviceDiscovery();

            // Loop until all devices are discovered or timeout reached.
            do
            {
                allLightsDiscoverd = LightAndStates.Count == numLightsExpected;
                if (!allLightsDiscoverd)
                {
                    Thread.Sleep(250);
                }
                else
                {
                    Client.StopDeviceDiscovery();
                    break;
                }
            } while (sw.Elapsed < DISCOVERY_TIMEOUT);

            return allLightsDiscoverd;
        }

        public async void RegisterLight(object sender, LifxClient.DeviceDiscoveryEventArgs args)
        {
            if (args.Device is LightBulb light)
            {
                LightStateResponse state = await Client.GetLightStateAsync(light);
                LightAndStates.Add(state.Label, new LightAndState(light, state));
            }
        }

        public void UnregisterLight(object sender, LifxClient.DeviceDiscoveryEventArgs args)
        {
            if (args.Device is LightBulb light)
            {
                LightAndState registeredLight = LightAndStates.FirstOrDefault(l => l.Value.Light.HostName == light.HostName).Value;
                if (registeredLight != null)
                {
                    registeredLight.IsConnected = false;
                }
            }
        }

        public async void Ping()
        {
            Dictionary<string, Task<CommandResponse<LightStateResponse>>> statusCheckTasks = new Dictionary<string, Task<CommandResponse<LightStateResponse>>>();
            foreach (var kv in LightAndStates)
            {
                statusCheckTasks.Add(kv.Key, CommandHandler.SendCommand(Client.GetLightStateAsync(kv.Value.Light)));
            }

            await Task.WhenAll(statusCheckTasks.Values);

            foreach (var taskKV in statusCheckTasks)
            {
                CommandResponse<LightStateResponse> response = taskKV.Value.Result;
                LightAndStates[taskKV.Key].Update(response.Successful, response.Response);
            }
        }

        public Task[] SetColor(ColorProperty color, double brightness, TimeSpan transition, params LightBulb[] lights)
        {
            return lights
                .Select(l => Client.SetColorAsync(l, color.Hue, color.Saturation, ColorProperty.GetBrightness(brightness), color.Kelvin, transition))
                .ToArray();
        }

        public override string ToString()
        {
            StringBuilder builder = new StringBuilder();
            builder.AppendLine($"Current registered lights ({LightAndStates.Keys.Count})");
            foreach (var light in LightAndStates)
            {
                LightAndState state = light.Value;
                builder.AppendLine($"[{(state.IsConnected ? "C" : "D")}] {light.Key} ({state.Light.MacAddressName}@{state.Light.HostName}:{state.Light.Port})");
                builder.AppendLine($"\tPower: {state.State.IsOn}\n\tHue: {state.State.Hue}\n\tSaturation: {state.State.Saturation}\n\tBrightness: {state.State.Brightness}\n\tTemperature: {state.State.Kelvin}");
            }

            return builder.ToString();
        }
    }
}
