# Lotto Picker

Web app một file (`index.html`) để phân tích kết quả Vietlott Mega 6/45 và Power 6/55, gợi ý bộ số
(thống kê, thần số học, ít người chọn), tính giá trị kỳ vọng của vé và kiểm chứng các chiến lược trên dữ liệu thật.

## Nguồn dữ liệu

| Dữ liệu | Nguồn | Cập nhật |
| --- | --- | --- |
| Lịch sử kết quả các kỳ | [vietvudanh/vietlott-data](https://github.com/vietvudanh/vietlott-data) | hằng ngày |
| Jackpot hiện tại, bảng giải kỳ gần nhất | vietlott.vn → `data/vietlott.json` | chạy tay trên máy bạn |

vietlott.vn không cho trình duyệt đọc trực tiếp (không có CORS) và chặn máy chủ đám mây như GitHub Actions
(Cloudflare trả 403), nên `scripts/fetch_vietlott.py` được chạy từ máy của bạn. Script chỉ dùng thư viện
chuẩn Python và chỉ ghi file khi dữ liệu thật sự thay đổi.

## Cập nhật dữ liệu Jackpot

Sau mỗi kỳ quay (18:00, kết quả có khoảng 18:30), chạy:

```bash
python scripts/fetch_vietlott.py --push
```

Script lấy Jackpot ước tính và bảng giải kỳ gần nhất, ghi vào `data/vietlott.json`, và nếu có thay đổi
thì commit + push file đó. Bỏ `--push` nếu chỉ muốn cập nhật file trên máy.

App đọc file này từ `LIVE_URL` trong `index.html`
(`https://raw.githubusercontent.com/huynhkimtri/vietlott-picker/main/data/vietlott.json`), hoặc từ
`data/vietlott.json` cùng thư mục khi app được phục vụ qua http(s).

Nếu vietlott.vn đổi giao diện, script sẽ giữ giá trị cũ cho phần không đọc được (và báo lỗi nếu không đọc được gì),
còn app tự quay về chế độ nhập tay.

## Điều khoản sử dụng

- Chỉ dùng cá nhân, giải trí, phi thương mại; app không dự đoán kết quả và không phải lời khuyên tài chính.
- Không dùng để bán "số đẹp"/soi cầu thu phí, không gắn vào cờ bạc trái phép, không tự động gửi yêu cầu
  làm quá tải nguồn dữ liệu.
- Chỉ dành cho người từ 18 tuổi trở lên. Chơi có trách nhiệm: chỉ chơi bằng số tiền bạn sẵn sàng mất.
- Dự án không thuộc và không được Công ty TNHH MTV Xổ số Điện toán Việt Nam (Vietlott) bảo trợ;
  "Vietlott", "Mega 6/45", "Power 6/55" là tên của Vietlott.
- Dữ liệu cá nhân (ngày sinh, họ tên) chỉ lưu trên trình duyệt của người dùng.

## Bản quyền

© 2026 Huỳnh Kim Trí. Bảo lưu mọi quyền. Bạn được xem mã nguồn và dùng app cho mục đích cá nhân,
nhưng không được sao chép, chỉnh sửa hay phát hành lại khi chưa được phép. Xem [LICENSE](LICENSE).

## Lưu ý

Mỗi kỳ quay là độc lập; mọi bộ số có cùng xác suất trúng. App mô tả quá khứ và giúp tránh các bộ số phổ biến
(giảm khả năng chia giải), không làm tăng xác suất trúng.
