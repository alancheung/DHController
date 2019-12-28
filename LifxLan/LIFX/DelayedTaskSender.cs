using LifxNet;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace PiLightController.LIFX
{
    public class DelayedTaskSender
    {
        private TimeSpan _timeout { get; }
        private TimeSpan _delay { get; }

        private DateTime _lastSentCommand { get; set; }

        public DelayedTaskSender(TimeSpan delay, TimeSpan timeout)
        {
            _delay = delay;
            _timeout = timeout;
        }

        public async Task<CommandResponse> SendCommand(Task command)
        {
            await Task.WhenAny(command, Task.Delay(_timeout));
            Thread.Sleep(_delay);

            return new CommandResponse(command.IsCompleted);
        }

        public async Task<CommandResponse<TResult>> SendCommand<TResult>(Task<TResult> command)
        {
            await Task.WhenAny(command, Task.Delay(_timeout));
            Thread.Sleep(_delay);

            return command.IsCompleted ? new CommandResponse<TResult>(true, command.Result) : CommandResponse<TResult>.Failed();
        }
    }
}
