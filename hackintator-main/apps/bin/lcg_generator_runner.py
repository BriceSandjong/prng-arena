import os
import sys
from pathlib import Path

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]
arg4 = sys.argv[4]
arg5 = int(sys.argv[5])

# Find the lcg_generator executable (support both .exe and no extension)
script_dir = Path(__file__).resolve().parent
lcg_gen_exe = script_dir / "lcg_generator" / "output" / "main.exe"
if not lcg_gen_exe.exists():
    lcg_gen_exe = script_dir / "lcg_generator" / "output" / "main"

if not lcg_gen_exe.exists():
    print(f"ERROR: Could not find lcg_generator executable at {lcg_gen_exe}", file=sys.stderr)
    sys.exit(1)

print(arg4)

for i in range(0, arg5):
  arg4 = os.popen(f'"{lcg_gen_exe}" {arg1} {arg2} {arg3} {arg4}').read()
  print(arg4, end='')

