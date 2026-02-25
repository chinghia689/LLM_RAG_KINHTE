"""
Script tạo file evaluation từ chatbot.

Bước 1: Chạy script này để chatbot trả lời các câu hỏi
Bước 2: Mở file Excel, điền cột "ground_truth" thủ công
Bước 3: Chạy scoring/main.py để chấm điểm
"""

import os
import sys
from pathlib import Path

# Thêm parent folder vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from chatbot.main import ChatbotRunner


def create_evaluation_file(questions: list, output_file: str = "eval_data.xlsx"):
    """
    Chạy chatbot với danh sách câu hỏi và lưu kết quả ra Excel.
    
    Args:
        questions: Danh sách câu hỏi cần test
        output_file: Tên file Excel output
    """
    
    # Khởi tạo chatbot
    print("🚀 Đang khởi tạo chatbot...")
    chatbot = ChatbotRunner(
        path_vector_store="./chroma_economy_db",
        llm_provider="groq"
    )
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n{'='*60}")
        print(f"📝 [{i}/{len(questions)}] Câu hỏi: {question}")
        print(f"{'='*60}")
        
        # Chuẩn bị input
        input_state = {
            "question": question,
            "generation": "",
            "documents": [],
            "prompt": "Bạn là một chuyên gia tư vấn kinh tế Việt Nam."
        }
        
        # Chạy workflow
        try:
            output_state = chatbot.compiled_workflow.invoke(input_state)
            
            answer = output_state.get("generation", "")
            documents = output_state.get("documents", [])
            
            # Lấy contexts từ documents
            contexts = [doc.page_content for doc in documents]
            
            results.append({
                "question": question,
                "ground_truth": "",  # <-- ĐIỀN THỦ CÔNG SAU
                "contexts_ground_truth": "",  # <-- TÙY CHỌN
                "answer": answer,
                "contexts_answer": str(contexts),
                "metadata": str([doc.metadata for doc in documents]) if documents else ""
            })
            
            print(f"✅ Đã xử lý thành công")
            
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            results.append({
                "question": question,
                "ground_truth": "",
                "contexts_ground_truth": "",
                "answer": f"ERROR: {e}",
                "contexts_answer": "[]",
                "metadata": ""
            })
    
    # Lưu ra Excel
    df = pd.DataFrame(results)
    output_path = os.path.join(os.path.dirname(__file__), output_file)
    df.to_excel(output_path, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Đã lưu {len(results)} kết quả vào: {output_path}")
    print(f"📝 BƯỚC TIẾP THEO: Mở file Excel và điền cột 'ground_truth' thủ công")
    print(f"   Sau đó chạy: python scoring/main.py")
    print(f"{'='*60}")
    
    return output_path


# ============ CÂU HỎI TEST ============
# Thêm/sửa câu hỏi tại đây
TEST_QUESTIONS = [
    "10 sự kiện kinh tế xã hội nổi bật năm 2023 là gì?",
    "Dự án đường Vành đai 4 TP.HCM có tổng mức đầu tư bao nhiêu?",
    "Chương trình nhà ở xã hội TP.HCM có bao nhiêu dự án?",
    "Tình hình thị trường bất động sản năm 2023 như thế nào?",
    "GDP Việt Nam năm 2023 tăng trưởng bao nhiêu?",
]


if __name__ == "__main__":
    create_evaluation_file(TEST_QUESTIONS, "eval_data.xlsx")
