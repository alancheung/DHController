using LifxNet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace LifxLan.LIFX
{
    public class ColorProperty
    {
        public ushort Hue { get; set; }
        public ushort Saturation { get; set; }
        public ushort Kelvin { get; set; }

        public static ColorProperty CreateFromKnownColor(System.Drawing.Color systemColor)
        {
            return new ColorProperty()
            {
                Hue = Convert.ToUInt16(systemColor.GetHue()),
                Saturation = Convert.ToUInt16(systemColor.GetSaturation()),
                Kelvin = Convert.ToUInt16(systemColor.GetBrightness()),
            };
        }

        public static ColorProperty CreateFromLifxState(LightStateResponse lifxColor)
        {
            return new ColorProperty()
            {
                Hue = lifxColor.Hue,
                Saturation = lifxColor.Saturation,
                Kelvin = lifxColor.Kelvin,
            };
        }

        public static ushort GetBrightness(double percent)
        {
            return Convert.ToUInt16(UInt16.MaxValue * percent);
        }
    }
}
