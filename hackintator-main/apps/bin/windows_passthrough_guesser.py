import sys


def main():
    if len(sys.argv) < 2:
        return

    input_path = sys.argv[1]
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            print(line.rstrip("\r\n"))


if __name__ == "__main__":
    main()
