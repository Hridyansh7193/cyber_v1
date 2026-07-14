import sys
import time

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
        
    mode = sys.argv[1]
    
    if mode == "normal":
        print("stdout line 1", flush=True)
        print("stderr line 1", file=sys.stderr, flush=True)
        sys.exit(0)
        
    elif mode == "error":
        sys.exit(42)
        
    elif mode == "timeout":
        print("stdout before timeout", flush=True)
        print("stderr before timeout", file=sys.stderr, flush=True)
        # Sleep to force a timeout
        time.sleep(10)
        # Should not be reached
        print("stdout after timeout", flush=True)
        
    elif mode == "crash":
        # Simulate an immediate crash
        raise Exception("Fatal crash")

if __name__ == "__main__":
    main()
