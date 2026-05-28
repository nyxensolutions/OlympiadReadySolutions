"""
Resume from timelines onward (bars+pies already posted in the failed run).
"""
import generate_sst_v2 as s

if __name__ == "__main__":
    print("=" * 65)
    print("OlympiadReady — SST v2 RESUME: timelines, maps, civics, text")
    print("=" * 65)
    s.gen_timelines()
    s.gen_map_questions()
    s.gen_civics_diagrams()
    s.gen_text_questions()
    total = s.POSTED + s.SKIPPED + s.FAILED
    print(f"\n{'='*65}")
    print(f"DONE — Posted: {s.POSTED}  Skipped(dup): {s.SKIPPED}  Failed: {s.FAILED}  Total: {total}")
    print(f"{'='*65}")
