using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using OlympiadReady.Api.Data;
using OlympiadReady.Api.Services;
using QuestPDF.Infrastructure;
using Sentry;
using Microsoft.AspNetCore.RateLimiting;

QuestPDF.Settings.License = LicenseType.Community;

var builder = WebApplication.CreateBuilder(args);


// ── GlitchTip / Sentry error tracking ────────────────────────────────────────
if (builder.Environment.IsProduction())
{
    builder.WebHost.UseSentry(o =>
    {
        o.Dsn = builder.Configuration["Sentry:Dsn"];
        o.TracesSampleRate = builder.Configuration.GetValue<double>("Sentry:TracesSampleRate", 0.1);
        o.Environment = builder.Configuration["Sentry:Environment"] ?? builder.Environment.EnvironmentName;
        o.Debug = builder.Environment.IsDevelopment();
        // Attach request body to error events (useful for diagnosing generation failures)
        o.MaxRequestBodySize = Sentry.Extensibility.RequestSize.Medium;
    });
}
// ─────────────────────────────────────────────────────────────────────────────
builder.Services.AddHttpClient<BrevoEmailService>();
builder.Services.AddScoped<IEmailService, BrevoEmailService>();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();
builder.Services.AddHttpContextAccessor();

builder.Services.AddDbContext<AppDbContext>(o =>
    o.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection"), 
        sqlOptions => sqlOptions.EnableRetryOnFailure(
            maxRetryCount: 5,
            maxRetryDelay: TimeSpan.FromSeconds(30),
            errorNumbersToAdd: null)));

builder.Services.AddHttpClient<AiGenerationService>(c =>
{
    c.BaseAddress = new Uri("https://api.openai.com/");
    c.Timeout = TimeSpan.FromSeconds(200); // Azure ARR limit is 230s; give 30s headroom
});

builder.Services.AddScoped<PdfService>();
builder.Services.AddScoped<UserService>();
builder.Services.AddScoped<SubscriptionService>();
builder.Services.AddScoped<MasteryService>();
builder.Services.AddScoped<QuestionBankService>();
builder.Services.AddHttpClient<RazorpayService>(c =>
{
    c.Timeout = TimeSpan.FromSeconds(30);
});

var clerkAuthority = builder.Configuration["Clerk:Authority"]
    ?? throw new InvalidOperationException("Clerk:Authority is not configured");

builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = clerkAuthority;
        options.MapInboundClaims = false;
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = clerkAuthority,
            ValidateAudience = false,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            NameClaimType = "sub"
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminPolicy", policy => policy.RequireClaim("role", "admin"));
});

const string CorsPolicy = "WebDev";
builder.Services.AddCors(o => o.AddPolicy(CorsPolicy, p => p
    .SetIsOriginAllowed(origin => 
    {
        var host = new Uri(origin).Host;
        return host == "localhost" || 
               host == "127.0.0.1" || 
               host == "olympiadready.com" || 
               host.EndsWith(".olympiadready.com") || 
               host.EndsWith(".vercel.app");
    })
    .AllowAnyHeader()
    .AllowAnyMethod()
    .AllowCredentials()
    .WithExposedHeaders("Content-Disposition")));

builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("GlobalFixed", opt =>
    {
        opt.Window = TimeSpan.FromMinutes(1);
        opt.PermitLimit = 200;
        opt.QueueProcessingOrder = System.Threading.RateLimiting.QueueProcessingOrder.OldestFirst;
        opt.QueueLimit = 10;
    });
});

var app = builder.Build();

// Apply pending EF migrations on startup. In dev this also creates the database the first time.
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseStaticFiles();
app.UseCors(CorsPolicy);
app.UseRateLimiter();
if (app.Environment.IsProduction())
{
    app.UseSentryTracing(); // must be before auth so request spans are captured
}
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers().RequireRateLimiting("GlobalFixed");

app.Run();
