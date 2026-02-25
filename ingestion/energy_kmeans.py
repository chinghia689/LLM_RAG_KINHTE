import sys
from pathlib import Path
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document

# Import energy_base_distance từ cùng thư mục
sys.path.insert(0, str(Path(__file__).parent))
from energy_base_distance import energy_base_distance


class EnergyRetriever:
    """
    Module Truy xuất thông tin nâng cao sử dụng Energy-Based Distance và K-Means.
    """
    def __init__(self, vector_store, embeddings_model, k_retrieve=30, k_clusters=7, similarity_threshold=0.40):
        """
        Khởi tạo Energy Retriever.
        
        Args:
            vector_store: Chroma vector store
            embeddings_model: Model embedding (HuggingFace embeddings)
            k_retrieve: Số top documents để retrieve (mặc định 30)
            k_clusters: Số clusters cho K-Means (mặc định 7)
            similarity_threshold: Ngưỡng cosine similarity (mặc định 0.40)
        """
        # retriever chuẩn dùng Cosine (Lấy diện rộng)
        self.retriever = vector_store.as_retriever(search_kwargs={'k': k_retrieve})
        self.embeddings = embeddings_model
        self.k_clusters = k_clusters
        self.similarity_threshold = similarity_threshold
        self.vector_store = vector_store

    def retrieve(self, query):
        """
        Truy xuất documents dựa trên query sử dụng Energy Distance.
        
        Args:
            query (str): Câu hỏi/query của người dùng
            
        Returns:
            List[Document]: Danh sách Document objects liên quan nhất
        """
        print(f"\n🔎 [Energy Retriever] Đang xử lý câu hỏi: '{query}'")
        
        # 1. Truy xuất diện rộng (Top 30 từ cosine similarity)
        docs = self.retriever.invoke(query)
        if not docs:
            print("   -> ⚠️ Không tìm thấy tài liệu thô nào.")
            return []

        context = [doc.page_content for doc in docs]

        # 2. Embedding lại query và context
        # (Cách này tốn kém vì phải embed lại, nhưng an toàn và dễ code)
        doc_vectors = np.array(self.embeddings.embed_documents(context))
        query_vector = np.array(self.embeddings.embed_query(query)).reshape(1, -1)

        # 3. Lọc nhiễu bằng Cosine Threshold
        sims = cosine_similarity(query_vector, doc_vectors)[0]
        max_sim = np.max(sims)
        print(f"   -> Max Cosine Similarity: {max_sim:.4f}")
        
        if max_sim < self.similarity_threshold:
            print(f"   -> 🛑 Dữ liệu nhiễu (Dưới ngưỡng {self.similarity_threshold}). Ngắt luồng!")
            return []

        # 4. Gom cụm K-Means
        actual_k = min(self.k_clusters, len(doc_vectors))
        kmeans = KMeans(n_clusters=actual_k, random_state=42, n_init='auto')
        labels = kmeans.fit_predict(doc_vectors)

        # 5. Đánh giá bằng Energy Distance
        best_energy = float('inf')
        best_cluster_idx = -1
        
        for i in range(actual_k):
            indices = np.where(labels == i)[0]
            if len(indices) == 0: 
                continue  # Bỏ qua cụm rỗng (hiếm gặp)
                
            cluster_vectors = doc_vectors[indices]
            energy = energy_base_distance(query_vector, cluster_vectors)
            
            if energy < best_energy:
                best_energy = energy
                best_cluster_idx = i

        # 6. Lấy documents từ best cluster
        print(f"   -> 🏆 Đã chọn Cụm {best_cluster_idx} với Energy Distance = {best_energy:.4f}")
        win_indices = np.where(labels == best_cluster_idx)[0]
        
        # Trả về Document objects từ dữ liệu gốc
        final_docs = [docs[i] for i in win_indices]

        print(f"   -> ✅ Truy xuất {len(final_docs)} documents")
        return final_docs

