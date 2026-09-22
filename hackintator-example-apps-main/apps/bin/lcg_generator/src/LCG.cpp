#include "../include/LCG.hpp"

LCG::LCG(int a, int c, int m, int x){
  setA(a);
  setC(c);
  setM(m);
  setX(x);
}

LCG::LCG(Number *nblist){
  setA(nblist[0].getInt());
  setC(nblist[1].getInt());
  setM(nblist[2].getInt());
  setX(nblist[3].getInt());
}

int LCG::generateNumber() const {
  return (getA() * getX() + getC()) % getM();
}

int LCG::getA() const {
  return a;
}

int LCG::getC() const {
  return c;
}

int LCG::getM() const {
  return m;
}

int LCG::getX() const {
  return x;
}

void LCG::setA(int a){
  this->a = a;
}

void LCG::setC(int c){
  this->c = c;
}

void LCG::setM(int m){
  this->m = m;
}

void LCG::setX(int x){
  this->x = x;
}
