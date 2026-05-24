using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.Data.SqlClient;

class Program
{
    private static readonly Dictionary<string, string> SubjectAliases = new(StringComparer.OrdinalIgnoreCase)
    {
        ["math"] = "Mathematics",
        ["maths"] = "Mathematics",
        ["mathematics"] = "Mathematics",
        ["imo"] = "Mathematics",
        ["science"] = "Science",
        ["nso"] = "Science",
        ["science-physics"] = "Science-Physics",
        ["science physics"] = "Science-Physics",
        ["sciencephysics"] = "Science-Physics",
        ["physics"] = "Science-Physics",
        ["phy"] = "Science-Physics",
        ["science-chemistry"] = "Science-Chemistry",
        ["science chemistry"] = "Science-Chemistry",
        ["sciencechemistry"] = "Science-Chemistry",
        ["chemistry"] = "Science-Chemistry",
        ["chem"] = "Science-Chemistry",
        ["che"] = "Science-Chemistry",
        ["science-biology"] = "Science-Biology",
        ["science biology"] = "Science-Biology",
        ["sciencebiology"] = "Science-Biology",
        ["biology"] = "Science-Biology",
        ["bio"] = "Science-Biology",
        ["english"] = "English",
        ["ieo"] = "English",
        ["eng"] = "English",
        ["hindi"] = "Hindi",
        ["iho"] = "Hindi",
        ["hindi-olympiad"] = "Hindi",
        ["hindiolympiad"] = "Hindi",
        ["general knowledge"] = "General Knowledge",
        ["generalknowledge"] = "General Knowledge",
        ["gk"] = "General Knowledge",
        ["igko"] = "General Knowledge",
        ["general studies"] = "General Knowledge",
        ["gs"] = "General Knowledge",
        ["generalawareness"] = "General Knowledge",
        ["general awareness"] = "General Knowledge",
        ["social studies"] = "Social Studies",
        ["socialstudies"] = "Social Studies",
        ["socialscience"] = "Social Studies",
        ["social science"] = "Social Studies",
        ["sst"] = "Social Studies",
        ["ss"] = "Social Studies",
        ["isso"] = "Social Studies",
        ["evs"] = "Social Studies",
        ["logical reasoning"] = "Logical Reasoning",
        ["logical-reasoning"] = "Logical Reasoning",
        ["logicalreasoning"] = "Logical Reasoning",
        ["reasoning"] = "Logical Reasoning",
        ["aptitude"] = "Logical Reasoning",
        ["reasoning & aptitude"] = "Logical Reasoning",
        ["reasoning and aptitude"] = "Logical Reasoning",
        ["irao"] = "Logical Reasoning",
        ["lr"] = "Logical Reasoning",
        ["computer science"] = "Computer Science",
        ["computer-science"] = "Computer Science",
        ["computerscience"] = "Computer Science",
        ["cyber"] = "Computer Science",
        ["nco"] = "Computer Science",
        ["computers"] = "Computer Science",
        ["computer"] = "Computer Science",
        ["cs"] = "Computer Science",
        ["it"] = "Computer Science",
        ["ict"] = "Computer Science",
        ["information technology"] = "Computer Science",
        ["commerce"] = "Commerce",
        ["ico"] = "Commerce",
        ["bst"] = "Commerce",
        ["business studies"] = "Commerce",
        ["business"] = "Commerce",
        ["ai"] = "AI",
        ["artificial intelligence"] = "AI",
        ["spell bee"] = "Spell Bee",
        ["spellbee"] = "Spell Bee",
        ["spelling bee"] = "Spell Bee",
        ["spellingbee"] = "Spell Bee",
        ["hbc"] = "Spell Bee",
        ["hummingbird"] = "Spell Bee",
        ["humming bird"] = "Spell Bee",
        ["spelling"] = "Spell Bee",
        ["spell-bee"] = "Spell Bee"
    };

    private static readonly Regex PrefixRx = new(@"^\(?([A-Da-d])[)\.\:\-]\s*", RegexOptions.Compiled);

    private static string StripOptionPrefix(string option, int position)
    {
        var trimmed = option.Trim();
        var m = PrefixRx.Match(trimmed);
        if (!m.Success) return trimmed;

        char expected = (char)('A' + position);
        if (char.ToUpper(m.Groups[1].Value[0]) != expected) return trimmed;

        return trimmed[m.Length..].Trim();
    }

    private static string NormalizeSubject(string input)
    {
        if (string.IsNullOrWhiteSpace(input)) return input;
        
        var trimmed = input.Trim();
        if (SubjectAliases.TryGetValue(trimmed, out var canonical)) return canonical;

        var collapsed = Regex.Replace(trimmed, @"[\s\-_]+", " ").Trim();
        if (SubjectAliases.TryGetValue(collapsed, out canonical)) return canonical;

        return input; // Fallback
    }

