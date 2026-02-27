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


def create_evaluation_file(questions: list, output_file: str = "eval_data.xlsx", ground_truths: dict = None, contexts_gt: dict = None):
    """
    Chạy chatbot với danh sách câu hỏi và lưu kết quả ra Excel.
    
    Args:
        questions: Danh sách câu hỏi cần test
        output_file: Tên file Excel output
        ground_truths: Dict {question: ground_truth} để tự động điền đáp án
        contexts_gt: Dict {question: contexts_ground_truth} để tự động điền context tham chiếu
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
            "prompt": "Bạn là một chuyên gia tư vấn kinh tế Việt Nam. Hãy trả lời câu hỏi CHỈ dựa trên thông tin trong ngữ cảnh được cung cấp. Nếu ngữ cảnh không chứa thông tin cần thiết, hãy nói rõ là không có thông tin."
        }
        
        # Chạy workflow
        try:
            output_state = chatbot.compiled_workflow.invoke(input_state)
            
            answer = output_state.get("generation", "")
            documents = output_state.get("documents", [])
            
            # Lấy contexts từ documents
            contexts = [doc.page_content for doc in documents]
            
            gt = ground_truths.get(question, "") if ground_truths else ""
            ctx_gt = contexts_gt.get(question, "") if contexts_gt else ""
            results.append({
                "question": question,
                "ground_truth": gt,
                "contexts_ground_truth": ctx_gt,
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
# Mỗi item gồm: question + ground_truth + contexts_ground_truth
# Dữ liệu trích CHÍNH XÁC từ Dataset_economy
TEST_QUESTIONS = [
    {
        "question": "10 sự kiện kinh tế xã hội nổi bật năm 2023 là gì?",
        "ground_truth": "Năm 2023 ghi nhận kinh tế toàn cầu tiếp tục đối mặt với một loạt khó khăn, thách thức ảnh hưởng tới nền kinh tế Việt Nam. Theo đó, Việt Nam đã triển khai nhiều giải pháp nhằm tháo gỡ khó khăn, thúc đẩy tăng trưởng, giữ vững ổn định kinh tế vĩ mô và các cân đối lớn của nền kinh tế.",
        "contexts_ground_truth": "10 sự kiện kinh tế xã hội 2023. Năm 2023 ghi nhận kinh tế toàn cầu tiếp tục đối mặt với một loạt khó khăn, thách thức. Những khó khăn, thách thức này đều ảnh hưởng tới nền kinh tế Việt Nam. Theo đó, Việt Nam đã triển khai nhiều giải pháp nhằm tháo gỡ khó khăn, thúc đẩy tăng trưởng, giữ vững ổn định kinh tế vĩ mô và các cân đối lớn của nền kinh tế."
    },
    {
        "question": "Dự án đường Vành đai 4 TP.HCM có tổng mức đầu tư bao nhiêu?",
        "ground_truth": "Dự án đường Vành đai 4 TP.HCM có tổng chiều dài khoảng 206,82 km, đi qua 5 tỉnh thành gồm Bà Rịa – Vũng Tàu (18,7 km), Đồng Nai (45,6 km), Bình Dương (47,45 km), TP.HCM (17,3 km) và Long An (78,3 km). Quy mô đường cao tốc loại A, vận tốc thiết kế 100 km/giờ, mặt cắt ngang 6-8 làn xe. Sơ bộ tổng mức đầu tư giai đoạn 1 khoảng 105.964 tỷ đồng.",
        "contexts_ground_truth": "Các địa phương đề xuất tổng chiều dài đường Vành đai 4 TP.HCM là khoảng 206,82 km. Chia ra như sau: Bà Rịa – Vũng Tàu dài 18,7 km; Đồng Nai dài 45,6 km; Bình Dương dài 47,45 km; TPHCM 17,3 km và Long An 78,3 km (chiếm tỷ lệ dài nhất của dự án). Quy mô chiều rộng mặt cắt ngang được đề xuất (giai đoạn 1) từ 22 - 27 m, tùy địa phương. Sơ bộ tổng mức đầu tư giai đoạn 1 khoảng 105.964 tỷ đồng. Dự án đường Vành đai 4 TP.HCM có quy mô và tiêu chuẩn kỹ thuật là đường cao tốc loại A, vận tốc thiết kế 100 km/giờ; mặt cắt ngang 6 - 8 làn xe."
    },
    {
        "question": "Chương trình nhà ở xã hội TP.HCM có bao nhiêu dự án?",
        "ground_truth": "Theo Sở Xây dựng TP.HCM, trên địa bàn thành phố có 09 dự án nhà ở xã hội đang triển khai với diện tích đất 17,5 ha, 517.689 m2 sàn xây dựng, quy mô 6.383 căn hộ. Trong đó có 05 dự án chuyển tiếp từ giai đoạn 2016-2020 và 04 dự án khởi công trong năm 2022. Giai đoạn 2016-2020, thành phố đã hoàn thành 19 dự án nhà ở xã hội với 14.954 căn hộ. Giai đoạn 2021-2025, chỉ tiêu phát triển nhà ở xã hội dự kiến khoảng 2,5 triệu m2, tương đương khoảng 35.000 căn. Hiện còn 82 dự án đang được theo dõi trong kế hoạch phát triển.",
        "contexts_ground_truth": "Theo Sở Xây dựng TP.HCM, hiện nay, trên địa bàn thành phố có 09 dự án nhà ở xã hội đang triển khai với diện tích đất 17,5 ha, 517.689 m2 sàn xây dựng, quy mô 6.383 căn hộ. Trong đó, có 05 dự án chuyển tiếp từ giai đoạn 2016 - 2020; 04 dự án động thổ, khởi công trong năm 2022. Giai đoạn 2016-2020, thành phố đã xây dựng, đưa vào sử dụng 19 dự án nhà ở xã hội, quy mô 14.954 căn hộ. Giai đoạn 2021-2025, chỉ tiêu phát triển nhà ở xã hội dự kiến khoảng 2,5 triệu m2, khoảng 35.000 căn nhà. Kết quả đến quý 2-2023, Thành phố đã hoàn thành đưa vào sử dụng 2 dự án, quy mô 623 căn hộ. Có 6 dự án nhà ở xã hội (với quy mô 3.956 căn hộ) và 1 dự án nhà lưu trú công nhân (1.040 căn) đang thi công. Hiện còn 82 dự án đang được theo dõi trong kế hoạch phát triển nhà ở xã hội."
    },
    {
        "question": "Tình hình thị trường bất động sản năm 2023 như thế nào?",
        "ground_truth": "Thị trường bất động sản năm 2023 gặp nhiều khó khăn, đặc biệt là thiếu nguồn cung và mất cân đối cơ cấu sản phẩm. Phân khúc nhà ở trung, cao cấp và bất động sản du lịch dư thừa, trong khi nhà ở xã hội, nhà ở cho công nhân và nhà thương mại giá phù hợp thiếu gay gắt. Nhà ở thương mại hoàn thành 52 dự án với gần 16.000 căn, chưa bằng một nửa năm ngoái. Đến hết quý 3/2023, toàn thị trường có hơn 324.700 giao dịch, chỉ bằng 41% năm ngoái. Thị trường bắt đầu có dấu hiệu tích cực trở lại từ quý 3/2023.",
        "contexts_ground_truth": "Thị trường bất động sản năm 2023 đã gặp nhiều khó khăn ngay từ đầu năm, đặc biệt là tình trạng thiếu nguồn cung, thiếu cân đối trong cơ cấu sản phẩm, phổ biến là bất động sản ở các phân khúc nhà ở trung, cao cấp, bất động sản du lịch có biểu hiện dư thừa. Trong khi đó, nguồn cung phân khúc nhà ở xã hội, nhà ở cho công nhân và nhà ở thương mại giá phù hợp cho đối tượng thu nhập thấp, thu nhập trung bình thiếu gay gắt, không đáp ứng được nhu cầu của người dân. Tổng kết năm 2023, Bộ Xây dựng cho biết nguồn cung bất động sản năm 2023 tiếp tục hạn chế ở tất cả phân khúc, trong đó, nhà ở thương mại hoàn thành 52 dự án với gần 16.000 căn, chưa bằng một nửa năm ngoái. Đến hết quý 3/2023, toàn thị trường có hơn 324.700 giao dịch, chỉ bằng 41% năm ngoái."
    },
    {
        "question": "GDP Việt Nam năm 2023 tăng trưởng bao nhiêu?",
        "ground_truth": "GDP Việt Nam năm 2023 ước tăng 5,05% so với năm trước. GDP quý 4/2023 tăng 6,72% so với cùng kỳ, là mức tăng trưởng quý 4 cao nhất kể từ năm 2019. Mặc dù không đạt mục tiêu 6,5% của Chính phủ và Quốc hội, Việt Nam vẫn thuộc nhóm nền kinh tế có mức tăng trưởng cao nhất khu vực và thế giới. Quy mô GDP năm 2023 ước đạt 10.221,8 nghìn tỷ đồng, tương đương 430 tỷ USD. GDP bình quân đầu người đạt 4.284 USD, tăng 160 USD so với năm 2022.",
        "contexts_ground_truth": "Vượt qua cơn gió ngược toàn cầu, GDP năm 2023 ước tăng 5,05%. Với mức tăng 6,72% đạt được trong quý 4/2023, tăng trưởng GDP cả năm 2023 của Việt Nam theo ước tính của Tổng cục Thống kê đạt 5,05%. Mặc dù tăng trưởng GDP cả năm 2023 không đạt mục tiêu đề ra (6,5%) nhưng là kết quả tích cực và thuộc nhóm các nền kinh tế có mức tăng trưởng cao nhất khu vực và thế giới. GDP quý 4/2023 ước tính tăng 6,72% so với cùng kỳ năm trước, cao hơn quý 4 các năm 2012-2013 và 2020-2022, với xu hướng tích cực quý sau cao hơn quý trước (quý 1 tăng 3,41%, quý 2 tăng 4,25%, quý 3 tăng 5,47%). Quy mô GDP theo giá hiện hành năm 2023 ước đạt 10.221,8 nghìn tỷ đồng, tương đương 430 tỷ USD. GDP bình quân đầu người năm 2023 ước đạt 101,9 triệu đồng/người, tương đương 4.284 USD, tăng 160 USD so với năm 2022."
    },
]



if __name__ == "__main__":
    # Tách question, ground_truth và contexts_ground_truth
    questions = [q["question"] for q in TEST_QUESTIONS]
    ground_truths = {q["question"]: q["ground_truth"] for q in TEST_QUESTIONS}
    contexts_gt = {q["question"]: q["contexts_ground_truth"] for q in TEST_QUESTIONS}
    create_evaluation_file(questions, "eval_data.xlsx", ground_truths=ground_truths, contexts_gt=contexts_gt)

