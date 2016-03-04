using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Minority_Report
{
    interface IStorage
    {
        // TODO define arguments for below function
        void OpenDataSource();
        WhiteBoard ReadWhiteBoard(Guid id);
        void WriteWhiteBoard(WhiteBoard wb);
    }
}
