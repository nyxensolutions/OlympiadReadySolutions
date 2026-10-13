using Google.Apis.AndroidPublisher.v3;
using Google.Apis.AndroidPublisher.v3.Data;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Services;

namespace OlympiadReady.Api.Services;

/// <summary>
/// Verifies Google Play subscription purchases with the Play Developer API.
/// Needs GooglePlay:ServiceAccountJson (a service account invited in Play Console with
/// "View financial data" and "Manage orders and subscriptions").
/// </summary>
public class GooglePlayService
{
    public const string MonthlyBasePlan = "monthly";
    public const string AnnualBasePlan = "annual";

    private readonly AndroidPublisherService? _publisher;

    public string PackageName { get; }
    public bool IsConfigured => _publisher != null;

    public GooglePlayService(IConfiguration config, ILogger<GooglePlayService> log)
    {
        PackageName = config["GooglePlay:PackageName"] ?? "com.nyxensolutions.olympiadready";

        var json = config["GooglePlay:ServiceAccountJson"];
        if (string.IsNullOrWhiteSpace(json))
        {
            log.LogWarning("GooglePlay:ServiceAccountJson is not set — Google Play purchases cannot be verified.");
            return;
        }

        var credential = CredentialFactory
            .FromJson<ServiceAccountCredential>(json)
            .ToGoogleCredential()
            .CreateScoped(AndroidPublisherService.Scope.Androidpublisher);

        _publisher = new AndroidPublisherService(new BaseClientService.Initializer
        {
            HttpClientInitializer = credential,
            ApplicationName = "OlympiadReady",
        });
    }

    public static string ProductIdFor(bool isChampion, int subjectCount) =>
        isChampion ? "champion" : $"modular_{subjectCount}";

    public static string BasePlanIdFor(bool isAnnual) => isAnnual ? AnnualBasePlan : MonthlyBasePlan;

    public Task<SubscriptionPurchaseV2> GetSubscriptionAsync(string purchaseToken, CancellationToken ct) =>
        Publisher.Purchases.Subscriptionsv2.Get(PackageName, purchaseToken).ExecuteAsync(ct);

    public Task AcknowledgeAsync(string productId, string purchaseToken, CancellationToken ct) =>
        Publisher.Purchases.Subscriptions
            .Acknowledge(new SubscriptionPurchasesAcknowledgeRequest(), PackageName, productId, purchaseToken)
            .ExecuteAsync(ct);

    private AndroidPublisherService Publisher =>
        _publisher ?? throw new InvalidOperationException("Google Play billing is not configured on the server.");
}
