-- =============================================================================
-- fix-subjects.sql
-- Normalises subject names in all tables to SOF-canonical values.
--
-- Canonical set:
--   Mathematics | Science | Science-Physics | Science-Chemistry | Science-Biology |
--   English | Hindi | General Knowledge | Social Studies | Logical Reasoning |
--   Computer Science | Commerce | AI
--
-- HOW TO RUN
--   1. Take a backup of the database first.
--   2. Open in SSMS (or run via sqlcmd), connect to your OlympiadReady DB.
--   3. Execute the script — it runs in a transaction so you can inspect before committing.
--   4. Review the verification SELECTs at the bottom.
--   5. If everything looks right: COMMIT TRANSACTION
--      If something is wrong:    ROLLBACK TRANSACTION
-- =============================================================================

BEGIN TRANSACTION;

-- ─────────────────────────────────────────────────────────────────────────────
-- LOWER(TRIM(...)) makes matching case-insensitive and whitespace-tolerant.
-- Science sub-disciplines run BEFORE the general 'Science' update so that
-- 'science-physics' etc. are caught first and not overwritten to 'Science'.
-- ─────────────────────────────────────────────────────────────────────────────

-- ── QuestionBank ─────────────────────────────────────────────────────────────

UPDATE QuestionBank SET Subject = 'Mathematics'
WHERE LOWER(TRIM(Subject)) IN ('math','maths','mathematics','imo');

-- Science sub-disciplines first
UPDATE QuestionBank SET Subject = 'Science-Physics'
WHERE LOWER(TRIM(Subject)) IN ('science-physics','science physics','sciencephysics','physics','phy');

UPDATE QuestionBank SET Subject = 'Science-Chemistry'
WHERE LOWER(TRIM(Subject)) IN ('science-chemistry','science chemistry','sciencechemistry','chemistry','chem','che');

UPDATE QuestionBank SET Subject = 'Science-Biology'
WHERE LOWER(TRIM(Subject)) IN ('science-biology','science biology','sciencebiology','biology','bio');

-- General Science (catch-all, runs after sub-disciplines)
UPDATE QuestionBank SET Subject = 'Science'
WHERE LOWER(TRIM(Subject)) IN ('science','nso');

UPDATE QuestionBank SET Subject = 'English'
WHERE LOWER(TRIM(Subject)) IN ('english','ieo','eng');

UPDATE QuestionBank SET Subject = 'Hindi'
WHERE LOWER(TRIM(Subject)) IN ('hindi','iho');

UPDATE QuestionBank SET Subject = 'General Knowledge'
WHERE LOWER(TRIM(Subject)) IN ('general knowledge','generalknowledge','gk','igko','general studies','gs');

UPDATE QuestionBank SET Subject = 'Social Studies'
WHERE LOWER(TRIM(Subject)) IN ('social studies','social-studies','socialstudies','socialscience','sst','ss','social science','isso','evs');

UPDATE QuestionBank SET Subject = 'Logical Reasoning'
WHERE LOWER(TRIM(Subject)) IN ('logical reasoning','logical-reasoning','logicalreasoning',
                                'reasoning','aptitude','reasoning & aptitude',
                                'reasoning and aptitude','irao','lr');

UPDATE QuestionBank SET Subject = 'Computer Science'
WHERE LOWER(TRIM(Subject)) IN ('computer science','computer-science','computerscience',
                                'cyber','nco','computers','computer','cs','it','ict',
                                'information technology');

UPDATE QuestionBank SET Subject = 'Commerce'
WHERE LOWER(TRIM(Subject)) IN ('commerce','ico','bst','business studies','business');

UPDATE QuestionBank SET Subject = 'AI'
WHERE LOWER(TRIM(Subject)) IN ('ai','artificial intelligence');

-- ── QuestionPapers ────────────────────────────────────────────────────────────

UPDATE QuestionPapers SET Subject = 'Mathematics'
WHERE LOWER(TRIM(Subject)) IN ('math','maths','mathematics','imo');

UPDATE QuestionPapers SET Subject = 'Science-Physics'
WHERE LOWER(TRIM(Subject)) IN ('science-physics','science physics','sciencephysics','physics','phy');

UPDATE QuestionPapers SET Subject = 'Science-Chemistry'
WHERE LOWER(TRIM(Subject)) IN ('science-chemistry','science chemistry','sciencechemistry','chemistry','chem','che');

UPDATE QuestionPapers SET Subject = 'Science-Biology'
WHERE LOWER(TRIM(Subject)) IN ('science-biology','science biology','sciencebiology','biology','bio');

UPDATE QuestionPapers SET Subject = 'Science'
WHERE LOWER(TRIM(Subject)) IN ('science','nso');

