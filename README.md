# Vietlott Picker

Web app một file (`index.html`) để phân tích kết quả Vietlott Mega 6/45 và Power 6/55, gợi ý bộ số
(thống kê, thần số học, ít người chọn), tính giá trị kỳ vọng của vé và kiểm chứng các chiến lược trên dữ liệu thật.

## Nguồn dữ liệu

| Dữ liệu | Nguồn | Cập nhật |
| --- | --- | --- |
| Lịch sử kết quả các kỳ | [vietvudanh/vietlott-data](https://github.com/vietvudanh/vietlott-data) | hằng ngày |
| Jackpot hiện tại, bảng giải kỳ gần nhất | vietlott.vn → `data/vietlott.json` | GitHub Actions, 3 lần/ngày |

vietlott.vn không cho trình duyệt đọc trực tiếp (không có CORS), nên `scripts/fetch_vietlott.py` chạy trên
GitHub Actions (`.github/workflows/update-data.yml`), lấy dữ liệu và commit vào `data/vietlott.json`.
Script chỉ dùng thư viện chuẩn Python và chỉ ghi file khi dữ liệu thật sự thay đổi.

## Cài đặt

1. Tạo một repo **public** trên GitHub và push thư mục này lên nhánh `main`.
2. Vào tab **Actions** của repo, bật workflow nếu GitHub hỏi, rồi chạy thử **Update Vietlott data → Run workflow**.
3. Trong `index.html`, đặt `LIVE_URL` thành
   `https://raw.githubusercontent.com/<user>/<repo>/main/data/vietlott.json`
   để app đọc được dữ liệu khi mở file trực tiếp. Nếu app được phục vụ qua http(s) cùng thư mục
   với `data/vietlott.json` (ví dụ GitHub Pages), app tự tìm thấy file mà không cần cấu hình.

Chạy script thủ công:

```bash
python scripts/fetch_vietlott.py data/vietlott.json
```

Nếu vietlott.vn đổi giao diện, script sẽ giữ giá trị cũ cho phần không đọc được (và báo lỗi nếu không đọc được gì),
còn app tự quay về chế độ nhập tay.

## Lưu ý

Mỗi kỳ quay là độc lập; mọi bộ số có cùng xác suất trúng. App mô tả quá khứ và giúp tránh các bộ số phổ biến
(giảm khả năng chia giải), không làm tăng xác suất trúng.
