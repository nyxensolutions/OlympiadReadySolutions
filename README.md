# Olympiad Ready

SaaS platform for AI-generated school Olympiad practice papers and mock tests.

This repository contains the working prototype flow:

```
Sign in (Clerk) → Config form → Claude API → Test arena → Results + PDF download
```

Persistence in local SQL Server. Auth via Clerk (test instance).

### Endpoints

- `POST /api/generate/preview` — open endpoint, returns N questions, no persistence.
- `POST /api/papers/generate` — generate, save to DB, return `{ paperId, questions, cached, ... }`. Returns **402** with `{ code: "QUOTA_EXCEEDED", tier, used, limit }` when the Free-tier monthly cap is hit.
- `GET  /api/papers/{id}` — retrieve a saved paper.
- `POST /api/tests/submit` — score `{ paperId, answers[], timeTakenSeconds }`, persist to `MockTestResults`.
- `POST /api/export/pdf` — render arbitrary questions to PDF (open).
- `GET  /api/export/pdf/{paperId}` — render a saved paper to PDF.
- `GET  /api/billing/me` — current subscription `{ tier, used, limit, allowed }`.
- `GET  /api/dashboard/summary` — bundles `subscription`, recent `papers`, recent `results`, topic-wise `mastery` for the dashboard page.
- `POST /api/billing/checkout` — create a Razorpay order for `{ plan: "ProMonthly" }`. Returns `{ orderId, keyId, amount, currency, ... }`.
- `POST /api/billing/verify` — verify Razorpay payment signature and activate `Subscriptions` row. Body: `{ orderId, paymentId, signature, plan }`.

### Tiers & quotas

| Plan | Papers / month | Price |
| ---- | -------------- | ----- |
| Free | 2              | ₹0    |
| Pro  | 50             | ₹199 / 30 days |

Quota counts every paper (cache hits included). Limit configurable in [SubscriptionService.cs](api/Services/SubscriptionService.cs).

### Razorpay (test mode)

Keys live in dotnet user-secrets, never in source:

```
dotnet user-secrets set "Razorpay:KeyId" "rzp_test_..."
dotnet user-secrets set "Razorpay:KeySecret" "..."
```

Test card for the checkout modal: `4111 1111 1111 1111`, any future expiry, any CVV, any 3DS OTP.

### Cost optimizations

- **Question cache** — papers stored with SHA256 hash of `(subject|grade|difficulty|count)`. A second user requesting the same config gets the cached questions, no Claude call. See [PaperCacheKey.cs](api/Services/PaperCacheKey.cs) and [PapersController.cs](api/Controllers/PapersController.cs).
- **Anthropic prompt caching** — system prompt sent with `cache_control: ephemeral`. After the system prompt grows past ~1024 tokens, subsequent calls within ~5 min cache the input portion and pay ~10% of the input-token rate. Token usage logged in the API console as `cache_create` / `cache_read`.

### Auth (Clerk)

Frontend uses `@clerk/nextjs` with `clerkMiddleware()`. Keys live in [web/.env.local](web/.env.local) (gitignored):

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` and `CLERK_SECRET_KEY`

Header shows Sign in / Sign up buttons when unauthenticated, `<UserButton />` when signed in. The generator flow only renders inside `<SignedIn>`; an unauth visitor sees a sign-in CTA instead.

Backend validates Clerk-issued JWTs via `Microsoft.AspNetCore.Authentication.JwtBearer`. The issuer URL is configured in `Clerk:Authority` (auto-fetches JWKS). Protected controllers: `PapersController`, `TestsController`, and `ExportController.PdfFromPaper`. The open `POST /api/generate/preview` and `POST /api/export/pdf` remain unauthenticated for the future "Try it Free" widget.

User rows are keyed by the JWT's `sub` claim (Clerk user ID). On first authed request, [UserService.GetOrSyncAsync](api/Services/UserService.cs) inserts a row and reuses it thereafter. Email/name fall back to `{sub}@clerk.local` since Clerk's default JWT doesn't include them — wire a Clerk webhook or call the Clerk Backend API later to backfill.

### Database

Local SQL Server with Windows auth. Connection string in [appsettings.json](api/appsettings.json):

```
Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True
```

Schema is auto-created on startup via `db.Database.EnsureCreated()`. Tables: `Users`, `QuestionPapers`, `MockTestResults`. Without auth, all writes attribute to a single seeded `guest:default` user; this gets replaced when Clerk lands.

To reset the schema while iterating: `DROP DATABASE OlympiadReady` in SSMS, then restart the API.

## Layout

- `api/` — ASP.NET Core 8 Web API. Single endpoint `POST /api/generate/preview`.
- `web/` — Next.js 14 (App Router) frontend with Tailwind + Lucide.

## Prerequisites

- .NET 8 SDK
- Node.js 18.17+ (or 20+)
- An Anthropic API key (`sk-ant-...`)

## Run it

### 1. Backend

```bash
cd api
# Set your key (do NOT commit this)
dotnet user-secrets init
dotnet user-secrets set "Anthropic:ApiKey" "sk-ant-..."
dotnet run
```

Listens on `http://localhost:5080` (see `api/Properties/launchSettings.json`).

### 2. Frontend

```bash
cd web
cp .env.local.example .env.local   # default points at http://localhost:5080
npm install
npm run dev
```

Open http://localhost:3000.

## Model

The backend uses `claude-sonnet-4-6` by default. Change it in `api/appsettings.json` under `Anthropic:Model` if needed.

## What's next

Once the slice works:

1. Wire up Clerk auth (Next.js middleware + JWT validation in .NET).
2. Add EF Core + Azure SQL with the schema in the spec.
3. Full generator dashboard (subject grid, config sidebar, sliders).
4. Test arena (timer, flagging, one-question-at-a-time).
5. Result analytics + explanation accordion.
6. PDF export via QuestPDF.
