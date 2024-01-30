using System;
using System.IO;
using System.Linq;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;
using cAlgo.Indicators;
using System.Collections.Generic;
using System.Globalization;
using System.Threading;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.WEuropeStandardTime, AccessRights = AccessRights.FullAccess)]
    public class Data_collect : Robot
    {

        [Parameter(DefaultValue = 0.0)]
        public double Parameter { get; set; }

        [Parameter("Source")]
        public DataSeries Source { get; set; }

        [Parameter("Periods", DefaultValue = 14)]
        public int Periods { get; set; }




        // CSV File
        public string DataDir = "C:\\Users\\bartw\\Documents\\cAlgo\\Sources\\Robots\\Data_Collect_32\\Data_Collect_32\\data";
        public string LogsDir = "c:\\Local\\Projects\\Trader\\Logs";
        private string fiName;
        private System.IO.FileStream fstream;
        private System.IO.StreamWriter fwriter;
        private System.IO.StreamWriter _fileWriter;
        private string csvhead = "";
        // File variables
        public List<string> logfile_list = new List<string>();

        public string start_backtest;
        public string stop_backtest;
        private string loghead = "";

        // Indicator variables

        private Aroon _Aroon;
        private CommodityChannelIndex _CCI;
        private DirectionalMovementSystem _directionalMS;
        private LinearRegressionRSquared _linearRegressionRS { get; set; }
        private MedianPrice _medianPrice;
        private ParabolicSAR _SAR;
        private PriceVolumeTrend _PriceVolumeTrend;
        private RelativeStrengthIndex _rsi;
        private SimpleMovingAverage _sma { get; set; }
        private Trix _Trix;
        private WilliamsPctR _WilliamsP;
        private MoneyFlowIndex _MFI; 
        private MoneyFlowIndex _MFI_50; 
        private TickVolume _TV;


        //private ElliotOscillator EWO;

        // Controle variables

        public string soutParameters2;
        public string TotalOutput;
        public int HistoryCount = 1;





        public List<string> features_list = new List<string>();
        public string feature_line;
        public int feature_pointer = 0;


       



        //double close = MarketSeries.Close[index];



        protected override void OnStart()
        {

            // Put your initialization logic here

            // Alles naar US notatie!!!
            CultureInfo nonInvariantCulture = new CultureInfo("en-US");
            Thread.CurrentThread.CurrentCulture = nonInvariantCulture;

            #region Call Indicators
            // Aanroep indicatoren
            _Aroon = Indicators.Aroon(Periods);
            _CCI = Indicators.CommodityChannelIndex(30);
            _directionalMS = Indicators.DirectionalMovementSystem(Periods);
            _linearRegressionRS = Indicators.LinearRegressionRSquared(Source, Periods);
            _medianPrice = Indicators.MedianPrice();
            _SAR = Indicators.ParabolicSAR(0.02, 0.2);
            _PriceVolumeTrend = Indicators.PriceVolumeTrend(Source);
            _rsi = Indicators.RelativeStrengthIndex(Source, Periods);
            _sma = Indicators.SimpleMovingAverage(Source, Periods);
            _Trix = Indicators.Trix(Source, Periods);
            _WilliamsP = Indicators.WilliamsPctR(Periods);
            _MFI = Indicators.MoneyFlowIndex(Periods);
            _MFI_50 = Indicators.MoneyFlowIndex(50);
            _TV = Indicators.TickVolume();
            // _EWO = Indicators.GetIndicator GetIndicator<ElliotOscillator>(Source, Elliot_FastPeriod, Elliot_SlowPeriod);

            #endregion

            Create_files();

        }

        protected override void OnBar()
        {
            // Put your core logic here
            data_collect();
            csvhead = "";


            Get_data_line();
            if (feature_line != null)
            {
                string joined = feature_line;
                fwriter.WriteLine(joined);
            }

            

        }

        protected override void OnStop()
        {
            string total_log;
            // Write to logfile
            DateTime dateRealServer = Server.Time;
            stop_backtest = dateRealServer.ToShortDateString();
            logfile_list.Add(start_backtest);
            logfile_list.Add(stop_backtest);
            logfile_list.Add(features_list.Count.ToString());
            total_log = string.Join(",", logfile_list);
            _fileWriter.WriteLine(total_log);
            _fileWriter.Close();

            // Put your deinitialization logic here
            fwriter.Close();
            fstream.Close();
        }

        public void Get_data_line()
        {
            
            feature_pointer = features_list.Count();
            feature_line = features_list[^1];
           
            
        }

    

        
        protected void data_collect()
        {
            
            //specifier = "F" voor twee decimalen en culture op US voor . in plaats van ,;
            CultureInfo culture;
            culture = CultureInfo.CreateSpecificCulture("en-US");
            // Create a list to add all Indicator values
            var sa = new System.Collections.Generic.List<string>();


            DateTime dateRealServer = Server.Time;
            
           
            //sa.Add(dateRealServer.ToShortDateString());
            // sa.Add(dateRealServer.ToString("yyyy-MM-dd H:mm"));
            sa.Add(dateRealServer.ToString("dd.MM.yyyy HH:mm:ss"));
            // sa.Add(dateRealServer.ToString("H:mm"));
            csvhead = csvhead + "Datum" + ",";

            


            for(int i = 1; i< 50; i++) 
            {

                sa.Add(Bars.ClosePrices.Last(i).ToString("F6", culture));
                csvhead += "close_price" + i.ToString()+ ","; 
    
                sa.Add(Bars.OpenPrices.Last(i).ToString("F6", culture));
                csvhead += "open_price" + i.ToString()+ ",";
    
                sa.Add(Bars.HighPrices.Last(i).ToString("F6", culture));
                csvhead += "high_price" + i.ToString()+ ",";
    
                sa.Add(Bars.LowPrices.Last(i).ToString("F6", culture));
                csvhead += "low_price" + i.ToString()+ ",";
                
                
                sa.Add(_rsi.Result.Last(i).ToString("F1", culture));
                csvhead += "rsi" + i.ToString()+ ",";

                sa.Add(_MFI.Result.Last(i).ToString("F6", culture));
                csvhead  +=  "mfi"+ i.ToString()+ "," ;

                sa.Add(_TV.Result.Last(i).ToString("F6", culture));
                csvhead += "tv"+ i.ToString()+ ",";

                sa.Add(_sma.Result.Last(i).ToString("F6", culture));
                csvhead += "sma"+ i.ToString()+ ",";

                sa.Add(_WilliamsP.Result.Last(i).ToString("F6", culture));
                csvhead += "williams"+ i.ToString()+ ",";

                sa.Add(_linearRegressionRS.Result.Last(i).ToString("F6", culture));
                csvhead += "regrs"+ i.ToString()+ ",";
                
                sa.Add(_CCI.Result.Last(i).ToString("F6", culture));
                csvhead += "cci"+ i.ToString() +",";



            }
    
            csvhead = csvhead.Remove(csvhead.Length -1, 1);
            

            // Put al list items in one "," delimited string
            string soutParameters2 = "";
            soutParameters2 = string.Join(",", sa);
            Print(soutParameters2);
            features_list.Add(soutParameters2);
            // Count elements for setting te amount of collumns in the Header
            int aantal_kolommen = sa.Count * HistoryCount;
            sa.Clear();
        }

        protected void Create_files()
        {

            // Create directory if it does not exist
            if (System.IO.Directory.Exists(LogsDir) == false)
            {
                System.IO.Directory.CreateDirectory(LogsDir);
            }

            // Open logfile voor test results
            loghead = "Datum/Tijd,File naam,symbol,Backtest start, Backtest stop,History_count,aantal rijen\n";
            var filePath = Path.Combine(LogsDir, "DataCollect_results.txt");
            if (System.IO.File.Exists(filePath) == false)
            {
                System.IO.File.WriteAllText(filePath, loghead);
            }
            _fileWriter = File.AppendText(filePath);
            _fileWriter.AutoFlush = true;

            // schrijf eerste gegens naar logfile
            var thisDate = DateTime.Now;
            logfile_list.Add(thisDate.ToString());
            var run_filePath = Path.Combine(ToString());
            logfile_list.Add(run_filePath);
            logfile_list.Add(Symbol.Name.ToString());
            DateTime dateRealServer = Server.Time;
            start_backtest = dateRealServer.ToShortDateString();

            #region Create File
            // Create CSV File
            // Create header
            // Hier data collect voor tellen van aantal kolommen
            data_collect();
         
            csvhead = csvhead + "\n";
            //csvhead = csvhead + "DateTime,IsFalling,RSI_Value,Max,RSI,SMA,MACD,Final,"\n";
            fiName = DataDir + "\\Unprocessed_Data.csv";
            // Create directory if it does not exist
            if (System.IO.Directory.Exists(DataDir) == false)
            {
                System.IO.Directory.CreateDirectory(DataDir);
            }
            // Create file if it does not exist
            //if (System.IO.File.Exists(fiName) == false)
            //{
            System.IO.File.WriteAllText(fiName, csvhead);
            //}
            fstream = File.Open(fiName, FileMode.Open, FileAccess.Write, FileShare.ReadWrite);
            fstream.Seek(0, SeekOrigin.End);
            fwriter = new System.IO.StreamWriter(fstream, System.Text.Encoding.UTF8, 1);
            fwriter.AutoFlush = true;
            #endregion
        }
    }
}

