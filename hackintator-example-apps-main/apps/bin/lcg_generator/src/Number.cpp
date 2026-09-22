#include "../include/Number.hpp"
#include <cmath>

Number::Number(char *nb){
  this->nb = nb;
}

Number::Number(){
  this->nb = 0;
}

int Number::getInt() const {
  return convertToInt();
}

int Number::getSizeCharString() const {
  int i = 0;
  while(nb[i] != '\0')
    i++;
  return i;
}

int Number::convertToInt() const {
  int newNb = 0;
  int size = getSizeCharString();

  for(int i = 0 ; i < size ; i++)
    newNb += (nb[i] - 48) * pow(10, size-1-i);

  return newNb;
}