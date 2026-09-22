## How to build

Just use the `make` command inside the project folder.

## How to use
You must have 4 arguments

$X_{n+1} = (aX_n + c) \bmod m$

Based on this formula, we have 4 variables : *a*, *x*, *c* and *m*.
```
$ lcg_generator.exe <a> <c> <m> <x>
```
Replace each <> with the wanted value, and the next value is returned inside a file called **output.txt**.
