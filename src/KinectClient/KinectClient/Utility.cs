using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MinorityReport
{
    public static class Utility
    {
        /// <summary>
        /// Populates an array with a value.
        /// </summary>
        /// <typeparam name="T">Type of values stored in array</typeparam>
        /// <param name="arr">Array to populate</param>
        /// <param name="value">Value to populate array with</param>
        public static void PopulateArray<T>(this T[] arr, T value)
        {
            for (int i = 0; i < arr.Length; ++i)
            {
                arr[i] = value;
            }
        }
    }
}
