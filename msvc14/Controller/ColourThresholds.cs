namespace Minority_Report
{
    public struct ColourThresholds
    {
        public string ColourName;

        public int min_rg;
        public int max_rg;
        public int min_rb;
        public int max_rb;
        public int min_gb;
        public int max_gb;

        public ColourThresholds(string name,
                                int minRG,
                                int maxRG,
                                int minRB,
                                int maxRB,
                                int minGB,
                                int maxGB)
        {
            ColourName = name;
            min_rg = minRG;
            max_rg = maxRG;
            min_rb = minRB;
            max_rb = maxRB;
            min_gb = minGB;
            max_gb = maxGB;
        }
    }
}