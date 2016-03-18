using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Net.Http;

namespace MinorityReport
{
    public class KinectClient
    {
        private const string HTTP_VERB_BODIES = "BODIES";
        private const string HTTP_VERB_GESTURE = "GESTURE";

        private const int POLL_INTERVAL_MS = 500;

        private string m_server_host;
        private int    m_server_port;

        private static readonly log4net.ILog log = log4net.LogManager.GetLogger
     (System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        private bool m_init_successful;

        private KinectHandler m_kinectHandler;
        private HttpClient    m_httpClient;

        private HttpMethod m_bodiesMethod = new HttpMethod(HTTP_VERB_BODIES);
        private HttpMethod m_gestureMethod = new HttpMethod(HTTP_VERB_GESTURE);

        public bool InitSuccessful
        {
            get
            {
                return m_init_successful;
            }
        }

        private bool ParseArgs(string[] args)
        {
            foreach (string arg in args)
            {
                if ((arg.Substring(0, 7) == "--host=") &&
                    (arg.Length > 7))
                {
                    if (m_server_host != "")
                    {
                        log.Error("Host cannot be specified more than once.");
                        return false;
                    }
                    m_server_host = arg.Substring(7);
                }

                else if ((arg.Substring(0, 7) == "--port=") &&
                         (arg.Length > 7))
                {
                    if (m_server_port != -1)
                    {
                        log.Error("Port cannot be specified more than once.");
                        return false;
                    }
                    try
                    {
                        m_server_port = Int32.Parse(arg.Substring(7));
                    }
                    catch (Exception ex)
                    {
                        if (ex is FormatException || ex is OverflowException)
                        {
                            log.Error("Invalid port specified.");
                            return false;
                        }
                        throw;
                    }
                    if (m_server_port < 0)
                    {
                        log.Error("Invalid port specified.");
                        return false;
                    }
                }

                else
                {
                    log.WarnFormat("Arg '{0}' unrecognised.", arg);
                }
            }

            bool retval = true;
            if (m_server_host == "")
            {
                log.Error("No server host specified.");
                retval = false;
            }
            if (m_server_port == -1)
            {
                log.Error("No server port specified.");
                retval = false;
            }
            return retval;
        }

        public KinectClient(string[] args)
        {
            m_init_successful = false;

            m_server_host = "";
            m_server_port = -1;

            log.Info("Starting the Kinect handler...");
            m_kinectHandler = new KinectHandler();

            log.Info("Initialising the HTTP client...");
            m_httpClient = new HttpClient();

            m_init_successful = ParseArgs(args);

            if (InitSuccessful)
            {
                log.Info("Checking the server is alive...");
                Task<bool> alive = PollServerAlive();
                alive.Wait();
                if (!alive.Result)
                {
                    log.Fatal("The server isn't alive! Cannot continue.");
                    m_init_successful = false;
                }
            }
        }

        public async Task MainLoop()
        {
            if (!InitSuccessful)
            {
                return;
            }

            bool alive = true;
            while (alive)
            {
                alive = await PollServerAlive();
                Thread.Sleep(POLL_INTERVAL_MS);
            }
        }

        private async Task<bool> PollServerAlive()
        {
            string uriStr = string.Format("http://{0}:{1}/alive",
                                          m_server_host,
                                          m_server_port);

            HttpRequestMessage msg = new HttpRequestMessage();
            msg.Method     = HttpMethod.Get;
            msg.RequestUri = new Uri(uriStr);
            
            HttpResponseMessage response = await m_httpClient.SendAsync(msg);

            return true;
        }
    }
}
