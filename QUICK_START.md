# 🚀 QUICK START GUIDE

Hướng dẫn nhanh để chạy chatbot trong 5 phút.

## 📋 Prerequisites
- Python 3.8+
- pip
- Internet (để download models)

## ⚡ 5 Bước Để Chạy

### 1️⃣ Cài Dependencies (2 phút)

```bash
cd /home/chinghia/CHATBOX_KINHTE
pip install -r requirements.txt
```

### 2️⃣ Chọn LLM Provider

Đặt API key trong `.env` hoặc terminal:

**Option A: Google Gemini** (free, recommended)
```bash
export KEY_API_GOOGLE="YOUR_GEMINI_API_KEY"
```

**Option B: OpenAI**
```bash
export KEY_API_OPENAI="sk-xxx..."
export OPENAI_LLM_MODEL_NAME="gpt-4-turbo"
```

**Option C: Local Ollama** (free, no API key needed)
```bash
# Install Ollama: https://ollama.ai
ollama run mistral
# Set in .env
export URL_OLLAMA="http://localhost:11434"
export MODEL_CHAT_OLLAMA="mistral"
export API_KEY_OLLAMA="dummy"
```

### 3️⃣ Build Vector Database (1-2 phút)

```bash
python ingestion/vector_data_builder.py
```

Kết quả:
```
🚀 BẮT ĐẦU QUÁ TRÌNH XÂY DỰNG VECTOR DATABASE...
--- BƯỚC 1: LOAD DỮ LIỆU ---
✅ Đã load 1523 văn bản từ './Dataset_economy'

--- BƯỚC 2: KHỞI TẠO MODEL ---
⚡ Đang tải mô hình Embedding: keepitreal/vietnamese-sbert...
✅ Đã tải mô hình thành công!

--- BƯỚC 3: CHUNKING & BUIDLING DB ---
✂️ Đang cắt 1523 văn bản gốc...
✅ Đã cắt thành 5234 chunks nhỏ.
🆕 Chưa có DB. Đang tạo DB mới tại './chroma_cosine'...
✅ Đã tạo và lưu DB mới thành công!

🎉 HOÀN THÀNH QUÁ TRÌNH XÂY DỰNG DATABASE!
```

### 4️⃣ Chạy Chatbot (1 phút)

```bash
python chatbot/main.py
```

### 5️⃣ Đặt Câu Hỏi 🎉

```
🤖 CHATBOT KINH TẾ - INTERACTIVE MODE
============================================================
📌 Gõ 'exit' hoặc 'quit' để thoát
============================================================

❓ Nhập câu hỏi: Nêu các chính sách hỗ trợ doanh nghiệp nhỏ và vừa?

============================================================
📝 Câu hỏi: Nêu các chính sách hỗ trợ doanh nghiệp nhỏ và vừa?
============================================================

🔎 [Energy Retriever] Đang xử lý câu hỏi: 'Nêu các chính sách hỗ trợ doanh nghiệp nhỏ và vừa?'
   -> Max Cosine Similarity: 0.7234
   -> 🏆 Đã chọn Cụm 2 với Energy Distance = 0.1542
   -> ✅ Truy xuất 8 documents
✅ Tài liệu liên quan: ...
✅ Tài liệu liên quan: ...
...
✅ Có tài liệu liên quan, tiến hành sinh câu trả lời

💭 Câu trả lời:
------------------------------------------------------------
Các chính sách hỗ trợ doanh nghiệp nhỏ và vừa (SMEs) của Chính phủ Việt Nam bao gồm:

1. **Hỗ trợ tài chính**:
   - Quỹ tín dụng ưu đãi cho SMEs
   - Lãi suất ưu đãi từ các ngân hàng thương mại
   - Hỗ trợ bảo lãnh vay vốn

2. **Hỗ trợ công nghệ số**:
   - Chương trình chuyển đổi số
   - Hỗ trợ về điều hành hiện đại

...chi tiết đầy đủ...
------------------------------------------------------------

❓ Nhập câu hỏi: 
```

## 🎯 Advanced Usage

### Direct Question
```bash
python chatbot/main.py --question "Kinh tế Việt Nam năm 2024 như thế nào?" --llm gemini
```

### Programmatic
```python
from chatbot.main import ChatbotRunner

chatbot = ChatbotRunner("./chroma_cosine", llm_provider="gemini")
answer = chatbot.answer_question("Nêu các thách thức của kinh tế Việt Nam")
print(answer)
```

## 🆘 Troubleshooting

### Lỗi: "ModuleNotFoundError: No module named 'langchain'"
```bash
pip install -r requirements.txt
```

### Lỗi: "Vector store không tìm thấy"
```bash
# Châc chắn đã chạy ingestion
python ingestion/vector_data_builder.py
```

### Lỗi: "API key không hợp lệ"
- Kiểm tra file `.env` hoặc environment variables
- Copy-paste API key lại (có kể cả dấu cách)

### Chậm/Timeout
- Giảm `k_retrieve` trong `files_rag_chat_agent.py` (từ 30 xuống 20)
- Hay sử dụng local Ollama thay vì API online

## 📁 File Quan Trọng

```
/home/chinghia/CHATBOX_KINHTE/
├── .env                        ← API keys ở đây
├── requirements.txt            ← Cài dependencies
├── README_CHATBOT.md           ← Hướng dẫn chi tiết
├── CHANGES_SUMMARY.md          ← Danh sách thay đổi
├── chatbot/
│   └── main.py                 ← 🔴 Chạy từ đây
└── ingestion/
    └── vector_data_builder.py  ← Chuẩn bị data từ đây
```

## ⏱️ Timeline Nhận Thức

```
Lần đầu tiên (Total: 5-10 phút):
  - Cài dependencies: 2-3 phút
  - Build vector DB: 1-2 phút
  - Chạy chatbot: 1 phút
  - Test câu hỏi: 1-2 phút
  
Lần sau (Total: < 1 phút):
  - python chatbot/main.py
  - Đặt câu hỏi ngay lập tức
```

## 🎓 Khái Niệm Chính

Để hiểu rõ hơn cách hoạt động:

1. **Ingestion** (setup một lần):
   - Đọc 1523 files `.txt` từ `Dataset_economy/`
   - Cắt thành 5000+ chunks
   - Embed bằng model tiếng Việt
   - Lưu trong ChromaDB

2. **Retrieval** (mỗi câu hỏi):
   - Tìm 30 documents gần nhất (Cosine similarity)
   - Gom cụm bằng K-Means
   - Chọn best cluster bằng Energy Distance
   - Trả về ~5-10 documents tốt nhất

3. **Grading** (validate):
   - LLM kiểm tra mỗi document có liên quan không
   - Loại bỏ documents không cần thiết

4. **Generation** (sinh câu trả lời):
   - Ghép documents thành context
   - LLM sinh câu trả lời dựa trên context

## 🔐 Security Notes

⚠️ **Important:**
- Không commit `.env` file lên Git
- Giữ API keys an toàn
- Sử dụng local Ollama nếu không muốn share data lên cloud

## 📞 Getting Help

Nếu gặp vấn đề không giải quyết được:

1. Kiểm tra [README_CHATBOT.md](README_CHATBOT.md)
2. Xem [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md) để hiểu thay đổi
3. Check terminal output để tìm thông báo lỗi
4. Chạy lại `python ingestion/vector_data_builder.py` để rebuild DB

---

**Happy Chatting! 🚀**
