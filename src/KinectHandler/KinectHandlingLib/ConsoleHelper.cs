using System.Runtime.InteropServices;
using System.Security;

namespace MinorityReportApp
{
    /// <summary>
    /// ConsoleHelper class found at http://stackoverflow.com/a/1953442
    /// </summary>
    public class ConsoleHelper
    {
        public static int Create()
        {
            if (AllocConsole())
                return 0;
            else
                return Marshal.GetLastWin32Error();
        }

        public static int Destroy()
        {
            if (FreeConsole())
                return 0;
            else
                return Marshal.GetLastWin32Error();
        }

        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Security", "CA2118:ReviewSuppressUnmanagedCodeSecurityUsage"), SuppressUnmanagedCodeSecurity]
        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        static extern bool AllocConsole();


        [System.Diagnostics.CodeAnalysis.SuppressMessage("Microsoft.Security", "CA2118:ReviewSuppressUnmanagedCodeSecurityUsage"), SuppressUnmanagedCodeSecurity]
        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        static extern bool FreeConsole();
    }
}