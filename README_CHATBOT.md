# 🤖 Chatbot RAG - Kinh Tế (README)

Một ứng dụng chatbot sử dụng **Retrieval-Augmented Generation (RAG)** với **Energy-Based Distance** để trả lời các câu hỏi về kinh tế Việt Nam.

## 📋 Kiến Trúc

```
┌─────────────────┐
│  User Question  │
└────────┬────────┘
         │
    ┌────▼────────────────────────────┐
    │   Ingestion Phase (First Time)   │
    │ 1. Load Dataset (load_document.py)
    │ 2. Embedding (model_embedding.py)
    │ 3. Chunking & Store in ChromaDB
    │    (chunks_document.py)
    │ 4. Build Vector Store
    │    (vector_data_builder.py)
    └────┬─────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────────┐
    │         Chatbot Phase  (Runtime)               │
    │                                                │
    │  ┌─ Retrieve (Energy Distance)               │
    │  │  - Load ChromaDB                          │
    │  │  - Get Top-30 by Cosine Similarity        │
    │  │  - K-Means Clustering                     │
    │  │  - Find Best Cluster by Energy Distance   │
    │  │                                            │
    │  └─▶ Grade Documents                         │
    │     - Check relevance with LLM               │
    │                                               │
    │  └─▶ Generate Answer (if docs exist)         │
    │     - Create context from documents          │
    │     - Call LLM to generate response          │
    │                                               │
    │  └─▶ Handle No Answer (if no docs)           │
    │     - Return default message                 │
    └────┬──────────────────────────────────────────┘
         │
    ┌────▼──────────────┐
    │  Answer to User    │
    └────────────────────┘
```

## 📁 Cấu Trúc Thư Mục

```
chatbot/
├── __init__.py
├── main.py                          # 🔴 Entry point - Chạy từ đây
├── services/
│   ├── __init__.py
│   ├── files_rag_chat_agent.py      # Main RAG workflow logic
│   └── base/
│       └── chat_agent.py            # (không dùng)
└── utils/
    ├── __init__.py
    ├── llm.py                       # LLM loader (OpenAI, Gemini, Ollama, etc)
    ├── graph_state.py               # State schema for LangGraph
    ├── document_grader.py           # Chấm điểm tài liệu
    ├── answer_generator.py          # Sinh câu trả lời
    └── custom_prompt.py             # System prompts

ingestion/
├── load_document.py                 # Load .txt files từ Dataset
├── model_embedding.py               # Vietnamese embedding model
├── chunks_document.py               # ChromaDB manager
├── vector_data_builder.py           # 🔴 Chạy ingestion từ đây
├── energy_base_distance.py          # Energy distance formula
└── energy_kmeans.py                 # Advanced retriever with Energy Distance
```

## ⚙️ Setup & Installation

### 1. Tạo Virtual Environment

```bash
# Sử dụng conda (nếu có)
conda create -n chatbot_env python=3.10
conda activate chatbot_env

# Hoặc sử dụng venv
python -m venv chatbot_env
source chatbot_env/bin/activate  # Mac/Linux
# hoặc
chatbot_env\Scripts\activate  # Windows
```

### 2. Cài Đặt Dependencies

Tạo file `requirements.txt` trong `/home/chinghia/CHATBOX_KINHTE/`:

```txt
langchain==0.1.0
langchain-core==0.1.0
langchain-community==0.0.30
langchain-openai==0.1.0
langchain-google-genai==0.0.12
langchain-xai==0.0.1
langchain-chroma==0.1.1
langchain-huggingface==0.0.1
langchain-text-splitters==0.0.1
langgraph==0.0.1
chromadb==0.4.25
sentence-transformers==2.2.2
numpy==1.24.3
scikit-learn==1.3.2
scipy==1.11.4
```

Cài đặt:
```bash
pip install -r requirements.txt
```

Hoặc cài thủ công các package quan trọng:
```bash
pip install langchain langchain-core langgraph langchain-chroma chromadb sentence-transformers scikit-learn numpy scipy
```

### 3. Thiết Lập Environment Variables

Tạo file `.env` trong thư mục gốc `/home/chinghia/CHATBOX_KINHTE/`:

```bash
# Chọn một trong các LLM providers sau:

# OpenAI
KEY_API_OPENAI=sk-xxx...
OPENAI_LLM_MODEL_NAME=gpt-4-turbo

# Google Gemini
KEY_API_GOOGLE=AIza...
GOOGLE_LLM_MODEL_NAME=gemini-pro

# Ollama (local server)
URL_OLLAMA=http://localhost:11434
MODEL_CHAT_OLLAMA=mistral
API_KEY_OLLAMA=dummy

# xAI Grok
KEY_API_GROK=xai-xxx...
GROK_LLM_MODEL_NAME=grok-beta
URL_GROK=https://api.x.ai/v1
```

Hoặc thiết lập trực tiếp trong code (xem phần sử dụng bên dưới).

## 🚀 Sử Dụng

### Bước 1: Build Vector Database (Chỉ chạy một lần)

```bash
cd /home/chinghia/CHATBOX_KINHTE/
python ingestion/vector_data_builder.py
```

📌 Output:
- Sẽ tạo thư mục `./chroma_cosine/` chứa vector database
- Nếu có lần chạy lại, sẽ append dữ liệu mới vào db cũ

### Bước 2: Chạy Chatbot

#### Option 1: Interactive Mode (Recommended)

