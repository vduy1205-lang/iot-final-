import os
import sys
import time
import glob

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("Vui long cai pyserial bang lenh: pip install pyserial")
    sys.exit(1)

DATASET_DIR = "dataset"

def ensure_dataset_dir():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

def list_serial_ports():
    ports = list(serial.tools.list_ports.comports())
    return [p.device for p in ports]

def main():
    ensure_dataset_dir()
    print("=" * 60)
    print("  CONG CU THU THAP DU LIEU TINYML (ESP32 + MPU6050)")
    print("  Tuong thich chuan 100% voi Edge Impulse Studio")
    print("=" * 60)

    ports = list_serial_ports()
    if not ports:
        print("\n[!] Khong tim thay cong COM nao! Vui long cam cap USB ESP32 vao laptop.")
        input("\nNhan Enter de thoat...")
        return

    print("\nDanh sach cong COM tim thay:")
    for i, p in enumerate(ports):
        print(f"  [{i+1}] {p}")

    if len(ports) == 1:
        selected_port = ports[0]
        print(f"\n-> Tu dong chon: {selected_port}")
    else:
        choice = input(f"\nChon cong COM [1-{len(ports)}]: ").strip()
        try:
            selected_port = ports[int(choice) - 1]
        except:
            selected_port = ports[0]

    baudrate = 115200
    try:
        ser = serial.Serial(selected_port, baudrate, timeout=1)
        print(f"[+] Da ket noi thanh cong voi {selected_port} o baudrate {baudrate}")
    except Exception as e:
        print(f"[!] Loi mo cong COM: {e}")
        return

    labels = ["dung_ngoi", "di_bo", "loang_choang", "te_nga"]

    while True:
        print("\n" + "-" * 50)
        print("DANH SACH CAC NHAN (LABELS):")
        for i, lbl in enumerate(labels):
            print(f"  [{i+1}] {lbl}")
        print("  [5] Nhap nhan tuy chon khac")
        print("  [0] Thoat chuong trinh")
        print("-" * 50)

        choice = input("Chon nhan muon thu [0-5]: ").strip()
        if choice == "0":
            break
        elif choice in ["1", "2", "3", "4"]:
            label = labels[int(choice) - 1]
        elif choice == "5":
            label = input("Nhap ten nhan moi: ").strip().replace(" ", "_")
        else:
            print("[!] Lua chon khong hop le!")
            continue

        duration_str = input("Thoi gian thu mau moi lan (giay, mac dinh 10s): ").strip()
        duration_sec = int(duration_str) if duration_str.isdigit() and int(duration_str) > 0 else 10

        print(f"\n-> Chuan bi thu nhan: [{label}] trong {duration_sec} giay...")
        for count in range(3, 0, -1):
            print(f"   Bat dau sau: {count} giay...")
            time.sleep(1)

        print("\n>>> DANG THU DU LIEU (Thuc hien dong tac ngay)... <<<")
        ser.reset_input_buffer()

        samples = []
        start_time = time.time()
        timestamp_ms = 0
        last_print = 0

        while (time.time() - start_time) < duration_sec:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                parts = line.split(",")
                if len(parts) == 6:
                    try:
                        vals = [float(x) for x in parts]
                        samples.append([timestamp_ms] + vals)
                        timestamp_ms += 20  # 50Hz = 20ms per sample
                    except ValueError:
                        pass
            
            elapsed = int(time.time() - start_time)
            if elapsed != last_print:
                last_print = elapsed
                remaining = duration_sec - elapsed
                print(f"   Dang thu... con lai {remaining}s (Da ghi {len(samples)} mau)", end="\r")

        print(f"\n[v] HOAN TAT! Tong so mau thu duoc: {len(samples)} mau.")

        if len(samples) > 0:
            timestamp_str = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{label}.{timestamp_str}.csv"
            filepath = os.path.join(DATASET_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("timestamp,accX,accY,accZ,gyrX,gyrY,gyrZ\n")
                for s in samples:
                    f.write(f"{s[0]},{s[1]},{s[2]},{s[3]},{s[4]},{s[5]},{s[6]}\n")

            print(f"[+] Da luu file: {filepath}")
            print(f"    (File nay san sang de upload thang len Edge Impulse Studio)")
        else:
            print("[!] Canh bao: Khong nhan duoc du lieu nao tu ESP32. Kiem tra lai day noi hoac baudrate.")

    ser.close()
    print("\nDa dong ket noi. Cam on ban!")

if __name__ == "__main__":
    main()
