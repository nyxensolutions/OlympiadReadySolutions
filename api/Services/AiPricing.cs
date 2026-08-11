namespace OlympiadReady.Api.Services;

/// <summary>
/// Real OpenAI per-token pricing, so AI spend is tracked in actual dollars rather than trusted
/// to the credit system's calibration. The credit budget (see <see cref="SubscriptionService"/>)
/// is a product-facing quota built on assumptions about token usage; this is what those
/// assumptions are checked against, and what the hard monthly dollar cap is enforced in.
///
/// Verified against https://developers.openai.com/api/docs/pricing on 2026-08-10. Update the
/// table when OpenAI reprices — nothing else needs to change.
/// </summary>
public static class AiPricing
{
    private readonly record struct Rate(decimal InputPerMillion, decimal OutputPerMillion);

    private static readonly Dictionary<string, Rate> Rates = new(StringComparer.OrdinalIgnoreCase)
    {
        ["gpt-4o-mini"]  = new(0.15m, 0.60m),
        ["gpt-4o"]       = new(2.50m, 10.00m),
        ["gpt-5.5"]      = new(5.00m, 30.00m),
        ["gpt-5-mini"]   = new(0.25m, 2.00m),
        ["gpt-5.4-mini"] = new(0.75m, 4.50m),
        ["o3"]           = new(2.00m, 8.00m),
        ["o4-mini"]      = new(1.10m, 4.40m),
    };

    // An unrecognised or future model name is priced as the most expensive known model rather
    // than treated as free. Being wrong-expensive fails safe against the dollar cap; being
    // wrong-cheap would let an unbudgeted model bypass it entirely.
    private static readonly Rate FallbackRate = new(5.00m, 30.00m);

    /// <summary>Real dollar cost from actual token counts returned by the API.</summary>
    public static decimal ActualCost(string model, int promptTokens, int completionTokens)
    {
        var rate = Rates.TryGetValue(model, out var r) ? r : FallbackRate;
        return promptTokens / 1_000_000m * rate.InputPerMillion
             + completionTokens / 1_000_000m * rate.OutputPerMillion;
    }

    // Measured from real generation + verification runs (10-question Olympiad batches on
    // gpt-5.5: ~305 prompt / ~1,136 completion tokens per question for generation alone).
    // Rounded up and padded for the verification pass, which runs on the same model. Only used
    // to size the PRE-call reservation — under-estimating is the unsafe direction, since the
    // reservation gates the call before real usage is known. The actual figure, once known,
    // replaces this estimate via SubscriptionService.ReconcileAiGenerationAsync, so error here
    // only affects a single call's margin, never the running total.
    private const int EstimatedPromptTokensPerQuestion = 400;
    private const int EstimatedCompletionTokensPerQuestion = 1500;

    /// <summary>Conservative pre-call estimate, used to size the reservation before the API runs.</summary>
    public static decimal EstimateCost(string model, int questionCount)
    {
        var promptTokens = EstimatedPromptTokensPerQuestion * questionCount;
        var completionTokens = EstimatedCompletionTokensPerQuestion * questionCount;
        return ActualCost(model, promptTokens, completionTokens);
    }
}
