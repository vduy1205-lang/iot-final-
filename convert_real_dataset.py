import csv
import os
import shutil

SOURCE_CSV = "d:/do-an/scratch/kaggle_data/acc_gyr.csv"
OUTPUT_DIR = "d:/do-an/dataset"

# Backup old simulated data if any, or clear directory
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mapping from original labels to our 4 target labels
LABEL_MAP = {
    "fall": "te_nga",
    "rfall": "te_nga",
    "lfall": "te_nga",
    "walk": "di_bo",
    "light": "dung_ngoi",
    "sit": "dung_ngoi",
    "step": "loang_choang",
}

# Parameters for window slicing
WINDOW_SIZE = 100      # 100 samples per window (2.0 seconds at 50Hz)
WINDOW_STEP = 50       # 50% overlap (1.0 second step) for data augmentation

# Load all rows from CSV
rows_by_segment = []
current_label = None
current_rows = []

with open(SOURCE_CSV, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for r in reader:
        lbl = r[-1].strip()
        vals = [float(x) for x in r[:-1]] # xAcc, yAcc, zAcc, xGyro, yGyro, zGyro
        if lbl == current_label:
            current_rows.append(vals)
        else:
            if current_rows and current_label:
                rows_by_segment.append((current_label, current_rows))
            current_label = lbl
            current_rows = [vals]
    if current_rows and current_label:
        rows_by_segment.append((current_label, current_rows))

print(f"Loaded {len(rows_by_segment)} continuous segments of real human movement.")

# Process each segment and write CSV windows
file_counters = {
    "te_nga": 0,
    "di_bo": 0,
    "dung_ngoi": 0,
    "loang_choang": 0
}

# Max windows per class to keep the dataset balanced
MAX_WINDOWS_PER_CLASS = {
    "te_nga": 200,
    "di_bo": 150,
    "dung_ngoi": 150,
    "loang_choang": 100,
}

for orig_label, segment_data in rows_by_segment:
    target_label = LABEL_MAP.get(orig_label)
    if not target_label:
        continue
    
    n_samples = len(segment_data)
    step = WINDOW_STEP
    # For classes with lots of data (like dung_ngoi), take larger step to avoid over-sampling
    if target_label == "dung_ngoi":
        step = 100

    for start_idx in range(0, n_samples - WINDOW_SIZE + 1, step):
        if file_counters[target_label] >= MAX_WINDOWS_PER_CLASS[target_label]:
            break
        
        window = segment_data[start_idx : start_idx + WINDOW_SIZE]
        
        file_counters[target_label] += 1
        idx_str = f"{file_counters[target_label]:04d}"
        filename = f"{target_label}.real_{idx_str}.csv"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, "w", newline="", encoding="utf-8") as out_f:
            writer = csv.writer(out_f)
            writer.writerow(["timestamp", "accX", "accY", "accZ", "gyrX", "gyrY", "gyrZ"])
            for t_idx, sample in enumerate(window):
                timestamp_ms = t_idx * 20  # 50Hz = 20ms
                writer.writerow([timestamp_ms, sample[0], sample[1], sample[2], sample[3], sample[4], sample[5]])

print("\n" + "=" * 60)
print("  KET QUA CHUYEN DOI DATASET NGUOI THAT (KAGGLE IMU)")
print("=" * 60)
total_files = 0
for lbl, cnt in file_counters.items():
    duration_sec = cnt * 2.0
    print(f"  - {lbl:15s}: {cnt:4d} files CSV (~{duration_sec/60:.1f} phut)")
    total_files += cnt

print(f"\n  TONG CONG: {total_files} files CSV chua du lieu NGUOI THAT 100%")
print(f"  Thu muc: {OUTPUT_DIR}")
