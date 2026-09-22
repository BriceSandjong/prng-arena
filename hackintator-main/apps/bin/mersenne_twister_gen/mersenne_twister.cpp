#include <random>
#include <iostream>

int main(int argc, char *argv[]){
  if(argc == 3){
    std::mt19937 mt(atoi(argv[1]));

    for (int i = 1; i <= atoi(argv[2]); i++) {
      std::cout << mt() << " ";
    }
    std::cout << std::endl;
  } else {
    return 1;
  }

  return 0;
}