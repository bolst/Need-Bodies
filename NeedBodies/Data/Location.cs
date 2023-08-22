using System.Text.Json.Serialization;
namespace NeedBodies.Data
{
	public class Location
	{
		[JsonPropertyName("arena")]
		public string Name { get; set; }

		[JsonPropertyName("address")]
		public string Address { get; set; }

		[JsonPropertyName("city")]
		public string City { get; set; }

		[JsonPropertyName("province")]
		public string Province { get; set; }

		[JsonPropertyName("postal")]
		public string Postal { get; set; }

		[JsonPropertyName("country")]
		public string Country { get; set; }

		[JsonPropertyName("website")]
		public string Website { get; set; }
	}
}

