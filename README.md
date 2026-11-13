# Personal Expense Agent

Single agent quản lý thu chi cá nhân, xây dựng bằng LangGraph, Ollama và SQLite.

## Luồng LangGraph

```text
START -> agent -> tools -> agent -> END
                 ^         |
                 |---------|
```

Agent tự quyết định có gọi tool hay trả lời trực tiếp. Các tool gồm thêm khoản
thu, thêm khoản chi, xem, thống kê và xóa giao dịch.

## Cài đặt

Yêu cầu: Python 3.11+ và Ollama.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama pull qwen2.5:0.5b
```

## Chạy

```bash
python -m app.main
```

Ví dụ:

```text
Hôm nay ăn trưa hết 45000 đồng
Cho tôi xem 5 giao dịch gần nhất
Tháng này tôi đã tiêu bao nhiêu?
Xóa giao dịch ID 2
```

Giao dịch được lưu tại `data/expenses.db`. Memory hội thoại được giữ trong
thời gian chương trình đang chạy và phân biệt bằng `thread_id`.

Model mặc định nhẹ để chạy ngay trên máy CPU 12 GB RAM. Khi có thêm dung lượng
ổ đĩa, có thể đổi `MODEL_NAME=qwen3:4b` trong `.env` để gọi tool ổn định hơn.
