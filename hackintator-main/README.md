# Hack'Int'Ator

## Overview
Hack'Int'Ator compares PRNG generators and guessers/predictors independently of their implementation language.
It runs both algorithms, normalizes outputs, and writes results in a consistent CSV format.

Minimal example:

```bash
./output/main -g my_generator -p my_guesser -n 1000
```

## Build With CMake

### Prerequisites
- CMake >= 3.16
- A C++17 compiler

### Configure + Build

From the project root (`hackintator-main`):

```bash
rmdir /s /q build (=> delete the build folder in the project : because you need your own build folder with your parameters)
cmake -S . -B build (=> create your own build folder)
cmake --build build --config Release (=> config the folder for you)
```

Output binary is generated in `output/`:
- Windows: `output/main.exe`
- Linux/macOS: `output/main`

### Notes
- `CMakeLists.txt` forces runtime output to `output/` for all build configs.
- On Windows, `psapi` is linked automatically.

## Install Python Packages 

From the project root (`hackintator-main`):

In Windows Powershell :

```bash
pip install z3-solver
pip install sympy
```

Or in Visual Studio Code Terminal :

```bash
python -m pip install z3-solver
python -mpip install sympy
```

## Core CLI Usage

```bash
./output/main -g <generator_profile> -p <guesser_profile> -n <iterations>
```

Useful options:
- `-ag "..."`: generator arguments
- `-ap "..."`: guesser arguments
- `-ns <int>`: optional source size
- `-h`: help

## INI Profiles

Each algorithm needs a profile in `apps/*.ini`.

### Common keys
- `cmd`: command to execute (required)
- `output`: `console` or file path (required)
- `line_filter`: regex to keep only useful lines
- `delimiter`: value delimiter
- `start_line`, `end_line`: output slicing

### Guesser-specific keys
- `input_format`: format regex used to parse guesser output
- `repeat`: `true` / `false`

### Placeholders
In `cmd`:
- `%args%`
- `%generator_output_file%`
- `%generator_output_to_separate_args%`
- `%generator_output_to_string%`

In `input_format`:
- `%data%`

### Example profiles

Generator:

```ini
cmd = python apps/bin/lcg_generator_runner.py
output = console
line_filter = ^.*$
delimiter =
start_line =
end_line =
```

Guesser:

```ini
cmd = apps/bin/lcg-periodfinder/output/main %generator_output_file%
output = console
input_format = %data%\n
repeat = true
```

Sample profiles repository:
https://github.com/FF108/hackintator-example-apps

## Launcher (Global Behavior)

To start the launcher :

- You can just simply start the HackintatorLauncher.exe (in \exe folder)

- Or write in your powerShell => in the root (`hackintator-main`) => "python launcher_ui.py"

What it does:
1. Detects profiles from `apps/*.ini`:
    - `*_generator` as generators
    - `*_guesser` as guessers
2. Lets you select multiple generators and guessers (scrollable lists, select/unselect all).
3. Runs a full batch: cartesian product generator x guesser.
4. For each run, executes `output/main(.exe)` with your UI parameters.
5. Archives each result in `batch_results/<timestamp>/` as:
    - `results_<generator>_vs_<guesser>.csv`
    - `SUMMARY.txt`

Launcher buttons:
- `Lancer Batch`: run all selected combinations
- `Ouvrir results.csv`: open latest result file
- `Ouvrir archive batch`: open `batch_results`
- `Rafraichir profils`: rescan `apps/*.ini`
- `voir les statistiques`: open stats app

Stats app resolution from launcher:
- In launcher EXE mode, it prefers `Visual/exe/BatchResultsViewer.exe`
- Fallbacks include `Visual/exe/BatchResultsViewer.exe` and `Visual/BatchResultsViewer.exe`
- In Python mode, it runs `Visual/InterfaceView.py`

## Stats App (Batch Results Viewer)

Stats UI file: `Visual/InterfaceView.py` (packaged as `BatchResultsViewer.exe`).

