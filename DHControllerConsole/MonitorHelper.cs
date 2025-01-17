﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace DHControllerConsole
{
    public static class MonitorHelper
    {
        [DllImport("user32.dll")]
        public static extern int SendMessage(int hWnd, int Msg, int wParam, int lParam);

        [DllImport("user32", EntryPoint = "PostMessage")]
        public static extern int PostMessageA(int hwnd, int wMsg, int wParam, int lParam);

        public static void TurnOn()
        {
            // SendMessage(-1, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_ON);

            // PostMessage used as it does not wait on windows to respond.
            PostMessageA(-1, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_ON);
        }

        public static void TurnOff()
        {
            SendMessage(-1, WM_SYSCOMMAND, SC_MONITORPOWER, MONITOR_OFF);
        }

        const int SC_MONITORPOWER = 0xF170;
        const int WM_SYSCOMMAND = 0x0112;
        const int MONITOR_ON = -1;
        const int MONITOR_OFF = 2;
    }
}
