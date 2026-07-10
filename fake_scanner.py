
import sys

target = sys.argv[1]
print(f"Scanning target: {target}")

if target == "example.com_25":
    print("Simulating crash on chunk 2! EXITING.")
    sys.exit(-1)
else:
    sys.exit(0)
