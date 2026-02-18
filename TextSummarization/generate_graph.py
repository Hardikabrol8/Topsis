import matplotlib.pyplot as plt
import pandas as pd

def generate_graph(input_file, output_image):
    try:
        df = pd.read_csv(input_file)
        
        # Sort by Rank for better visualization (Number 1 on top/first)
        df_sorted = df.sort_values(by='Rank')
        
        plt.figure(figsize=(10, 6))
        bars = plt.barh(df_sorted['Model'], df_sorted['Topsis Score'], color='skyblue')
        plt.xlabel('TOPSIS Score')
        plt.ylabel('Model')
        plt.title('Comparison of Text Summarization Models using TOPSIS')
        plt.gca().invert_yaxis() # Highest rank at top
        
        # Add scores to bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width, bar.get_y() + bar.get_height()/2, f'{width:.4f}', 
                     ha='left', va='center')
            
        plt.tight_layout()
        plt.savefig(output_image)
        print(f"Graph saved to {output_image}")
        
    except Exception as e:
        print(f"Error generating graph: {e}")

if __name__ == "__main__":
    generate_graph('result.csv', 'topsis_graph.png')
