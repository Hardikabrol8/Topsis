import sys
import os
import pandas as pd
import numpy as np

def validate_inputs():
    # 1. Check number of parameters
    if len(sys.argv) != 5:
        print("Error: Incorrect number of parameters.")
        print("Usage: topsis <InputDataFile> <Weights> <Impacts> <OutputResultFileName>")
        print("Example: topsis data.csv \"1,1,1,1\" \"+,+,-,+\" result.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    weights_str = sys.argv[2]
    impacts_str = sys.argv[3]
    output_file = sys.argv[4]

    # 2. Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)

    return input_file, weights_str, impacts_str, output_file

def topsis_algorithm(input_file, weights_str, impacts_str, output_file):
    try:
        # Read the file
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            print(f"Error: Could not read file. {e}")
            sys.exit(1)

        # 3. Check number of columns (must be >= 3)
        if df.shape[1] < 3:
            print("Error: Input file must contain three or more columns.")
            sys.exit(1)

        # 4. Check for non-numeric values in 2nd to last columns
        # Taking a copy of the numeric part to work on
        df_numeric = df.iloc[:, 1:].copy()
        
        # Helper to check if values are numeric
        try:
            df_numeric = df_numeric.apply(pd.to_numeric)
        except ValueError:
            print("Error: From 2nd to last columns must contain numeric values only.")
            sys.exit(1)

        # Parsing weights and impacts
        try:
            weights = [float(w) for w in weights_str.split(',')]
            impacts = impacts_str.split(',')
        except ValueError:
            print("Error: Weights must be numeric and separated by commas.")
            sys.exit(1)

        # 5. Check if number of weights, impacts, and columns match
        num_cols = df_numeric.shape[1]
        if len(weights) != num_cols or len(impacts) != num_cols:
            print(f"Error: Number of weights ({len(weights)}), impacts ({len(impacts)}), and columns ({num_cols}) must be the same.")
            sys.exit(1)

        # 6. Check validation of impacts
        if not all([i in ['+', '-'] for i in impacts]):
            print("Error: Impacts must be either '+ve' (+) or '-ve' (-).")
            sys.exit(1)

        # --- TOPSIS Logic ---

        # Vector Normalization
        # r_ij = x_ij / sqrt(sum(x_ij^2))
        normalized_df = df_numeric.div(np.sqrt((df_numeric**2).sum()), axis=1)

        # Weighted Normalized Decision Matrix
        # v_ij = r_ij * w_j
        weighted_normalized_df = normalized_df.mul(weights, axis=1)

        # Ideal Best (V+) and Ideal Worst (V-)
        ideal_best = []
        ideal_worst = []

        for col_idx, col in enumerate(weighted_normalized_df.columns):
            if impacts[col_idx] == '+':
                ideal_best.append(weighted_normalized_df[col].max())
                ideal_worst.append(weighted_normalized_df[col].min())
            else: # Impact is '-'
                ideal_best.append(weighted_normalized_df[col].min())
                ideal_worst.append(weighted_normalized_df[col].max())

        # Euclidean Distance from Ideal Best (S+) and Ideal Worst (S-)
        # S_i+ = sqrt(sum((v_ij - v_j+)^2))
        s_plus = np.sqrt(((weighted_normalized_df - ideal_best) ** 2).sum(axis=1))
        
        # S_i- = sqrt(sum((v_ij - v_j-)^2))
        s_minus = np.sqrt(((weighted_normalized_df - ideal_worst) ** 2).sum(axis=1))

        # Performance Score
        # P_i = S_i- / (S_i+ + S_i-)
        # Handle division by zero if S_plus + S_minus is 0 (unlikely but possible)
        total_dist = s_plus + s_minus
        performance_score = np.divide(s_minus, total_dist, out=np.zeros_like(s_minus), where=total_dist!=0)

        # Add Score and Rank to the original dataframe
        df['Topsis Score'] = performance_score
        df['Rank'] = df['Topsis Score'].rank(ascending=False).astype(int)

        # Save output
        df.to_csv(output_file, index=False)
        print(f"Success: Output saved to {output_file}")

    except Exception as e:
        print(f"Error: An unexpected error occurred. {e}")
        sys.exit(1)

def main():
    input_file, weights, impacts, output_file = validate_inputs()
    topsis_algorithm(input_file, weights, impacts, output_file)

if __name__ == "__main__":
    main()
