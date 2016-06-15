using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    class CalibratePOSTData
    {
        [JsonProperty( NullValueHandling = NullValueHandling.Ignore )]
        public IList<IList<float>> points;

        public string instanceID;
    }
}
