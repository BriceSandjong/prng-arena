#pragma once
#include "Number.hpp"

class LCG {
  private:
    int a;
    int c;
    int m;
    int x;
  protected:
    void setA(int a);
    void setC(int c);
    void setM(int m);
    void setX(int x);
  public:
    LCG(int a, int c, int m, int x);
    LCG(Number *nblist);
    int generateNumber() const;
    int getA() const;
    int getC() const;
    int getM() const;
    int getX() const;
};
