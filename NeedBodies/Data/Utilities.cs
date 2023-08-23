using NeedBodies.Auth;
namespace NeedBodies.Data
{
	public static class Utilities
	{
		public static readonly string Brand = "Need Bodies";
		public static readonly string HttpAddress = "http://127.0.0.1:5000";

		public static async Task<string> AddGame(string strHostID, string strHost, int intPlayerLim, int intGoalieLim, string strDate, string strTime, string strLocation)
		{
			HttpClient client = new HttpClient();

            JSONDateTimeLocation dateTimeLocation = new JSONDateTimeLocation
            {
                date = strDate,
                time = strTime,
                location = strLocation
            };

            var response = await client.PostAsJsonAsync<JSONDateTimeLocation>($"{Utilities.HttpAddress}/addGame/{strHostID}/{strHost}/{intPlayerLim}/{intGoalieLim}", dateTimeLocation);
			if (response.IsSuccessStatusCode)
			{
				return await response.Content.ReadAsStringAsync();
			}

			return String.Empty;
        }

		public static async Task<User> AddUser(string strName, string strPhone, string strEmail, string strPassword)
		{
            HttpClient client = new HttpClient();

            JSONEmailPassword emailPassword = new JSONEmailPassword
            {
                email = strEmail,
                password = strPassword
            };

            var response = await client.PostAsJsonAsync<JSONEmailPassword>($"{Utilities.HttpAddress}/addUser/{strName}/{strPhone}", emailPassword);
			return await response.Content.ReadFromJsonAsync<User>();

        }

        public static async Task<List<Game>> GetUserGames(string userID)
		{
			HttpClient client = new HttpClient();
			return await client.GetFromJsonAsync<List<Game>>(Utilities.HttpAddress + $"/getUserGames/{userID}");
        }

		public static async Task<List<Game>> GetUserHostedGames(string userID)
		{
			HttpClient client = new HttpClient();
			return await client.GetFromJsonAsync<List<Game>>(Utilities.HttpAddress + $"/getUserHostedGames/{userID}");
        }

		public static async Task<List<Location>> GetArenas()
		{
            HttpClient client = new HttpClient();
			return await client.GetFromJsonAsync<List<Location>>(Utilities.HttpAddress + "/arenas");
        }

		public static async Task<List<Game>> GetGames(string gameID = "-1")
		{
			HttpClient client = new HttpClient();
			List<Game> gameAsList;

            if (gameID == "-1")
			{
                return await client.GetFromJsonAsync<List<Game>>($"{Utilities.HttpAddress}/games");
            }
            else
			{
				return await client.GetFromJsonAsync<List<Game>>($"{Utilities.HttpAddress}/games?gameID={gameID}");
            }
		}

		public static async Task<string> RemoveUserFromGame(string userID, string gameID)
		{
            HttpClient client = new HttpClient();
            return await client.GetStringAsync(Utilities.HttpAddress + $"/removeUserFromGame/{userID}/{gameID}");
        }

		public static async Task<string> RemoveGame(string gameID)
		{
            HttpClient client = new HttpClient();
            return await client.GetStringAsync(Utilities.HttpAddress + $"/removeGame/{gameID}");
        }
    }
}

