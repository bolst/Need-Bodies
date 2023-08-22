using System.Linq;
using System.Text.Json.Serialization;
using NeedBodies.Auth;

namespace NeedBodies.Data
{
	public class Game
	{
        [JsonPropertyName("id")]
        public string ID { get; set; }

        [JsonPropertyName("host")]
        public string Host { get; set; }

        [JsonPropertyName("date")]
        public string Date { get; set; }

        [JsonPropertyName("time")]
        public string Time { get; set; }

        [JsonPropertyName("location")]
        public string Location { get; set; }

        [JsonPropertyName("player limit")]
        public int PlayerLimit { get; set; }

        [JsonPropertyName("player list")]
        public string PlayerList { get; set; }

        [JsonPropertyName("goalie limit")]
        public int GoalieLimit { get; set; }

        [JsonPropertyName("goalie list")]
        public string GoalieList { get; set; }

        public string FormatDate()
        {
            if (Date == String.Empty || Date.Length != 8) return String.Empty;

            string year = Date.Substring(0, 4);
            string month = Date.Substring(4, 2);
            string day = Date.Substring(6, 2);

            return month + '/' + day + '/' + year;
        }

        public string FormatTime()
        {
            string time = this.Time;

            if (Time.Length == 3)
            {
                time = "0" + time;
            }
            else if (time == String.Empty || time.Length != 4) return String.Empty;

            string strMinute = time.Substring(2, 2);
            int intHour = -1;
            string strAMPM = "AM";

            Int32.TryParse(time.Substring(0, 2), out intHour);
            if (intHour != -1)
            {
                if (intHour > 12 && intHour < 24)
                {
                    intHour -= 12;
                    strAMPM = "PM";
                }
                else if (intHour == 12)
                {
                    strAMPM = "PM";
                }
                else if (intHour == 0)
                {
                    intHour += 12;
                }
            }

            string strHour = intHour.ToString();

            return strHour + ':' + strMinute + ' ' + strAMPM;
        }

        public string FormatPlayerCount()
        {
            if (PlayerList == null) return $"0/{PlayerLimit}";

            string endString = '/' + PlayerLimit.ToString();

            int playerCount = PlayerList.Count(x => x == ';');

            string strPlayerCount = playerCount.ToString();

            return strPlayerCount + endString;
        }

        public string FormatGoalieCount()
        {
            if (GoalieList == null) return $"0/{GoalieLimit}";

            string endString = '/' + GoalieLimit.ToString();

            int goalieCount = GoalieList.Count(x => x == ';');

            string strGoalieCount = goalieCount.ToString();

            return strGoalieCount + endString;
        }

        public List<User> GetPlayers(UserService userService)
        {
            if (PlayerList == null) return new List<User>();

            string[] userIDs = PlayerList.Split(';');
            userIDs = userIDs.SkipLast(1).ToArray();
            List<User> Users = new List<User>();
            foreach (string userID in userIDs)
            {
                User userFromID = userService.GetByID(userID);
                Users.Add(userFromID);
            }

            return Users;
        }

        public List<User> GetGoalies(UserService userService)
        {
            if (GoalieList == null) return new List<User>();

            string[] userIDs = GoalieList.Split(';');
            userIDs = userIDs.SkipLast(1).ToArray();
            List<User> Users = new List<User>();
            foreach (string userID in userIDs)
            {
                User userFromID = userService.GetByID(userID);
                Users.Add(userFromID);
            }

            return Users;
        }
    }
}