UPDATE QuestionPapers SET Subject = 'English'
WHERE LOWER(TRIM(Subject)) IN ('english','ieo','eng');

UPDATE QuestionPapers SET Subject = 'Hindi'
WHERE LOWER(TRIM(Subject)) IN ('hindi','iho');

UPDATE QuestionPapers SET Subject = 'General Knowledge'
WHERE LOWER(TRIM(Subject)) IN ('general knowledge','generalknowledge','gk','igko','general studies','gs');

UPDATE QuestionPapers SET Subject = 'Social Studies'
WHERE LOWER(TRIM(Subject)) IN ('social studies','social-studies','socialstudies','socialscience','sst','ss','social science','isso','evs');

UPDATE QuestionPapers SET Subject = 'Logical Reasoning'
WHERE LOWER(TRIM(Subject)) IN ('logical reasoning','logical-reasoning','logicalreasoning',
                                'reasoning','aptitude','reasoning & aptitude',
                                'reasoning and aptitude','irao','lr');

UPDATE QuestionPapers SET Subject = 'Computer Science'
WHERE LOWER(TRIM(Subject)) IN ('computer science','computer-science','computerscience',
                                'cyber','nco','computers','computer','cs','it','ict',
                                'information technology');

UPDATE QuestionPapers SET Subject = 'Commerce'
WHERE LOWER(TRIM(Subject)) IN ('commerce','ico','bst','business studies','business');

UPDATE QuestionPapers SET Subject = 'AI'
WHERE LOWER(TRIM(Subject)) IN ('ai','artificial intelligence');

-- ── UserMastery ───────────────────────────────────────────────────────────────

UPDATE UserMastery SET Subject = 'Mathematics'
WHERE LOWER(TRIM(Subject)) IN ('math','maths','mathematics','imo');

UPDATE UserMastery SET Subject = 'Science-Physics'
WHERE LOWER(TRIM(Subject)) IN ('science-physics','science physics','sciencephysics','physics','phy');

UPDATE UserMastery SET Subject = 'Science-Chemistry'
WHERE LOWER(TRIM(Subject)) IN ('science-chemistry','science chemistry','sciencechemistry','chemistry','chem','che');

UPDATE UserMastery SET Subject = 'Science-Biology'
WHERE LOWER(TRIM(Subject)) IN ('science-biology','science biology','sciencebiology','biology','bio');

UPDATE UserMastery SET Subject = 'Science'
WHERE LOWER(TRIM(Subject)) IN ('science','nso');

UPDATE UserMastery SET Subject = 'English'
WHERE LOWER(TRIM(Subject)) IN ('english','ieo','eng');

UPDATE UserMastery SET Subject = 'Hindi'
WHERE LOWER(TRIM(Subject)) IN ('hindi','iho');

UPDATE UserMastery SET Subject = 'General Knowledge'
WHERE LOWER(TRIM(Subject)) IN ('general knowledge','generalknowledge','gk','igko','general studies','gs');

UPDATE UserMastery SET Subject = 'Social Studies'
WHERE LOWER(TRIM(Subject)) IN ('social studies','social-studies','socialstudies','socialscience','sst','ss','social science','isso','evs');

UPDATE UserMastery SET Subject = 'Logical Reasoning'
WHERE LOWER(TRIM(Subject)) IN ('logical reasoning','logical-reasoning','logicalreasoning',
                                'reasoning','aptitude','reasoning & aptitude',
                                'reasoning and aptitude','irao','lr');

UPDATE UserMastery SET Subject = 'Computer Science'
WHERE LOWER(TRIM(Subject)) IN ('computer science','computer-science','computerscience',
                                'cyber','nco','computers','computer','cs','it','ict',
                                'information technology');

UPDATE UserMastery SET Subject = 'Commerce'
WHERE LOWER(TRIM(Subject)) IN ('commerce','ico','bst','business studies','business');

UPDATE UserMastery SET Subject = 'AI'
WHERE LOWER(TRIM(Subject)) IN ('ai','artificial intelligence');

-- =============================================================================
-- VERIFY — distinct subjects remaining in each table.
-- After running, only canonical names should appear below.
-- =============================================================================

SELECT 'QuestionBank' AS [Table], Subject, COUNT(*) AS Rows
FROM QuestionBank
GROUP BY Subject
ORDER BY Subject;

SELECT 'QuestionPapers' AS [Table], Subject, COUNT(*) AS Rows
FROM QuestionPapers
GROUP BY Subject
ORDER BY Subject;

SELECT 'UserMastery' AS [Table], Subject, COUNT(*) AS Rows
FROM UserMastery
GROUP BY Subject
ORDER BY Subject;

-- If all Subject values match the canonical list, run:
-- COMMIT TRANSACTION;
-- Otherwise:
-- ROLLBACK TRANSACTION;
