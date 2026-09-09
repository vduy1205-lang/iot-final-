# ĐẶC TẢ KỸ THUẬT HỆ THỐNG IoT GIÁM SÁT SỨC KHỎE & PHÁT HIỆN TÉ NGÃ
### (Quy Mô 1 Người Cụ Thể • 1 Phòng Ngủ & Sân Vườn Mini • 100% Wi-Fi Nội Bộ • Không Dùng LoRa)

---

## 1. Phạm Vi & Bối Cảnh Hệ Thống

* **Đối tượng phục vụ:** Giám sát an toàn cho **01 người cao tuổi (Cụ A)** sống tại **01 phòng ngủ độc lập**, có khu vực sinh hoạt mở rộng ra **sân vườn mini** liền kề.
* **Môi trường vô tuyến:**
  * Toàn bộ khuôn viên (phòng ngủ + sân vườn mini, bán kính hoạt động $\le 50 - 80\text{m}$) được phủ kín bởi **01 mạng Wi-Fi 2.4GHz duy nhất** (cùng tên SSID, cùng mật khẩu, cùng dải mạng con LAN `192.168.1.0/24`).
  * **Không sử dụng LoRa, không dùng SIM 4G di động** nhằm tối ưu chi phí, giảm trọng lượng đai đeo và đồng nhất hạ tầng mạng cục bộ.
* **Mô hình máy chủ phân tán 2 tầng:**
  * **Cấp 1 - Máy chủ biên cục bộ (Local Edge Server):** Bo mạch **ESP32 Đầu Giường**. Trực tiếp xử lý cảm biến có dây, điều khiển còi tại phòng, yêu cầu chụp ảnh từ Camera góc phòng và quản lý an toàn trực tiếp cho Cụ A.
  * **Cấp 2 - Máy chủ hiển thị trung tâm (Central Web Dashboard):** Máy tính đặt tại bàn trực của điều dưỡng/y tá, kết nối chung mạng Wi-Fi, hiển thị giao diện thời gian thực và lưu trữ lịch sử sự kiện.

---

