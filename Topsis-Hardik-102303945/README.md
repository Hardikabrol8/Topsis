# Topsis-Hardik-102303945

A Python package to implement TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).

## Installation

```bash
pip install Topsis-Hardik-102303945
```

## Usage

This package can be used via the command line.

```bash
topsis <InputDataFile> <Weights> <Impacts> <ResultFileName>
```

### Arguments

1.  **InputDataFile**: Path to the input CSV file containing data.
    - First column should be the name/ID of the alternative.
    - Other columns must be numeric.
2.  **Weights**: Comma-separated numbers representing weights for each criterion (e.g., "1,1,1,2").
3.  **Impacts**: Comma-separated signs ('+' or '-') representing the impact of each criterion (e.g., "+,+,-,+").
4.  **ResultFileName**: Path where the result CSV will be saved.

### Example

```bash
topsis data.csv "1,1,1,1" "+,+,-,+" result.csv
```

## Output

The output file will contain the original data with two additional columns:
- **Topsis Score**: The calculated performance score.
- **Rank**: The ranking of the alternative.
