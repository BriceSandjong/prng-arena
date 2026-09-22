from mt19937predictor import MT19937Predictor
from sys import argv

predictionLength = int(argv[2])

def main():
  predictor = MT19937Predictor()

  with open(argv[1], "r") as f:
    for i in f.readlines():
      value = int(i)
      predictor.setrandbits(value, 32)
      print(value)

  for i in range(0, predictionLength):
    print(predictor.getrandbits(32))

if __name__ == "__main__":
  main()