using OpenWeatherMap;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace OpenWeatherConsole
{
    public class Program
    {
        public static void Main(string[] args)
        {
            //Int32.TryParse(APIKeys.BALTIMORE_CITY, out int baltimoreKey);
            //SingleResult<CurrentWeatherResult> currentWeather = CurrentWeather.GetByCityId(baltimoreKey);

            Int32.TryParse(APIKeys.BALTIMORE_CITY, out int baltimoreKey);
            OpenWeatherMapClient client = new OpenWeatherMapClient(APIKeys.OPEN_WEATHER_KEY);
            Task<CurrentWeatherResponse> getter = client.CurrentWeather.GetByCityId(baltimoreKey);
            getter.Wait(10000);
            CurrentWeatherResponse currentWeather = getter.Result;



            //using (HttpClient client = new HttpClient())
            //{
            //    var response = client.GetAsync(new Uri(String.Format("https://api.openweathermap.org/data/2.5/weather?id={0}&appid={1}", APIKeys.BALTIMORE_CITY, APIKeys.OPEN_WEATHER_KEY))).Result;
            //    Console.WriteLine($"Successful: {response.IsSuccessStatusCode}");

            //    Task<string> test = response.Content.ReadAsStringAsync();
            //    test.Wait();
            //    CurrentWeatherResult data = JsonConvert.DeserializeObject<CurrentWeatherResult>(test.Result);
            //}

            Console.ReadKey();
        }
    }
}
