import tkinter as tk
from tkinter import scrolledtext, messagebox
import csv
import random

CSV_FILE = 'silkroadBoxDropRates.csv'
OUTPUT_FILE = 'silkroadBoxSimulator_outcome.txt'

def simulate_drops():
    try:
        num_boxes = int(entry.get())
        if num_boxes <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a positive integer for number of boxes.")
        return

    items = []
    probabilities = []
    drop_rate_map = {}

    # Load drop rates from CSV and build item list + drop rate map
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = row['Item'].strip().replace("Secret Flame", "Secret Key")
            drop_rate_percent = float(row['Drop Rate'].strip('%'))
            quantity = int(row['Quantity'])
            items.append((item, quantity))
            probabilities.append(drop_rate_percent / 100)
            drop_rate_map[item] = drop_rate_percent

    results = []
    detailed_drops = []
    for _ in range(num_boxes):
        selected = random.choices(items, weights=probabilities, k=1)[0]
        results.append(selected)
        detailed_drops.append(f"Box: {selected[0]} x{selected[1]}")

    summary = {}
    grouped = {}
    for item, qty in results:
        summary[(item, qty)] = summary.get((item, qty), 0) + 1
        grouped[item] = grouped.get(item, 0) + qty

    # Summary (Item + Qty) sorted by drop count and keep special items last
    sorted_summary = sorted(
        [(item, qty, count) for (item, qty), count in summary.items() if count > 0],
        key=lambda x: (x[0] in ['Secret Key', 'Element of Destruction'], x[2] * x[1])
    )

    # Grouped Totals sorted by CSV drop rate (ascending), special items last
    special_items = ['Secret Key', 'Element of Destruction']
    sorted_grouped = sorted(
        grouped.items(),
        key=lambda x: (x[0] in special_items, drop_rate_map.get(x[0], float('inf')))
    )

    output_lines = [f"Opening {num_boxes} boxes...", ""]
    output_lines.extend(detailed_drops)

    output_lines.append("\nSummary (Grouped by Item and Quantity):")
    for item, qty, count in sorted_summary:
        percent = (count / num_boxes) * 100
        output_lines.append(f"{item} x{qty}: {count} times ({percent:.2f}%)")

    output_lines.append("\nTotal Quantities Obtained (Grouped by Item):")
    for item, total_qty in sorted_grouped:
        output_lines.append(f"{item}: {total_qty}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for line in output_lines:
            f.write(line + "\n")

    text_area.delete(1.0, tk.END)
    for line in output_lines:
        text_area.insert(tk.END, line + "\n")

# --- GUI Setup ---

root = tk.Tk()
root.title("Silkroad Box Simulator")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

entry_label = tk.Label(frame, text="Number of Boxes:")
entry_label.grid(row=0, column=0, padx=5, pady=5)

entry = tk.Entry(frame, width=10)
entry.grid(row=0, column=1, padx=5, pady=5)
entry.insert(0, "50")

btn = tk.Button(frame, text="Open Boxes", command=simulate_drops)
btn.grid(row=0, column=2, padx=10)

text_area = scrolledtext.ScrolledText(root, width=80, height=30, wrap=tk.WORD)
text_area.pack(padx=10, pady=10)

root.mainloop()
