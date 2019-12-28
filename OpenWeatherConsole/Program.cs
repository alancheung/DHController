using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace OpenWeatherConsole
{
    class Program
    {
        public static void Main(string[] args)
        {
            object untrackedConfiguration = ConfigurationManager.AppSettings;

            //using (HttpClient client = new HttpClient())
            //{
            //    var response = client.GetAsync(new Uri(String.Format("https://api.openweathermap.org/data/2.5/weather?id={0}&appid={1}", BALTIMORE, KEY))).Result;
            //    Console.WriteLine($"Successful: {response.IsSuccessStatusCode}");

            //    Task<string> test = response.Content.ReadAsStringAsync();
            //    test.Wait();
            //    dynamic data = JsonConvert.DeserializeObject<dynamic>(test.Result);
            //}

            Console.ReadKey();
        }
    }
}
