from langchain_huggingface import HuggingFaceEmbeddings

class VietnameseEmbedding:
    """
    Class quản lý mô hình nhúng (Embedding) chuyên dụng cho tiếng Việt.
    """
    def __init__(self, model_name='keepitreal/vietnamese-sbert', device='cpu'):
        # Lưu lại tên model để dễ debug sau này
        self.model_name = model_name
        
        # Cấu hình phần cứng (Chạy CPU cho nhẹ máy, hoặc 'cuda' nếu có GPU rảnh)
        self.model_kwargs = {'device': device}

        self.encode_kwargs = {'normalize_embeddings': True}

        # Khởi tạo model với đầy đủ tham số bảo vệ
        try:
            print(f"⚡ Đang tải mô hình Embedding: {self.model_name}...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs=self.model_kwargs,
                encode_kwargs=self.encode_kwargs
            )
            print("✅ Đã tải mô hình thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi tải mô hình: {e}")

    def get_model(self):
        """Hàm dùng để lấy object embeddings ra ngoài sử dụng"""
        return self.embeddings
vn_embedder = VietnameseEmbedding(device='cpu')