    private static string NormalizeDifficulty(string? s)
    {
        if (string.IsNullOrWhiteSpace(s)) return "Foundation";
        return s.Trim().ToLowerInvariant() switch
        {
            "foundation" => "Foundation",
            "advanced" => "Advanced",
            "olympiad" => "Olympiad",
            "medium" => "Advanced",
            _ => "Foundation"
        };
    }

    class QuestionJsonModel
    {
        public string? QuestionText { get; set; }
        public string? ImageUrl { get; set; }
        public JsonElement Options { get; set; }
        public string? CorrectAnswer { get; set; }
        public string? Topic { get; set; }
        public string? SubTopic { get; set; }
        public string? Difficulty { get; set; }
        public string? Explanation { get; set; }
    }

    static void Main(string[] args)
    {
        bool isRun = args.Contains("--run");
        string seededDir = @"d:\Nyxen\OlympiadReady\OlympiadReadySolutions\seeded";
        string connStr = "Server=localhost;Database=OlympiadReady;Integrated Security=True;TrustServerCertificate=True;Application Name=OlympiadReady";

        Console.WriteLine("=================================================");
        Console.WriteLine("        OlympiadReady Database Importer          ");
        Console.WriteLine("=================================================");
        Console.WriteLine($"Mode: {(isRun ? "LIVE RUN (Wiping and Writing to DB)" : "DRY RUN (Analysis & Validation)")}");
        Console.WriteLine($"Directory: {seededDir}");
        Console.WriteLine();

        if (!Directory.Exists(seededDir))
        {
            Console.WriteLine($"ERROR: Directory '{seededDir}' does not exist!");
            return;
        }

        var files = Directory.GetFiles(seededDir, "*.json", SearchOption.AllDirectories);
        Console.WriteLine($"Found {files.Length} JSON files to import.");

        int totalQuestions = 0;
        int successfulFiles = 0;
        int failedFiles = 0;
        var subjectStats = new Dictionary<string, int>();
        var gradeStats = new Dictionary<int, int>();

        SqlConnection? conn = null;
        SqlTransaction? trans = null;

        if (isRun)
        {
            Console.WriteLine("Connecting to database and clearing corrupted data...");
            try
            {
                conn = new SqlConnection(connStr);
                conn.Open();
                
                // Clear the tables safely
                using (var clearCmd = new SqlCommand("DELETE FROM UserMistakes; DELETE FROM QuestionPapers; DELETE FROM QuestionBank;", conn))
                {
                    int rowsDeleted = clearCmd.ExecuteNonQuery();
                    Console.WriteLine("Successfully deleted previous corrupted database records from UserMistakes, QuestionPapers, and QuestionBank.");
                }

                trans = conn.BeginTransaction();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"DB Connection / Clearing Error: {ex.Message}");
                if (conn != null) conn.Dispose();
                return;
            }
        }

        var filenameRegex = new Regex(@"^(?:sample-)?(?<subject>[a-zA-Z0-9\-]+?)-grade(?<grade>\d+)-", RegexOptions.IgnoreCase);

