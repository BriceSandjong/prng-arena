#include <iostream>
#include "../include/LCG.hpp"
#include "../include/Number.hpp"

int main(int argc, char *argv[]){
	if(argc == 5){
		argv[0] = NULL;

		Number numberList[argc-1];

		for (int i = 0; i < argc; i++) 
			if(argv[i] != NULL)
				numberList[i-1] = Number(argv[i]);

		LCG gen = LCG(numberList);
    std::cout << gen.generateNumber() << std::endl;
	} else {
		return 1;
	}

	return 0;
}
