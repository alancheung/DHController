using LifxLan.LIFX;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SimpleLifxLanConsole
{
    public class Program
    {
        public static void Main(string[] args)
        {
            if (!Int32.TryParse(ConfigurationManager.AppSettings["NUM_LIGHTS"], out int numLights) ||
                !Int32.TryParse(ConfigurationManager.AppSettings["DISCOVERY_TIMEOUT_MS"], out int discoveryTimeoutMs) ||
                !Int32.TryParse(ConfigurationManager.AppSettings["COMMAND_DELAY_MS"], out int commandDelayMs) ||
                !Int32.TryParse(ConfigurationManager.AppSettings["COMMAND_TIMEOUT_MS"], out int commandTimeoutMs))
            {
                throw new ArgumentException("Application settings invalid!");
            }

            Console.WriteLine($"Connecting with {numLights} lights...");

            LightManager lifx = new LightManager(numLights,
                TimeSpan.FromMilliseconds(discoveryTimeoutMs),
                TimeSpan.FromMilliseconds(commandDelayMs),
                TimeSpan.FromMilliseconds(commandTimeoutMs));

            Console.WriteLine(lifx.ToString());
            Console.WriteLine("Connected!");
            Console.ReadKey();

            bool commandSent = lifx.TurnOff(TimeSpan.Zero, lifx.LightAndStates.Keys.ToArray());
            Console.WriteLine(commandSent);
            Console.ReadKey();
        }
    }
}