        foreach (var file in files)
        {
            string filename = Path.GetFileNameWithoutExtension(file);
            if (filename.Equals("HOW-TO-IMPORT", StringComparison.OrdinalIgnoreCase)) continue;

            var match = filenameRegex.Match(filename);
            string rawSubject = "";
            int grade = 1;

            if (match.Success)
            {
                rawSubject = match.Groups["subject"].Value;
                grade = int.Parse(match.Groups["grade"].Value);
            }
            else
            {
                // Fallback parsing for different naming conventions
                if (filename.StartsWith("computer-science-grade1-"))
                {
                    rawSubject = "computer-science";
                    grade = 1;
                }
                else
                {
                    Console.WriteLine($"WARNING: Could not parse subject/grade from filename: {filename}. Skipping file.");
                    failedFiles++;
                    continue;
                }
            }

            string subject = NormalizeSubject(rawSubject);

            try
            {
                // Read strictly as UTF-8
                string jsonText = File.ReadAllText(file, Encoding.UTF8);
                var questions = JsonSerializer.Deserialize<List<QuestionJsonModel>>(jsonText, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                if (questions == null || questions.Count == 0)
                {
                    Console.WriteLine($"WARNING: File {filename}.json is empty or invalid. Skipping.");
                    failedFiles++;
                    continue;
                }

                int fileInserted = 0;
                var existingInFile = new HashSet<string>(StringComparer.Ordinal);

                foreach (var q in questions)
                {
                    if (string.IsNullOrWhiteSpace(q.QuestionText)) continue;

                    string qTextTrimmed = q.QuestionText.Trim();
                    if (existingInFile.Contains(qTextTrimmed)) continue; // skip duplicates within the same file
                    existingInFile.Add(qTextTrimmed);

                    // Parse Options properly
                    List<string> optionsList = new List<string>();
                    if (q.Options.ValueKind == JsonValueKind.Array)
                    {
                        foreach (var opt in q.Options.EnumerateArray())
                        {
                            optionsList.Add(opt.GetString() ?? "");
                        }
                    }
                    else if (q.Options.ValueKind == JsonValueKind.Object)
                    {
                        var keys = new[] { "A", "B", "C", "D" };
                        foreach (var k in keys)
                        {
                            if (q.Options.TryGetProperty(k, out var prop))
                            {
                                optionsList.Add($"{k}) {prop.GetString()}");
                            }
                            else
                            {
                                optionsList.Add("");
                            }
                        }
                    }

                    if (optionsList.Count != 4)
                    {
                        continue; // skip malformed options
                    }

                    // Clean option prefixes
                    var cleanedOptions = optionsList.Select((o, i) => StripOptionPrefix(o, i)).ToList();
                    string optionsJson = JsonSerializer.Serialize(cleanedOptions);

                    string correctAns = (q.CorrectAnswer ?? "A").Trim().ToUpper();
                    if (correctAns.Length > 0 && (correctAns[0] == 'A' || correctAns[0] == 'B' || correctAns[0] == 'C' || correctAns[0] == 'D'))
                    {
                        correctAns = correctAns[0].ToString();
                    }
                    else
                    {
                        correctAns = "A";
                    }

                    string difficulty = NormalizeDifficulty(q.Difficulty);
                    string topic = (q.Topic ?? "").Trim();
                    string subTopic = (q.SubTopic ?? "").Trim();
                    string explanation = (q.Explanation ?? "").Trim();

                    if (isRun && conn != null && trans != null)
                    {
                        using var insertCmd = new SqlCommand(@"
                            INSERT INTO QuestionBank (QuestionBankId, Subject, Grade, Difficulty, Topic, SubTopic, QuestionText, OptionsJson, CorrectAnswer, Explanation, CreatedAt)
                            VALUES (@id, @subject, @grade, @diff, @topic, @subtopic, @text, @options, @correct, @exp, @created)", conn, trans);
                        
                        insertCmd.Parameters.AddWithValue("@id", Guid.NewGuid());
                        insertCmd.Parameters.AddWithValue("@subject", subject);
                        insertCmd.Parameters.AddWithValue("@grade", grade);
                        insertCmd.Parameters.AddWithValue("@diff", difficulty);
                        insertCmd.Parameters.AddWithValue("@topic", topic);
                        insertCmd.Parameters.AddWithValue("@subtopic", string.IsNullOrEmpty(subTopic) ? (object)DBNull.Value : subTopic);
                        insertCmd.Parameters.AddWithValue("@text", qTextTrimmed);
                        insertCmd.Parameters.AddWithValue("@options", optionsJson);
                        insertCmd.Parameters.AddWithValue("@correct", correctAns);
                        insertCmd.Parameters.AddWithValue("@exp", explanation);
                        insertCmd.Parameters.AddWithValue("@created", DateTime.UtcNow);

                        insertCmd.ExecuteNonQuery();
                    }

                    fileInserted++;
                    totalQuestions++;
                }

                // Collect Stats
                if (!subjectStats.ContainsKey(subject)) subjectStats[subject] = 0;
                subjectStats[subject] += fileInserted;

                if (!gradeStats.ContainsKey(grade)) gradeStats[grade] = 0;
                gradeStats[grade] += fileInserted;

                successfulFiles++;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR processing file {filename}.json: {ex.Message}");
                failedFiles++;
            }
        }

        if (isRun && conn != null && trans != null)
        {
            try
            {
                trans.Commit();
                Console.WriteLine("DATABASE TRANSACTION COMMITTED SUCCESSFULLY!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Transaction Commit Error: {ex.Message}");
                trans.Rollback();
            }
            finally
            {
                conn.Close();
                conn.Dispose();
            }
        }

        Console.WriteLine();
        Console.WriteLine("=================================================");
        Console.WriteLine("               IMPORT REPORT                     ");
        Console.WriteLine("=================================================");
        Console.WriteLine($"Successful files:  {successfulFiles}");
        Console.WriteLine($"Failed/Skipped:    {failedFiles}");
        Console.WriteLine($"Total Questions:   {totalQuestions}");
        Console.WriteLine();
        Console.WriteLine("Questions by Subject:");
        foreach (var pair in subjectStats.OrderByDescending(p => p.Value))
        {
            Console.WriteLine($"  - {pair.Key,-20}: {pair.Value} questions");
        }
        Console.WriteLine();
        Console.WriteLine("Questions by Grade:");
        foreach (var pair in gradeStats.OrderBy(p => p.Key))
        {
            Console.WriteLine($"  - Grade {pair.Key,-13}: {pair.Value} questions");
        }
        Console.WriteLine("=================================================");
    }
}
