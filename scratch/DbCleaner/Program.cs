using System;
using System.Collections.Generic;
using Microsoft.Data.SqlClient;

class Program
{
    static string Clean(string s)
    {
        if (string.IsNullOrEmpty(s)) return s;

        // 1. Degree symbol cleanup
        s = s.Replace("Â°", "°");
        s = s.Replace("Â", "");

        // 2. Multiplication U+FFFD U+002D
        s = s.Replace("\uFFFD-", "×");
        s = s.Replace("-", "×");

        // 3. Indian Rupee symbol
        s = s.Replace("â‚¹", "₹");
        s = s.Replace("\uFFFD,\uFFFD", "₹");
        s = s.Replace(",", "₹");
        s = s.Replace("\uFFFD,", "₹");
        s = s.Replace(",", "₹");

        return s;
    }

    static void Main()
    {
        string connStr = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;";
        using var conn = new SqlConnection(connStr);
        conn.Open();

        Console.WriteLine("Successfully connected to the database. Cleaning up corrupt characters...");

        // --- 1. Clean QuestionBank ---
        int qbUpdated = 0;
        using (var cmd = new SqlCommand("SELECT QuestionBankId, QuestionText, OptionsJson, Explanation FROM QuestionBank", conn))
        using (var reader = cmd.ExecuteReader())
        {
            var updates = new List<(Guid id, string text, string opts, string exp)>();
            while (reader.Read())
            {
                var id = reader.GetGuid(0);
                var text = reader.IsDBNull(1) ? "" : reader.GetString(1);
                var opts = reader.IsDBNull(2) ? "" : reader.GetString(2);
                var exp = reader.IsDBNull(3) ? "" : reader.GetString(3);

                var cleanText = Clean(text);
                var cleanOpts = Clean(opts);
                var cleanExp = Clean(exp);

                if (cleanText != text || cleanOpts != opts || cleanExp != exp)
                {
                    updates.Add((id, cleanText, cleanOpts, cleanExp));
                }
            }
            reader.Close();

            Console.WriteLine($"Found {updates.Count} rows in QuestionBank requiring updates.");
            foreach (var u in updates)
            {
                using var upCmd = new SqlCommand(
                    "UPDATE QuestionBank SET QuestionText = @text, OptionsJson = @opts, Explanation = @exp WHERE QuestionBankId = @id", conn);
                upCmd.Parameters.AddWithValue("@id", u.id);
                upCmd.Parameters.AddWithValue("@text", u.text);
                upCmd.Parameters.AddWithValue("@opts", u.opts);
                upCmd.Parameters.AddWithValue("@exp", u.exp);
                upCmd.ExecuteNonQuery();
                qbUpdated++;
            }
        }
        Console.WriteLine($"QuestionBank: Updated {qbUpdated} rows.");

        // --- 2. Clean QuestionPapers ---
        int qpUpdated = 0;
        using (var cmd = new SqlCommand("SELECT PaperId, JsonContent FROM QuestionPapers", conn))
        using (var reader = cmd.ExecuteReader())
        {
            var updates = new List<(Guid id, string content)>();
            while (reader.Read())
            {
                var id = reader.GetGuid(0);
                var content = reader.IsDBNull(1) ? "" : reader.GetString(1);
                var cleanContent = Clean(content);

                if (cleanContent != content)
                {
                    updates.Add((id, cleanContent));
                }
            }
            reader.Close();

            Console.WriteLine($"Found {updates.Count} rows in QuestionPapers requiring updates.");
            foreach (var u in updates)
            {
                using var upCmd = new SqlCommand(
                    "UPDATE QuestionPapers SET JsonContent = @content WHERE PaperId = @id", conn);
                upCmd.Parameters.AddWithValue("@id", u.id);
                upCmd.Parameters.AddWithValue("@content", u.content);
                upCmd.ExecuteNonQuery();
                qpUpdated++;
            }
        }
        Console.WriteLine($"QuestionPapers: Updated {qpUpdated} rows.");

        // --- 3. Clean UserMistakes ---
        int umUpdated = 0;
        using (var cmd = new SqlCommand("SELECT MistakeId, QuestionJson FROM UserMistakes", conn))
        using (var reader = cmd.ExecuteReader())
        {
            var updates = new List<(Guid id, string json)>();
            while (reader.Read())
            {
                var id = reader.GetGuid(0);
                var json = reader.IsDBNull(1) ? "" : reader.GetString(1);
                var cleanJson = Clean(json);

                if (cleanJson != json)
                {
                    updates.Add((id, cleanJson));
                }
            }
            reader.Close();

            Console.WriteLine($"Found {updates.Count} rows in UserMistakes requiring updates.");
            foreach (var u in updates)
            {
                using var upCmd = new SqlCommand(
                    "UPDATE UserMistakes SET QuestionJson = @json WHERE MistakeId = @id", conn);
                upCmd.Parameters.AddWithValue("@id", u.id);
                upCmd.Parameters.AddWithValue("@json", u.json);
                upCmd.ExecuteNonQuery();
                umUpdated++;
            }
        }
        Console.WriteLine($"UserMistakes: Updated {umUpdated} rows.");
        Console.WriteLine("Cleanup process complete!");
    }
}