```bash
cd /home/chinghia/CHATBOX_KINHTE/
python chatbot/main.py
```

Sau đó gõ câu hỏi:
```
❓ Nhập câu hỏi: Nêu các chính sách hỗ trợ doanh nghiệp nhỏ và vừa?
💭 Câu trả lời:
... [chatbot sẽ trả lời]
```

#### Option 2: Direct Question (Command Line)

```bash
python chatbot/main.py --question "Kinh tế Việt Nam hiện tại như thế nào?" --llm gemini
```

#### Option 3: Programmatic Usage

```python
from chatbot.main import ChatbotRunner

# Khởi tạo
chatbot = ChatbotRunner(
    path_vector_store="./chroma_cosine",
    llm_provider="gemini"
)

# Đặt câu hỏi
answer = chatbot.answer_question(
    question="Nêu các chính sách hỗ trợ doanh nghiệp nhỏ và vừa?",
    prompt="Bạn là chuyên gia tư vấn kinh tế Việt Nam"
)

print(answer)
```

## 🔧 Cấu Hình Tùy Chỉnh

### Thay Đổi LLM Provider

Trong `chatbot/main.py`, dòng:
```python
LLM_PROVIDER = "gemini"  # Thay thành: openai, local, grok
```

### Điều Chỉnh Retrieval Parameters

Trong `files_rag_chat_agent.py`, hàm `retrieve()`:
```python
energy_retriever = EnergyRetriever(
    vector_store=self.vector_store,
    embeddings_model=self.embeddings,
    k_retrieve=30,         # Số top docs để lấy từ Cosine (mặc định 30)
    k_clusters=7,          # Số clusters K-Means (mặc định 7)
    similarity_threshold=0.40  # Ngưỡng cosine similarity (mặc định 0.40)
)
```

### Điều Chỉnh Chunking trong Ingestion

Trong `ingestion/vector_data_builder.py`:
```python
db_manager.process_and_store(
    raw_documents=docs,
    chunk_size=800,        # Kích thước mỗi chunk
    chunk_overlap=300      # Overlap giữa chunks
)
```

## 📊 Workflow Chi Tiết

### Retrieval Phase (Truy Xuất)

1. **Load Vector Store**: Tải ChromaDB từ disk
2. **Initial Retrieval**: Cosine similarity search → Top 30 documents
3. **Embedding**: Re-embed query và documents
4. **Similarity Check**: Kiểm tra max cosine similarity vs threshold
5. **K-Means Clustering**: Gom chúng thành 7 clusters
6. **Energy Distance**: Tìm cluster "tốt nhất" dựa trên energy distance
7. **Final Selection**: Trả về documents từ best cluster

### Grading Phase (Đánh Giá)

- Gửi từng document + question lên LLM
- LLM trả lời "yes" hoặc "no" (liên quan hay không)
- Chỉ giữ lại "yes" documents

### Generation Phase (Sinh Câu Trả Lời)

- Ghép nội dung tất cả documents thành context
- Gửi lên LLM: question + context + custom prompt
- LLM sinh câu trả lời dựa trên context

## 🐛 Troubleshooting

### "Vector store không tìm thấy"

```
❌ Lỗi: Vector store không tìm thấy tại './chroma_cosine'
```

**Giải pháp**: Chạy ingestion trước:
```bash
python ingestion/vector_data_builder.py
```

### "Không có documents liên quan"

Điều chỉnh ngưỡng tương tự:
```python
similarity_threshold=0.30  # Giảm từ 0.40 xuống 0.30
```

### "LLM API key không hợp lệ"

Đảm bảo `.env` được set đúng, hoặc pass trực tiếp khi init:
```python
# Khởi tạo LLM thủ công
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(google_api_key="YOUR_KEY", model="gemini-pro")
```

## 📝 Ví Dụ Sử Dụng

### Ví Dụ 1: Câu hỏi đơn giản

```
❓ Nhập câu hỏi: Nêu ý nghĩa của chính sách tài khóa kỹ thuật số?

✅ Truy xuất: 30 documents
✅ Đánh giá: 12 documents liên quan
💭 Câu trả lời: 
Chính sách tài khóa kỹ thuật số (Digital Transformation Strategy) là... [chi tiết]
```

### Ví Dụ 2: Multi-turn conversation

```
❓ Nhập câu hỏi: Nêu các yếu tố ảnh hưởng đến tăng trưởng kinh tế?
💭 Câu trả lời: [answer 1]

❓ Nhập câu hỏi: Làm thế nào để tối ưu hóa các yếu tố đó?
💭 Câu trả lời: [answer 2]
```

## 📚 Tài Liệu Tham Khảo

- [LangChain Documentation](https://python.langchain.com)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Energy Distance Paper](https://en.wikipedia.org/wiki/Energy_distance)

## ✅ Checklist

- [ ] Environment variables đã được thiết lập
- [ ] Vector store đã được build (đã chạy ingestion)
- [ ] Dependencies đã cài đặt
- [ ] LLM API key hợp lệ
- [ ] Có thể chạy `python chatbot/main.py` thành công

## 📞 Support

Nếu gặp lỗi, vui lòng check:
1. Environment variables trong `.env`
2. Đường dẫn vector store có tồn tại
3. Internet connection (để gọi LLM API)
4. Python version >= 3.8

---

**Chúc bạn sử dụng chatbot vui vẻ! 🚀**
