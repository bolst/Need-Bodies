using System.Text.Json.Serialization;

namespace NeedBodies.Auth
{
    public class User
    {
        [JsonPropertyName("id")]
        public string ID { get; set; }

        [JsonPropertyName("name")]
        public string Name { get; set; }

        [JsonPropertyName("email")]
        public string Email { get; set; }

        [JsonPropertyName("phone")]
        public string Phone { get; set; }

        [JsonPropertyName("password")]
        public string Password { get; set; }

        [JsonPropertyName("games")]
        public string Games { get; set; }

        [JsonPropertyName("hosted games")]
        public string HostedGames { get; set; }

        [JsonPropertyName("role")]
        public string Role { get; set; }
    }
}