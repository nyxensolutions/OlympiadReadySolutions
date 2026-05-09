namespace OlympiadReady.Api.Models;

public record QuotaStatus(string Tier, int Used, int Limit, bool Allowed);
