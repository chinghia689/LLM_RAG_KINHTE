import os
import pandas as pd


def aggregate_metrics_excel(file_path, out: str = None):
    """
    Gom tất cả chỉ số đã tính (context_precision, recall, BLEU, ROUGE, MRR, HitRate, NDCG...)
    vào một file Excel tổng hợp (có cả sheet chi tiết và sheet tóm tắt).

    Args:
        file_path (str): Đường dẫn file Excel đầu vào (đã có các cột chỉ số).
        out (str, optional): Đường dẫn file output.
                             - Nếu không truyền → tự động thêm tiền tố 'metrics_' vào tên file gốc.

    Returns:
        str: Đường dẫn file Excel đã tạo (gồm 2 sheet: detailed + summary).
    """
    # Đọc file Excel đã có kết quả chỉ số từng câu hỏi
    df = pd.read_excel(file_path)

    # ========================
    # 1. Xác định các cột metrics cần gom
    # ========================
    metric_cols = [
        "context_precision",
        "context_recall",
        "faithfulness",
        "answer_relevancy",
        "answer_correctness",
        "Human Evaluation",
        "ROUGE-2 Recall",
        "ROUGE-2 Precision",
        "ROUGE-2 F1",
        "BLEU-2",
        "Cosine Similarity",
        "Mean Reciprocal Rank",
        "Hit@5",
        "NDCG@5",
    ]

    # ========================
    # 2. Tính trung bình toàn cục các chỉ số
    # ========================
    summary = {}
    for col in metric_cols:
        if col in df.columns:  # chỉ tính nếu cột tồn tại
            summary[col] = df[col].mean()

    # Chuyển dict summary → DataFrame (1 dòng duy nhất)
    df_summary = pd.DataFrame([summary])

    # ========================
    # 3. Tạo đường dẫn file output
    # ========================
    if out:
        out_path = out
    else:
        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        out_path = os.path.join(dir_name, f"metrics_{base_name}")

    # ========================
    # 4. Lưu ra Excel (2 sheet: detailed & summary)
    # ========================
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="detailed")  # sheet chi tiết
        df_summary.to_excel(writer, index=False, sheet_name="summary")  # sheet tổng hợp

    # ========================
    # 5. Log kết quả
    # ========================
    print("✅ Đã tạo file tổng hợp:", out_path)
    print(df_summary)

    return out_path
