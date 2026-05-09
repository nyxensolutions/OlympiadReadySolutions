using System.Security.Cryptography;
using System.Text;

namespace OlympiadReady.Api.Services;

public static class PaperCacheKey
{
    public static string Compute(string subject, int grade, string difficulty, int count)
    {
        var canonical =
            $"{subject.Trim().ToLowerInvariant()}|{grade}|{difficulty.Trim().ToLowerInvariant()}|{count}";
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(canonical));
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }
}
