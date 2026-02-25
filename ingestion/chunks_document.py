import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from model_embedding import vn_embedder

embeddings=vn_embedder.get_model()
class ChromaDBManager:
    """
    Class quản lý Vector Database (Chroma) và xử lý cắt văn bản.
    """
    def __init__(self, embeddings_model=embeddings, persist_dir='./chroma_economy_db'):
        # Nhận embedding model từ class VietnameseEmbedding bạn đã làm ở bước trước
        self.embeddings = embeddings_model
        self.persist_dir = persist_dir
        self.vector_store = None

    def process_and_store(self, raw_documents, chunk_size=800, chunk_overlap=300):
        """Hàm thực hiện cắt văn bản và lưu vào Database"""
        print(f"✂️ Đang cắt {len(raw_documents)} văn bản gốc...")
        
        # 1. Cấu hình Splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=['\n\n', '\n', '.', ',', ' ']
        )
        
        # Cắt thành các chunk nhỏ
        doc_splits = text_splitter.split_documents(raw_documents)
        print(f"✅ Đã cắt thành {len(doc_splits)} chunks nhỏ.")

        # 2. Xử lý VectorDB (Chroma)
        if os.path.exists(self.persist_dir):
            print(f"📂 Đã tìm thấy DB cũ tại '{self.persist_dir}'. Đang load và thêm dữ liệu mới...")
            # Load DB cũ
            self.vector_store = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embeddings
            )
            # Thêm chunks mới vào DB cũ
            self.vector_store.add_documents(doc_splits)
            print("✅ Đã cập nhật thành công dữ liệu mới vào DB cũ!")
            
        else:
            print(f"🆕 Chưa có DB. Đang tạo DB mới tại '{self.persist_dir}'...")
            # Tạo mới hoàn toàn
            self.vector_store = Chroma.from_documents(
                documents=doc_splits,
                embedding=self.embeddings,
                persist_directory=self.persist_dir
            )
            print("✅ Đã tạo và lưu DB mới thành công!")

    def get_retriever(self, k=30):
        """Hàm lấy retriever ra để tìm kiếm"""
        if not self.vector_store:
            if os.path.exists(self.persist_dir):
                self.vector_store = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=self.embeddings
                )
            else:
                raise ValueError("❌ Database chưa được tạo. Hãy chạy process_and_store() trước!")
                
        # Trả về retriever
        return self.vector_store.as_retriever(search_kwargs={'k': k})