## 2. Kiến Trúc Chuẩn 4 Tầng IoT (Khớp 100% Khung Ảnh Viết Tay)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. TẦNG VẬT LÝ & LIÊN KẾT DỮ LIỆU (PHYSICAL & LINK LAYER)                              │
│    ├── CẢM BIẾN (SENSORS) - 3 CỤM ĐẶT TẠI 3 VỊ TRÍ ĐỘC LẬP:                            │
│    │   ├── [1] Cụm cảm biến có dây cố định (Wired Station): MAX30102 nối cáp I2C       │
│    │   │       trực tiếp vào ESP32 đặt tại trạm đầu giường                             │
│    │   ├── [2] Cụm nút cảm biến di động không dây (Wireless Wearable Node):            │
│    │   │       MPU6050 gắn trên đai đeo bụng di động, toàn cụm chạy pin Li-Po,         │
│    │   │       truyền toàn bộ dữ liệu ra ngoài qua sóng vô tuyến Wi-Fi                 │
│    │   └── [3] Cụm cảm biến thị giác (Vision Node): Camera OV2640 trên ESP32-CAM       │
│    ├── CƠ CẤU CHẤP HÀNH (ACTUATORS):                                                   │
│    │   ├── Còi Buzzer 1 (Active 5V): Đặt trên đai đeo bụng (kêu ngắt quãng SOS tại chỗ)│
│    │   ├── Còi Buzzer 2 (Active 5V): Đặt tại đầu giường (bíp 100ms khi đo SpO2 xong,   │
│    │   │   hú còi dồn dập tại phòng khi xảy ra sự cố té ngã)                           │
│    │   └── Loa/Còi cảnh báo âm thanh tại máy tính bàn trực điều dưỡng                  │
│    └── PHƯƠNG TIỆN TRUYỀN DẪN VẬT LÝ:                                                  │
│        ├── Cáp đồng I2C vật lý: Nối cảm biến MAX30102 với ESP32 đầu giường (400kHz)   │
│        └── Sóng vô tuyến vô tuyến Wi-Fi 2.4GHz (Chuẩn IEEE 802.11 b/g/n)               │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. TẦNG INTERNET (INTERNET / NETWORK LAYER)                                            │
│    ├── Giao thức cốt lõi: Giao thức mạng Internet IPv4 (Internet Protocol v4)          │
│    ├── Cơ chế định địa chỉ: Cấp phát dải IP tĩnh nội bộ (Static IP Subnet 192.168.1.0/24)│
│    │   giúp các nút giao tiếp trực tiếp ngang hàng mà không phụ thuộc DHCP server      │
│    ├── Định tuyến cục bộ: Default Gateway (Router nội bộ 192.168.1.1)                   │
│    └── Khả năng kết nối Internet công cộng (Public WAN/Internet):                      │
│        • Chế độ vận hành chuẩn: Toàn bộ điều khiển khẩn cấp chạy độc lập trong LAN     │
│        • Kênh mở rộng Internet: Router kết nối Internet qua cáp quang/4G Gateway để    │
│          đồng bộ trạng thái lên Web Cloud hoặc gửi thông báo tới điện thoại người nhà  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. TẦNG TRUYỀN VẬN (TRANSPORT LAYER)                                                   │
│    ├── Giao thức chính: TCP (Transmission Control Protocol)                            │
│    │   • Cơ chế: Hướng kết nối (Connection-oriented), bắt tay 3 bước, bảo đảm toàn vẹn │
│    │     dữ liệu (gói tin báo ngã, ảnh snapshot và kết quả SpO2 không bị rớt gói)     │
│    │   • Quản lý cổng (Port Management):                                               │
│    │     - Cổng 80: Dịch vụ HTTP Web Server trên ESP32 Đầu giường và ESP32-CAM         │
│    │     - Cổng 1883: Kênh truyền thông điệp MQTT Broker nội bộ                        │
│    │     - Cổng 3000 / 8080: Máy chủ Web Dashboard trung tâm                           │
│    └── Giao thức bổ trợ: UDP (User Datagram Protocol)                                  │
│        • Sử dụng cho các bản tin quảng bá trạng thái nhanh (Discovery / Broadcast)     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. TẦNG ỨNG DỤNG (APPLICATION LAYER)                                                   │
│    ├── CÁC GIAO THỨC TẦNG ỨNG DỤNG (APPLICATION PROTOCOLS):                           │
│    │   ├── HTTP REST API: Đai gửi POST JSON báo ngã; Đầu giường gửi GET /capture kéo ảnh│
│    │   ├── HTTP Stream: Truyền luồng hình ảnh chuyển động MJPEG từ Camera lên Web      │
│    │   ├── MQTT Protocol: Trao đổi dữ liệu dạng Publish/Subscribe qua JSON nhẹ         │
│    │   └── WebSocket (ws://): Đẩy dữ liệu thời gian thực hai chiều lên trình duyệt Web │
│    └── PHẦN MỀM & GIAO DIỆN ỨNG DỤNG:                                                  │
│        ├── Firmware nhúng: Hệ điều hành thời gian thực FreeRTOS trên ESP32             │
│        ├── Back-end: Local Server xử lý logic sự kiện, phân loại rủi ro và lưu trữ DB  │
│        └── Front-end: Web Dashboard hiển thị trực quan cho nhân viên y tế giám sát     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Sơ Đồ Khối Tổng Quan Hệ Thống (Mô Hình 1 Cụ A / 1 Phòng & Sân Vườn)

```
            ┌───────────────────────────────────────────────┐
            │   ROUTER WI-FI VIỆN DƯỠNG LÃO (192.168.1.1)   │
            │   (Phủ sóng 2.4GHz: Phòng Cụ A & Sân vườn)    │
            └───────┬───────────────────────────────┬───────┘
                    │                               │ (Wi-Fi)
                    │ (Wi-Fi)                       ▼
                    ▼                 ┌───────────────────────────┐
┌───────────────────────────────────┐ │    KHU VỰC SÂN VƯỜN       │
│        PHÒNG NGỦ CỦA CỤ A         │ │ • Cụ A đi dạo ngoài sân   │
│                                   │ │ • Đai phát còi SOS & gửi  │
│  [ Cảm biến SpO2 MAX30102 ]       │ │   báo ngã thẳng về Server │
│         │ (Cáp I2C có dây)        │ └─────────────┬─────────────┘
│         ▼                         │               │
│  ┌─────────────────────────────┐  │               │
│  │ ESP32 ĐẦU GIƯỜNG (IP .50)   │  │               │
│  │ (Edge Server - Còi D25)     │  │               │
│  └───▲─────────────────────┬───┘  │               │
│      │                     │      │               │
│  (1) │ Wi-Fi POST          │ (2)  │               │
│      │ báo ngã             │ GET  │               │
│      │                     │/cap  │               │
│  ┌───┴──────────┐   ┌──────▼───┐  │               │
│  │ ĐAI LƯNG     │   │ ESP32-CAM│  │               │
│  │ (IP .70)     │   │ (IP .60) │  │               │
│  │ Còi SOS D4   │   │ Port 80  │  │               │
│  └──────────────┘   └──────┬───┘  │               │
└──────────────┬─────────────┼──────┘               │
               │ (3)         │ (4)                  │ (5)
               │ Dữ liệu     │ Luồng Video          │ Báo ngã
               │ tổng hợp    │ /stream              │ ngoài sân
               ▼             ▼                      ▼
┌───────────────────────────────────────────────────────────┐
│        MÁY CHỦ TRUNG TÂM & WEB DASHBOARD (IP .200)        │
│       • Node.js Express + SQLite (Cổng TCP 3000)          │
│       • Theo dõi SpO2, nhịp tim, dáng đi & ảnh ngã        │
│       • Chuông cảnh báo y tá & nút tắt còi từ xa          │
└───────────────────────────────────────────────────────────┘
```

---

## 4. Danh Mục Linh Kiện Phần Cứng (BOM Cho 1 Cụ / 1 Phòng)

| STT | Thiết bị | Vị trí | Linh kiện chi tiết | Vai trò trong hệ thống IoT |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Cụm Nút Đai Lưng Di Động**<br>*(Wireless Wearable Sensor Node)* | Cụ A đeo quanh thắt lưng | • 01 Bo mạch **ESP32 NodeMCU 30-pin**<br>• 01 Module cảm biến gia tốc **MPU6050** (giao tiếp I2C nội bộ với ESP32)<br>• 01 Còi **Active Buzzer 5V** (Chân D4)<br>• 01 Pin sạc **Li-Po 3.7V (1200 - 2000mAh)**<br>• 01 Mạch sạc pin **TP4056 Type-C**<br>• 01 Mạch kích áp **MT3608** (kích lên 5V)<br>• Vỏ hộp in 3D kèm đai co giãn | Đóng vai trò **Nút cảm biến không dây di động**. Thu thập chuyển động, phát hiện ngã bằng thuật toán gia tốc, hú còi SOS tại chỗ và truyền tin không dây qua Wi-Fi. |
| **2** | **Trạm Đầu Giường & Cảm Biến Cố Định**<br>*(Wired Station & Local Edge Server)* | Bàn/tường cố định đầu giường Cụ A | • 01 Bo mạch **ESP32 NodeMCU 30-pin**<br>• 01 Cảm biến **MAX30102** đo nhịp tim/SpO2<br>• 01 Dây bẹ 4 sợi kéo dài ($1.0 - 1.5\text{m}$)<br>• 01 Còi **Active Buzzer 5V** (Chân D25)<br>• 01 Nguồn Adapter 5V-2A cắm điện 220V | Đóng vai trò **Cụm cảm biến có dây** (MAX30102 nối dây bẹ) kết hợp **Máy chủ biên cục bộ** (Edge Server): bíp 100ms khi đo SpO2 xong, hú còi phòng và chủ động kéo ảnh Camera khi có ngã. |
| **3** | **Cụm Cảm Biến Thị Giác**<br>*(Vision Sensor Node)* | Góc cao trần phòng ngủ | • 01 Bo mạch **ESP32-CAM** (Kèm camera OV2640)<br>• 01 Đế nạp & cấp nguồn **ESP32-CAM-MB microUSB**<br>• 01 Củ sạc 5V-2A cắm điện liên tục | Đóng vai trò **Cảm biến thị giác (Camera)**: Cung cấp endpoint chụp ảnh tĩnh tức thời (`/capture`) và luồng video trực tiếp (`/stream`). |
| **4** | **Hạ Tầng Internet & Máy Chủ Ứng Dụng** | Bàn trực điều dưỡng | • 01 **Router Wi-Fi chuẩn 802.11n/ac** (Cổng WAN kết nối Internet, LAN cấp phát dải IP tĩnh `192.168.1.0/24`)<br>• 01 **Laptop / PC** chạy trình duyệt Web Dashboard | Thiết lập tầng Internet và vận hành Tầng ứng dụng (Back-end Server + Web Dashboard). |

---

## 5. Đặc Tả Tầng Internet & Bảng Phân Bổ Địa Chỉ IP (Internet Layer Specification)

Hệ thống sử dụng không gian địa chỉ **IPv4 Private Subnet `192.168.1.0/24`** với `Subnet Mask: 255.255.255.0` và `Default Gateway: 192.168.1.1`:

| Thiết bị | Vai trò mạng | Địa chỉ IP tĩnh | Cổng TCP phục vụ | Chức năng ở Tầng Internet / Transport |
| :--- | :--- | :---: | :---: | :--- |
| **Router Wi-Fi** | Gateway định tuyến LAN/WAN | `192.168.1.1` | - | Định tuyến nội bộ và chuyển tiếp gói tin ra Internet công cộng (WAN). |
| **ESP32 Đầu Giường** | Local Edge Server (Node có dây) | `192.168.1.50` | `80 (TCP)` | Lắng nghe gói tin báo ngã từ đai lưng, phục vụ REST API cục bộ. |
| **ESP32-CAM** | Vision Sensor Node | `192.168.1.60` | `80 (TCP)` | Cung cấp dịch vụ HTTP Server trả ảnh JPEG qua TCP stream. |
| **Đai Lưng ESP32** | Wireless Sensor Node | `192.168.1.70` | Client | Thiết lập kết nối TCP Socket bắn HTTP POST đến Đầu giường/Server. |
| **Máy Chủ Web PC** | Central Application Server | `192.168.1.200` | `3000 (TCP)` | Chạy máy chủ Web Dashboard, nhận kết nối WebSocket từ trình duyệt. |

---

## 6. Chi Tiết Giao Thức Giao Tiếp Theo Từng Kịch Bản Hoạt Động

### Kịch bản 1: Cụ A ngồi tại giường đo SpO2 và nhịp tim
* **Hiện trường:** Cụ A áp ngón tay vào cảm biến MAX30102 tại đầu giường.
* **Giao thức:**
  * MAX30102 $\longrightarrow$ ESP32 Đầu giường: **Giao thức I2C phần cứng** (`SDA: GPIO 21`, `SCL: GPIO 22`, tốc độ $400\text{kHz}$).
  * Khi thuật toán ổn định ($100$ mẫu hợp lệ): ESP32 kích hoạt chân `GPIO 25` cấp mức HIGH trong đúng **$100\text{ms}$** $\rightarrow$ Còi kêu **"TÍT"** 1 tiếng ngắn báo hiệu đo xong.
  * ESP32 Đầu giường $\longrightarrow$ Web Dashboard: **HTTP POST JSON** (hoặc WebSocket):
    ```json
    { "type": "VITAL_SIGNS", "spo2": 98, "heart_rate": 76, "status": "NORMAL" }
    ```
* **Thời gian xử lý:** Đọc và lọc tín hiệu: $3 - 5\text{s}$; Phản hồi tiếng bíp: tức thì ($< 1\text{ms}$).

---

### Kịch bản 2: Cụ A thức dậy, đi lại bình thường trong phòng
* **Hiện trường:** Cụ A đeo đai lưng, đi lại trong phòng ngủ.
* **Giao thức:**
  * MPU6050 $\longrightarrow$ ESP32 Đai lưng: **Giao thức I2C nội bo** (`GPIO 21/22`, $50\text{Hz}$).
  * Phân tích gia tốc: Trọng lực dao động tuần hoàn, biên độ gia tốc $SVM \in [0.8g, 1.4g]$ $\rightarrow$ Xác định trạng thái `WALKING`.
  * Đai lưng $\longrightarrow$ ESP32 Đầu giường: **HTTP POST** gửi định kỳ $5\text{s}$/lần qua Wi-Fi:
    ```json
    { "device": "BELT_01", "state": "WALKING", "battery": 85 }
    ```
  * Web Dashboard hiển thị: *Cụ A: Đang đi lại trong phòng*.

---

### Kịch bản 3: Cụ A bị té ngã trong phòng ngủ (SỰ CỐ NGUY CẤP)
* **Hiện trường:** Cụ A trượt chân ngã đập người xuống sàn phòng ngủ.
* **Chuỗi phản ứng giao thức:**
  1. **Nhận diện tại Đai:** Thuật toán phát hiện 3 pha:
     * *Pha 1:* Rơi tự do ngắn ($SVM < 0.5g$).
     * *Pha 2:* Va chạm mạnh ($SVM > 2.8g$).
     * *Pha 3:* Góc nghiêng cơ thể lệch $> 60^\circ$ và nằm bất động $> 2\text{s}$.
  2. **Báo động tại chỗ:** ESP32 đai lưng lập tức bật còi trên đai (GPIO 4) kêu dồn dập.
  3. **Gửi tin khẩn cấp qua Wi-Fi:** Đai lưng gửi ngay gói tin HTTP POST tới ESP32 Đầu giường (`192.168.1.50:80/api/alert`):
     ```json
     { "device": "BELT_01", "event": "FALL", "location_hint": "ROOM" }
     ```
  4. **Phản ứng của ESP32 Đầu giường:**
     * Kích hoạt còi tại phòng (GPIO 25) hú báo động liên tục.
     * Bắn lệnh **HTTP GET** sang ESP32-CAM: `GET http://192.168.1.60/capture`.
     * Camera trả về chuỗi nhị phân ảnh JPEG ($640 \times 480$, độ trễ $\approx 60\text{ms}$).
  5. **Báo về Dashboard:** ESP32 Đầu giường đẩy sự kiện ngã kèm link ảnh/base64 ảnh về Web Server trung tâm.
  6. **Giao diện Y tá:** Web bật còi hú máy tính, viền màn hình chớp đỏ, hiện ảnh chụp hiện trường tại phòng Cụ A.

---

### Kịch bản 4: Cúi người nhặt đồ hoặc rơi đai lưng (Cơ Chế Khử Báo Động Giả)
* **Hiện trường:** Cụ A ngồi phịch mạnh xuống giường hoặc làm rớt đai lưng.
* **Giao thức & Cơ chế xử lý:**
  * Khi xuất hiện va chạm vượt ngưỡng: Đai lưng **không gửi báo ngã ngay**, mà kích hoạt **Cửa sổ chờ hủy 5 giây (Cancel Grace Window)**:
    * Còi đai phát tiếng bíp ngắt quãng chậm nhắc nhở.
    * Nếu trong 5 giây, MPU6050 ghi nhận có chuyển động nâng đai lên hoặc đứng thẳng lại $\rightarrow$ Hủy sự kiện ngã, không phát chuông báo động toàn hệ thống.
    * Nếu sau 5 giây vẫn bất động $\rightarrow$ Kích hoạt Kịch bản 3 (báo ngã thật).
  * Đối chứng thị giác: Nếu điều dưỡng nhận được cảnh báo, chỉ cần liếc qua ảnh chụp từ ESP32-CAM trên Dashboard là biết ngay đai nằm dưới đất hay cụ A ngã thật.

---

### Kịch bản 5: Cụ A đi dạo ngoài sân vườn mini
* **Hiện trường:** Cụ A đi ra sân vườn mini (khoảng cách $30 - 60\text{m}$, vẫn trong tầm phủ của bộ phát Wi-Fi).
* **Giao thức:**
  * Đai lưng duy trì kết nối Wi-Fi, gửi gói tin cập nhật định kỳ mỗi 5 giây qua HTTP POST tới Server.
  * ESP32 Đầu giường: Cảm biến SpO2 trống; Camera phòng quay phòng trống.
  * Dashboard hiển thị trạng thái: *Cụ A: Đang ở khu vực Sân Vườn*.

---

### Kịch bản 6: Cụ A bị té ngã ngoài sân vườn mini
* **Hiện trường:** Cụ A trượt ngã trên bãi cỏ hoặc lối đi lát gạch ngoài sân.
* **Chuỗi giao thức:**
  1. Đai lưng phát hiện va chạm ngã $\rightarrow$ Còi trên đai hú vang ngoài sân.
  2. Đai lưng gửi gói tin khẩn cấp qua sóng Wi-Fi về Server:
     ```json
     { "device": "BELT_01", "event": "FALL", "zone": "GARDEN" }
     ```
  3. Server kích hoạt còi tại máy tính và còi trạm đầu giường để báo y tá.
  4. **Xử lý thị giác:** Server nhận diện vị trí là `GARDEN` $\rightarrow$ Web Dashboard ghi rõ: **"CẢNH BÁO: CỤ A NGÃ TẠI KHU VỰC SÂN VƯỜN (Ngoài tầm quan sát Camera phòng)"**. Y tá chạy thẳng ra sân cứu hộ, không mất công vào phòng tìm.

---

### Kịch bản 7: Đai lưng cạn pin hoặc mất kết nối Wi-Fi
* **Hiện trường:** Pin đai lưng cạn kiệt, hoặc Cụ A đi vào góc khuất mất sóng Wi-Fi quá $30\text{s}$.
* **Giao thức giám sát sống còn (Keep-Alive / Heartbeat):**
  * Bình thường, đai lưng gửi gói tin "sống" mỗi $5\text{s}$.
  * Trên Server/Đầu giường chạy một bộ đếm `TimeoutTimer`.
  * Nếu sau **$30\text{s}$** không nhận được bất kỳ bản tin nào từ đai:
    * Server tự động chuyển trạng thái của Cụ A thành **`DISCONNECTED (Mất kết nối / Nghi vấn hết pin)`**.
    * Phát âm thanh thông báo nhẹ để y tá kiểm tra thiết bị đai đeo.

---

### Kịch bản 8: Đo SpO2 phát hiện chỉ số nguy kịch
* **Hiện trường:** Cụ A ngồi tại giường đo SpO2, kết quả $SpO_2 < 90\%$ hoặc Nhịp tim $> 120\text{ bpm}$.
* **Giao thức:**
  * ESP32 Đầu giường không chỉ kêu "TÍT" 100ms, mà phát còi bíp liên tục dồn dập tại phòng.
  * Bắn gói tin cảnh báo y tế ưu tiên cao:
    ```json
    { "type": "MEDICAL_ALARM", "spo2": 87, "heart_rate": 130, "priority": "CRITICAL" }
    ```
  * Dashboard nhấp nháy thẻ màu cam cảnh báo cần can thiệp bình thở oxy ngay.

---

### Kịch bản 9: Cụ A tháo đai để trên bàn khi đi ngủ đêm
* **Hiện trường:** Cụ A tháo đai cắm sạc hoặc để trên bàn ngủ.
* **Giao thức:**
  * Sau 10 phút không có bất kỳ rung chấn nào ($SVM \approx 1.0g$, độ lệch chuẩn $\sigma \approx 0$), đai lưng gửi tin báo:
    ```json
    { "device": "BELT_01", "state": "IDLE_CHARGING" }
    ```
  * Hệ thống tạm ngưng thuật toán phát hiện ngã để tiết kiệm pin và loại bỏ 100% báo động giả ban đêm.

---

## 7. Đánh Đổi Kỹ Thuật & Giải Pháp Khắc Phục (Wi-Fi Thay Cho LoRa)

| Vấn đề kỹ thuật | Rủi ro thực tế | Giải pháp công nghệ đã tích hợp trong thiết kế |
| :--- | :--- | :--- |
| **Tiêu thụ pin trên đai** | ESP32 bật Wi-Fi ăn dòng $80 - 150\text{mA}$, pin $1200\text{mAh}$ chỉ dùng được khoảng 10–14 tiếng. | • Áp dụng chu kỳ ngủ ngắn (Modem-sleep) khi đứng yên.<br>• Chỉ gửi bản tin mỗi $5\text{s}$ khi đi lại; chỉ phát dữ liệu dồn dập khi có ngã.<br>• Quy trình vận hành: Cụ A đeo ban ngày, sạc pin vào ban đêm lúc ngủ. |
| **Trễ truyền tin khi chập chờn sóng** | Nếu sóng Wi-Fi ngoài vườn yếu lúc bắt đầu ngã, gói tin có thể bị rớt. | • Đai lưng chạy cơ chế **Buffer + Retry**: nếu gửi HTTP POST thất bại, lưu vào hàng đợi và thử lại mỗi $500\text{ms}$ cho đến khi nhận được mã phản hồi `200 OK`. |
| **Băng thông Camera** | ESP32-CAM stream video liên tục có thể chiếm dụng kênh truyền 2.4GHz. | • Mặc định Camera chỉ ở trạng thái chờ.<br>• Chỉ kích hoạt lấy ảnh tĩnh snapshot (`/capture`) khi có ngã.<br>• Luồng video trực tiếp (`/stream`) chỉ bật khi điều dưỡng chủ động nhấn nút "Xem Camera" trên Web. |

---

## 8. Kế Hoạch Đấu Nối Chân Phần Cứng Thực Tế

### 1. Đai đeo bụng (ESP32 NodeMCU):
* `MPU6050 SDA` $\longrightarrow$ `ESP32 GPIO 21`
* `MPU6050 SCL` $\longrightarrow$ `ESP32 GPIO 22`
* `MPU6050 VCC / GND` $\longrightarrow$ `3.3V / GND`
* `Còi Active Buzzer 1 (+)` $\longrightarrow$ `ESP32 GPIO 4`
* `Còi Active Buzzer 1 (-)` $\longrightarrow$ `GND`
* `Nguồn cấp:` Pin Li-Po $\longrightarrow$ TP4056 $\longrightarrow$ MT3608 (kích 5V) $\longrightarrow$ Chân `VIN` và `GND` của ESP32.

### 2. Trạm Đầu Giường (ESP32 NodeMCU):
* `MAX30102 SDA` $\longrightarrow$ `ESP32 GPIO 21` (kéo dài bằng dây bẹ)
* `MAX30102 SCL` $\longrightarrow$ `ESP32 GPIO 22`
* `MAX30102 VIN / GND` $\longrightarrow$ `3.3V / GND`
* `Còi Active Buzzer 2 (+)` $\longrightarrow$ `ESP32 GPIO 25` (phát tiếng bíp $100\text{ms}$ đo xong & hú còi khi ngã)
* `Còi Active Buzzer 2 (-)` $\longrightarrow$ `GND`
* `Nguồn cấp:` Cáp sạc 5V cắm chân microUSB của ESP32.

### 3. Camera Góc Phòng (ESP32-CAM):
* Cắm trực tiếp trên đế nạp **ESP32-CAM-MB**, cấp nguồn 5V qua cổng microUSB độc lập.

---

## 9. Hiện Trạng Thực Tế & Lộ Trình Kiểm Thử (Hardware Implementation Status)

### 1. Phân định rõ giữa "Mã nguồn phần mềm" và "Phần cứng thực tế":
* **Phần mềm (Firmware & Code):** Toàn bộ mã nguồn 4 tầng (`master_fall_detection_esp32.ino`, `firmware_node_wired`, `firmware_camera`, `backend`, `frontend`) đã được lập trình sẵn và lưu trong thư mục dự án để làm mẫu chuẩn nạp vào vi điều khiển.
* **Hiện trạng phần cứng thực tế:**
  * **Đai đeo thắt lưng (Wireless Node):** Đã hoàn tất gia công, hàn nối linh kiện vật lý (ESP32 + MPU6050 + Pin Li-Po + sạc TP4056 + tăng áp MT3608 + Còi Buzzer chân D4). **Tình trạng: Mới hàn xong phần cứng, CHƯA KIỂM THỬ (Untested).**
  * **Trạm Đầu Giường (Wired Station & Edge Server):** Chưa lắp ráp phần cứng (chưa gắn cảm biến MAX30102 và còi vào ESP32 thứ hai).
  * **Camera Góc Phòng (Vision Node):** Chưa lắp đặt và chưa nạp code vào module ESP32-CAM.
  * **Máy Chủ Web Dashboard:** Chưa chạy liên thông thực tế với các bo mạch phần cứng.

### 2. Lộ trình 4 bước kiểm thử tuần tự tiếp theo:
1. **Bước 1 — Kiểm thử Đai lưng đã hàn (Ưu tiên số 1):**
   * Cắm cáp nạp [master_fall_detection_esp32.ino](file:///d:/iot%20final/master_fall_detection_esp32.ino) vào ESP32 đai đeo.
   * Mở Serial Monitor ($115200\text{ baud}$), kiểm tra đọc dữ liệu 6 trục MPU6050.
   * Kiểm tra còi chân D4 phát tiếng bíp và test thuật toán gia tốc khi mô phỏng rơi tự do / va đập ngã.
2. **Bước 2 — Chuẩn bị phần cứng Trạm Đầu Giường:**
   * Cắm dây bẹ I2C nối cảm biến MAX30102 (`SDA: GPIO 21`, `SCL: GPIO 22`) và còi chân `D25` vào bo mạch ESP32 thứ 2.
   * Nạp [firmware_node_wired.ino](file:///d:/iot%20final/firmware_node_wired/firmware_node_wired.ino), kiểm tra chức năng đo SpO2 và phản hồi tiếng bíp $100\text{ms}$.
3. **Bước 3 — Nạp chương trình Camera:**
   * Cắm ESP32-CAM lên đế nạp ESP32-CAM-MB, nạp [firmware_camera.ino](file:///d:/iot%20final/firmware_camera/firmware_camera.ino).
   * Kiểm tra truy cập địa chỉ IP của camera trên trình duyệt web để kiểm tra luồng xem trực tiếp (`/stream`) và chụp ảnh (`/capture`).
4. **Bước 4 — Khởi chạy Web Server & Ghép nối toàn diện:**
   * Chạy máy chủ [backend/server.js](file:///d:/iot%20final/backend/server.js) và mở [frontend/index.html](file:///d:/iot%20final/frontend/index.html).
   * Kích hoạt sự cố ngã trên đai lưng để kiểm tra toàn bộ chuỗi phản ứng: Còi đai hú $\rightarrow$ Đầu giường hú còi phòng $\rightarrow$ Kéo ảnh từ Camera $\rightarrow$ Báo động hiển thị trên Web Dashboard.

