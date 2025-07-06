import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import re
import sys

# Logger that writes to both console and file
class DualLogger:
    def __init__(self, filename):
        self.console = sys.stdout
        self.file = open(filename, 'w', encoding='utf-8')

    def write(self, message):
        self.console.write(message)
        self.file.write(message)

    def flush(self):
        self.console.flush()
        self.file.flush()

def load_drop_data():
    df = pd.read_csv("silkroadBoxDropRates.csv")
    df['Drop Rate'] = df['Drop Rate'].str.replace('%', '').astype(float)
    df['Probability'] = df['Drop Rate'] / df['Drop Rate'].sum()
    df['Full Item'] = df['Item Name (Korean)'] + f" x" + df['Qty'].astype(str)
    return df

def simulate_box_opening(df, num_boxes):
    print(f"\nOpening {num_boxes} boxes...\n")

    items = df['Full Item']
    probabilities = df['Probability']

    drops = np.random.choice(items, size=num_boxes, p=probabilities)

    for i, item in enumerate(drops, 1):
        print(f"Box {i}: {item}")

    drop_counts = Counter(drops)

    print("\n=== Drop Summary ===")
    for item, count in drop_counts.items():
        rate = (count / num_boxes) * 100
        print(f"{item}: {count} times ({rate:.2f}%)")

    # Group by base item
    grouped_totals = defaultdict(int)
    base_drop_rates = defaultdict(list)
    quantity_pattern = re.compile(r"(.+?) x(\d+)$")

    for _, row in df.iterrows():
        match = quantity_pattern.match(row['Full Item'])
        if match:
            base_name, _ = match.groups()
            base_drop_rates[base_name].append(row['Drop Rate'])

    for full_item, count in drop_counts.items():
        match = quantity_pattern.match(full_item)
        if match:
            base_name, qty = match.groups()
            grouped_totals[base_name] += int(qty) * count

    # Manual exclusions
    special_items = ['Secret Key', 'Element of Destruction']

    # Sort regular items by lowest drop rate
    sorted_items = sorted(
        [(item, qty) for item, qty in grouped_totals.items() if item not in special_items],
        key=lambda x: min(base_drop_rates[x[0]])
    )

    # Add special items at the end
    for item in special_items:
        if item in grouped_totals:
            sorted_items.append((item, grouped_totals[item]))

    print("\n=== Grouped Total Quantities Obtained (Sorted by Drop Rate) ===")
    for base_item, total_qty in sorted_items:
        print(f"{base_item}: {total_qty}")

if __name__ == "__main__":
    sys.stdout = DualLogger("silkroadBoxSimulator_outcome.txt")
    df = load_drop_data()
    simulate_box_opening(df, 1000)