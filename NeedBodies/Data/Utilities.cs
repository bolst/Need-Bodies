using NeedBodies.Auth;
using System.Net;
using System.Net.Mail;
namespace NeedBodies.Data
{
	public static class Utilities
	{
		public static readonly string brandName = "Need Bodies";
		public static readonly string httpAddress = "http://127.0.0.1:5000";
		public static readonly string passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$";
        public static readonly string SiteLink = "https://localhost:7041";
		public static readonly int playerLimit = 100;
		public static readonly int goalieLimit = 20;


        public static async Task<string> AddGame(string strHostID, string strHost, int intPlayerLim, int intGoalieLim, string strDate, string strTime, string strLocation)
		{
			HttpClient client = new HttpClient();

            JSONDateTimeLocation dateTimeLocation = new JSONDateTimeLocation
            {
                date = strDate,
                time = strTime,
                location = strLocation
            };

            var response = await client.PostAsJsonAsync<JSONDateTimeLocation>($"{Utilities.httpAddress}/addGame/{strHostID}/{strHost}/{intPlayerLim}/{intGoalieLim}", dateTimeLocation);
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

            var response = await client.PostAsJsonAsync<JSONEmailPassword>($"{Utilities.httpAddress}/addUser/{strName}/{strPhone}", emailPassword);
			return await response.Content.ReadFromJsonAsync<User>();

        }

        public static async Task<List<Game>> GetUserGames(string userID)
		{
			HttpClient client = new HttpClient();
			return await client.GetFromJsonAsync<List<Game>>(Utilities.httpAddress + $"/getUserGames/{userID}");
        }

		public static async Task<List<Game>> GetUserHostedGames(string userID)
		{
			HttpClient client = new HttpClient();
			return await client.GetFromJsonAsync<List<Game>>(Utilities.httpAddress + $"/getUserHostedGames/{userID}");
        }

		public static async Task<List<Location>> GetArenas()
		{
            HttpClient client = new HttpClient();
			return await client.GetFromJsonAsync<List<Location>>(Utilities.httpAddress + "/arenas");
        }

		public static async Task<List<Game>> GetGames(string gameID = "-1")
		{
			HttpClient client = new HttpClient();
			List<Game> gameAsList;

            if (gameID == "-1")
			{
                return await client.GetFromJsonAsync<List<Game>>($"{Utilities.httpAddress}/games");
            }
            else
			{
				return await client.GetFromJsonAsync<List<Game>>($"{Utilities.httpAddress}/games?gameID={gameID}");
            }
		}

		public static async Task<string> RemoveUserFromGame(string userID, string gameID)
		{
            HttpClient client = new HttpClient();
            return await client.GetStringAsync(Utilities.httpAddress + $"/removeUserFromGame/{userID}/{gameID}");
        }

		public static async Task<string> RemoveGame(string gameID)
		{
            HttpClient client = new HttpClient();
            return await client.GetStringAsync(Utilities.httpAddress + $"/removeGame/{gameID}");
        }

		public static async Task<bool> IsUserInGame(string userID, string gameID)
		{
            HttpClient client = new HttpClient();
			string response = await client.GetStringAsync(Utilities.httpAddress + $"/isUserInGame/{userID}/{gameID}");
			return response == "yes";
        }

		public static async Task<string> CheckUserCredentials(string userID, string password)
		{

            HttpClient client = new HttpClient();

            JSONPassword jsonPassword = new JSONPassword
            {
                password = password
            };

            var response = await client.PostAsJsonAsync<JSONPassword>($"{Utilities.httpAddress}/checkUser/{userID}", jsonPassword);
			return await response.Content.ReadAsStringAsync();
        }

        public static async Task<string> GetUserRID(string userID)
        {
            HttpClient client = new HttpClient();

            return await client.GetStringAsync($"{Utilities.httpAddress}/getUserRID/{userID}");
        }

        public static async Task<string> ResetUserPassword(string userID, string myRID, string newPassword, UserService userService)
        {
            HttpClient client = new HttpClient();

            JSONRIDPassword jsonRidPassword = new JSONRIDPassword
            {
                RID = myRID,
                password = newPassword,
            };

            var response = await client.PostAsJsonAsync<JSONRIDPassword>($"{Utilities.httpAddress}/resetUserPassword/{userID}", jsonRidPassword);
            return await response.Content.ReadAsStringAsync();
        }


		private class JSONPassword
		{
			public string password { get; set; }
		}

        private class JSONRIDPassword
        {
            public string RID { get; set; }
            public string password { get; set; }
        }

        private class JSONEmailPassword
        {
            public string email { get; set; }
            public string password { get; set; }
        }

        private class JSONDateTimeLocation
        {
            public string date { get; set; }
            public string time { get; set; }
            public string location { get; set; }
        }

        public class Email
        {
            private string BrandEmail { get; set; }
            private string Password { get; set; }

            public SmtpClient smtpClient { get; set; }

            public Email() { }

            public async Task Initialize()
            {
                HttpClient client = new HttpClient();
                JSONEmailPassword jSONEmailPassword = await client.GetFromJsonAsync<JSONEmailPassword>($"{Utilities.httpAddress}/getEmailCredentials");
                BrandEmail = jSONEmailPassword.email;
                Password = jSONEmailPassword.password;

                smtpClient = new SmtpClient("smtp.office365.com", 587)
                {
                    UseDefaultCredentials = false,
                    Credentials = new NetworkCredential(BrandEmail, Password),
                    DeliveryMethod = SmtpDeliveryMethod.Network,
                    EnableSsl = true,
                };
            }

            public async Task<string> SendForgotPassword(string emailTo, UserService userService)
            {
                User user = userService.GetByEmail(emailTo);
                if (user == null)
                {
                    return $"An email with a password reset link has been sent to {emailTo} if it is registered.";
                }

                string userID = user.ID;
                string RID = await Utilities.GetUserRID(userID);

                string subject = $"{Utilities.brandName} Reset Password";

                string body = $"<div><a href=\"{Utilities.SiteLink}/reset?UID={userID}&RID={RID}\">Click here</a> to reset your password for Need Bodies.</div>";

                MailMessage mailMessage = new MailMessage
                {
                    From = new MailAddress(BrandEmail),
                    Subject = subject,
                    Body = body,
                    IsBodyHtml = true,
                };
                mailMessage.To.Add(emailTo);

                try
                {
                    smtpClient.Send(mailMessage);
                    return $"An email with a password reset link has been sent to {emailTo} if it is registered.";
                }
                catch(Exception exc)
                {
                    return $"Error: {exc.ToString()}";
                }
            }
        }
    }
}

