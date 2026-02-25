import pandas as pd
import os
import re


def extract_keyword_from_ground_truth(question, ground_truth):
    """
    Lấy phần text thay cho 'bao nhiêu' trong ground_truth
    """
    if "bao nhiêu" not in str(question).lower():
        return None

    # Chuẩn hoá khoảng trắng
    q = re.sub(r"\s+", " ", str(question)).strip()
    gt = re.sub(r"\s+", " ", str(ground_truth)).strip()

    # Tách quanh 'bao nhiêu'
    parts = re.split(r" bao nhiêu ", q, flags=re.IGNORECASE)
    if len(parts) != 2:
        return None

    left, right = parts

    pattern = re.escape(left.strip()) + r"\s*(.+?)\s*" + re.escape(right.strip())

    match = re.search(pattern, gt, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def check_answer(question, ground_truth, answer):
    """
    Check keyword có nằm trong answer hay không
    """
    keyword = extract_keyword_from_ground_truth(question, ground_truth)

    if not keyword:
        return 0, None

    # check thuần text
    if keyword in str(answer):
        return 1, keyword

    return 0, keyword


def he(file_path):
    df = pd.read_excel(file_path)

    results = df.apply(
        lambda row: check_answer(
            row["question"],
            row["ground_truth"],
            row["answer"],
        ),
        axis=1,
    )

    df["Human Evaluation"] = results.apply(lambda x: x[0])
    df["Keyword Ground Truth"] = results.apply(lambda x: x[1])

    out = os.path.join(
        os.path.dirname(file_path),
        "he_" + os.path.basename(file_path),
    )

    df.to_excel(out, index=False)
    return out
