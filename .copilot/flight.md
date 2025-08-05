Dưới đây là **backlog chi tiết cho module Odoo 18** dùng để **quản lý chuyến bay và các bin chứa đồ (Cargo Bins)** – phục vụ mục tiêu MVP cho hệ thống Logistic Portal.

---

## 📦 Module: `logistic_flight_bin`

### 🎯 Mục tiêu:

* Quản lý chuyến bay liên quan đến vận chuyển hàng hóa (air freight)
* Quản lý các thùng chứa (cargo bins) trong từng chuyến bay
* Cho phép tracking hàng hóa theo chuyến bay và bin

---

## 🧾 Epic 1: Quản lý chuyến bay

### 🧩 User Story 1.1 – Tạo và quản lý chuyến bay

**Mô tả:**
Là nhân viên vận hành, tôi muốn tạo và cập nhật thông tin chuyến bay để theo dõi lịch trình vận chuyển hàng hóa.

**Fields**:

* Flight Number
* Departure Airport (IATA code)
* Arrival Airport (IATA code)
* Departure Time
* Arrival Time
* Status: Scheduled / Departed / Landed / Cancelled
* Carrier (Hãng bay)

**Acceptance Criteria**:

* Người dùng có thể tạo chuyến bay với đầy đủ thông tin bắt buộc
* Không được nhập giờ đến trước giờ đi
* Flight number là duy nhất trong cùng ngày
* Có thể cập nhật trạng thái chuyến bay

**Definition of Done**:

* Có form view, list view hiển thị tất cả các chuyến bay
* Các ràng buộc được kiểm tra
* Có thể filter theo trạng thái, carrier, mã sân bay

---

## 🧾 Epic 2: Quản lý Bin (Cargo Containers)

### 🧩 User Story 2.1 – Tạo bin chứa hàng

**Mô tả:**
Là nhân viên kho, tôi muốn khai báo và gán các bin chứa đồ vào chuyến bay để quản lý vị trí hàng hóa.

**Fields**:

* Bin Code (mã bin)
* Type (ULD, Pallet, Container,...)
* Volume (m³)
* Max Weight (kg)
* Current Weight (kg)
* Assigned Flight (many2one → flight)

**Acceptance Criteria**:

* Có thể tạo bin và gán cho chuyến bay
* Không cho phép `Current Weight > Max Weight`
* Khi chuyến bay đã cất cánh, không thể thay đổi bin

**Definition of Done**:

* Có giao diện quản lý bin riêng (form, list view)
* Giao diện ở màn hình chuyến bay có tab danh sách các bin
* Có cảnh báo khi bin vượt quá tải

---

## 🧾 Epic 3: Tracking bin trong chuyến bay

### 🧩 User Story 3.1 – Tra cứu thông tin bin theo chuyến bay

**Mô tả:**
Là nhân viên CSKH, tôi muốn tra cứu bin nào đang thuộc chuyến bay nào, để hỗ trợ khách hàng khi tracking hàng hóa.

**Acceptance Criteria**:

* Có smart button "View Bins" trên chuyến bay
* Có link điều hướng từ bin về chuyến bay
* Có search bin theo mã chuyến bay, sân bay

**Definition of Done**:

* Hoạt động điều hướng đã test đủ case
* Tất cả dữ liệu đã có khả năng lọc theo chuyến bay hoặc bin

---

## 🧾 Epic 4: Tự động hóa & tích hợp

### 🧩 User Story 4.1 – Tự động chuyển trạng thái chuyến bay

**Mô tả:**
Là hệ thống, tôi muốn tự cập nhật trạng thái chuyến bay theo giờ cất/hạ cánh thực tế để giảm sai sót nhập tay.

**Acceptance Criteria**:

* Nếu giờ hiện tại > giờ cất cánh → chuyển trạng thái: `Departed`
* Nếu giờ hiện tại > giờ hạ cánh → chuyển trạng thái: `Landed`
* Job chạy mỗi 10 phút

**Definition of Done**:

* Cron job hoạt động ổn định, ghi log khi có cập nhật
* Có thể bật/tắt tính năng này trong cấu hình

---

## 📐 Kiến trúc Module

### Models:

* `logistic.flight`
* `logistic.bin`

### Quan hệ:

* 1 `flight` có nhiều `bin`
* 1 `bin` chỉ thuộc 1 `flight`

---

## 🧪 Test case mẫu

| Scenario                            | Kết quả mong đợi                    |
| ----------------------------------- | ----------------------------------- |
| Tạo flight mới với giờ đến < giờ đi | ❌ Báo lỗi                           |
| Tạo bin vượt max weight             | ❌ Báo lỗi                           |
| Gán bin vào chuyến bay đã cất cánh  | ❌ Không cho phép                    |
| Cron chạy sau giờ hạ cánh           | ✅ Chuyến bay có trạng thái `Landed` |

---

Bạn muốn tôi tạo luôn code khung module `logistic_flight_bin` cho Odoo 18 chứ? Nếu có, tôi sẽ tạo:

* `__manifest__.py`
* Models: `flight.py`, `bin.py`
* Views: form/list
* Security rules
* Menu & action

Bạn có muốn tôi xuất luôn project starter repo không?