Main features:
1. Detects a `batch_results` root automatically (or lets you choose one).
2. Lists batch folders and contained `results_*_vs_*.csv` files.
3. Lets you select CSV files for analysis.
4. Computes aggregated metrics:
    - average accuracy/error
    - average time, CPU, memory
    - predictor ranking
    - best predictor per generator
5. Generates PNG charts from selected CSV files.
6. Can open the last generated PNG directly.

Expected input structure:
- `batch_results/<batch_id>/results_*_vs_*.csv`

## AI-Powered Guessers (Ollama)

This platform includes integration with **Ollama**, a local LLM inference engine, allowing you to test whether Large Language Models can predict PRNG sequences.

### Available LLM Models

Three pre-configured Ollama guessers are available:

- **ollama_mistral_guesser**: Uses Mistral 7B model (4.4 GB) - Fast, general-purpose language model
- **ollama_gemma4_guesser**: Uses Gemma 4 model (9.6 GB) - Stronger mathematical reasoning
- **ollama_qwen_guesser**: Uses Qwen 3.5 model (6.6 GB) - Multilingual, code-aware

### How Ollama Guessers Work

1. **Number Extraction**: The guesser reads the generated numbers from the generator's output
2. **Context Preparation**: Sends the last 10 numbers to the LLM with the prompt "Next 3:"
3. **API Query**: Makes an HTTP request to Ollama API (`http://localhost:11434/api/generate`)
4. **Prediction**: Extracts the 3 predicted numbers from the LLM's response
5. **Cycling**: Repeats the 3 predictions to match the input length (1 prediction per input number)
6. **Fallback**: If Ollama is unavailable or times out, outputs the original numbers

### Setup Requirements

1. **Install Ollama**: Download from [ollama.ai](https://ollama.ai)
2. **Run Ollama Server**: `ollama serve`
3. **Download Models** (one-time setup):
    ```bash
    ollama pull mistral
    ollama pull gemma
    ollama pull qwen
    ```
4. **Verify**: `ollama list` should show all 3 models

### Usage Example

```bash
./output/main -g windows_lcg_generator -p ollama_mistral_guesser -n 100
```

### Expected Accuracy

- **Mistral, Gemma4, Qwen**: ~1% match ratio (expected behavior)
- **Why so low?** PRNGs are deterministic mathematical algorithms; LLMs perform statistical pattern matching and cannot replicate cryptographic properties
- **Research Value**: This demonstrates that LLMs fundamentally cannot predict PRNGs - they require algorithmic analysis, not pattern recognition

### Performance Characteristics

| Model | Size | Speed | Memory | Best For |
|-------|------|-------|--------|----------|
| Mistral | 4.4 GB | Fast (~2-3s per query) | Moderate | Quick testing |
| Gemma4 | 9.6 GB | Slow (~5-10s per query) | High | Detailed analysis |
| Qwen | 6.6 GB | Medium (~3-5s per query) | Moderate | Balanced approach |

### Implementation Details

The Ollama guessers are implemented in Python and use the standard library `urllib` for HTTP communication (no external dependencies). Each guesser:

- Reads generator output file
- Extracts all integer values with regex
- Sends JSON request to Ollama: `{"model": "mistral", "prompt": "Next 3:[...numbers...]", "stream": false}`
- Cycles predictions across all input numbers
- Gracefully handles timeouts and network errors

## Output Files

Generated in `output/`:
- `main` / `main.exe`: core executable
- `generator.output`: raw generator output
- `generator.output.formatted`: normalized generator output
- `guesser.output`: guesser output
- `results.csv`: final comparison result

`results.csv` format:
- Line 0: command used
- Line 1: `generated;guessed;generated;guessed;...`
- Line 2: match ratio
- Line 3: execution time (seconds)
- Line 4: CPU usage (%)
- Line 5: memory usage (kB)

## Internal Architecture

- `Comparator`: orchestrates runs and writes comparison output
- `Generator` / `Guesser`: derived from `Algorithm`
- `InterfaceConsole` / `InterfaceSystem`: console vs file-based integration
- `AlgoConfig`: parses INI configuration
- `OutputReader`: parses algorithm output according to profile rules


