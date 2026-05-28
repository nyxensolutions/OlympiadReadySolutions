"""Retry only the failed sections (Medium->Advanced fix)"""
import sys
sys.path.insert(0, r"D:\Nyxen\OlympiadReady\OlympiadReadySolutions\scripts")
import generate_olympiad_thin_slots as s

s.POSTED = s.SKIPPED = s.FAILED = 0
s.gen_gr5_cs()
s.gen_gr6_cs()
s.gen_gr10_gk()

print(f"\n{'='*60}")
print(f"RETRY DONE — Posted: {s.POSTED}  Skipped(dup): {s.SKIPPED}  Failed: {s.FAILED}")
print(f"{'='*60}")
