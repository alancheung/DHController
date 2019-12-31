using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Common.Logging
{
    public class SmartLogger
    {
        public static void Log(string message)
        {
#if DEBUG
            Console.WriteLine(message);
#else
            string logFilePath = Path.Combine(Directory.GetCurrentDirectory(), "log.txt");
            StreamWriter sw = File.CreateText(logFilePath);
            sw.WriteLine(message);
            sw.Flush();
            sw.Close();
#endif

        }
    }
}
