import sys
import pylox

def main():
    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(1)
    elif len(sys.argv) == 2:
        print("Hi")
        pylox.run_file(sys.argv[1])
    else:
        pylox.run_prompt()

if __name__ == "__main__":
    main()