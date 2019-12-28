using LifxNet;
using System;

namespace LifxLan.LIFX
{
    public class LightAndState
    {
        public LightBulb Light { get; set; }

        public LightStateResponse State { get; set; }

        public bool IsConnected { get; set; }

        public DateTime LastCommandDateTime { get; set; }

        public LightAndState(LightBulb light, LightStateResponse state)
        {
            Light = light;
            State = state;
            IsConnected = true;
            LastCommandDateTime = DateTime.Now;
        }

        public void Update(bool connected, LightStateResponse newState)
        {
            IsConnected = connected;
            LastCommandDateTime = DateTime.Now;
            if (newState != null)
            {
                State = newState;
            }
        }
    }
}
