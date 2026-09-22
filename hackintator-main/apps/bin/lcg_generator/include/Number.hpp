#pragma once

class Number {
  private:
    char *nb;
    int getSizeCharString() const;
    int convertToInt() const;
  public:
    Number(char *nb);
    Number();
    int getInt() const;
};