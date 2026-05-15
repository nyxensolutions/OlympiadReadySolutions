# How to import question bank JSON files

## Step 1 — Set the admin key

In `api/appsettings.json` replace `REPLACE_WITH_A_STRONG_RANDOM_SECRET`
with any long random string (keep it private — it's your seeding key).

Or use dotnet user-secrets so it never touches source:
```
cd api
dotnet user-secrets set "Admin:ApiKey" "my-super-secret-seed-key-123"
```

## Step 2 — Start the API

```
cd api
dotnet run
```

## Step 3 — POST your JSON file

```powershell
# PowerShell
Invoke-RestMethod `
  -Uri "http://localhost:5080/api/admin/import-questions?subject=Math&grade=5" `
  -Method POST `
  -Headers @{ "X-Admin-Key" = "my-super-secret-seed-key-123"; "Content-Type" = "application/json" } `
  -Body (Get-Content seed-data/math-grade5-foundation.json -Raw)
```

```bash
# curl
curl -X POST "http://localhost:5080/api/admin/import-questions?subject=Math&grade=5" \
  -H "X-Admin-Key: my-super-secret-seed-key-123" \
  -H "Content-Type: application/json" \
  -d @seed-data/math-grade5-foundation.json
```

The response looks like:
```json
{ "inserted": 42, "skipped": 0, "errors": [] }
```

`skipped` = exact duplicate question texts already in the DB (safe to re-run).

## Step 4 — Check bank stats

```
GET http://localhost:5080/api/admin/bank-stats
Header: X-Admin-Key: <your-key>
```

Returns a list like:
```json
[
  { "subject": "Math", "grade": 5, "difficulty": "Foundation", "count": 120 },
  { "subject": "Math", "grade": 5, "difficulty": "Advanced",    "count": 80 }
]
```

## JSON file format

Each file is a JSON **array** — one object per question:

```json
[
  {
    "QuestionText": "What is the LCM of 4 and 6?",
    "Options": ["8", "12", "24", "6"],
    "CorrectAnswer": "B",
    "Topic": "Fractions",
    "SubTopic": "LCM and HCF",
    "Difficulty": "Foundation",
    "Explanation": "The LCM of 4 and 6 is 12 because it is the smallest number divisible by both 4 and 6."
  }
]
```

| Field          | Rules                                                              |
|----------------|--------------------------------------------------------------------|
| `QuestionText` | Required. Any length. Duplicate texts for the same subject+grade are skipped automatically. |
| `Options`      | Required. Exactly 4 strings. No A./B. prefix — the UI adds that. |
| `CorrectAnswer`| Required. One of: `A`, `B`, `C`, `D`                             |
| `Topic`        | Required. Use the standard topic list from the system prompt.     |
| `SubTopic`     | Optional. Free text — as specific as you like.                    |
| `Difficulty`   | Required. One of: `Foundation`, `Advanced`, `Olympiad`            |
| `Explanation`  | Required. 2-4 sentences, plain English (or Devanagari for Hindi). |

`subject` and `grade` come from the query string, not the JSON body.
So one file = one subject + one grade (any mix of difficulties is fine).

## How the routing works

| User tier | Source                                                     |
|-----------|------------------------------------------------------------|
| Free      | Random N questions from QuestionBank matching the config.  |
|           | Falls back to Claude live-generation if bank has < N rows. |
| Pro       | QuestionPaper SHA256 cache → Claude live-generation.       |

So once you seed ≥ 5 questions per (subject, grade, difficulty) combo,
Free users will be served entirely from the bank — no Claude API cost.
