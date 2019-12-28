using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PiLightController.LIFX
{
    public class CommandResponse
    {
        public bool Successful { get; }

        public CommandResponse(bool successful)
        {
            Successful = successful;
        }

        public static CommandResponse Failed()
        {
            return new CommandResponse(false);
        }
    }

    public class CommandResponse<T> : CommandResponse
    {
        public T Response { get; }

        public CommandResponse(bool successful, T response) : base(successful)
        {
            Response = response;
        }

        public new static CommandResponse<T> Failed()
        {
            return new CommandResponse<T>(false, default(T));
        }
    }
}
