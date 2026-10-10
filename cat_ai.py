import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

folder = Path(__file__).resolve().parent

examples = {
    "ごはん": [
        "お腹がすいた",
        "ごはんを食べたい",
        "食事の場所に行って",
        "餌を食べに行こう",
    ],
    "窓辺": [
        "外を眺めたい",
        "窓辺に行って",
        "窓から景色を見たい",
        "日向ぼっこをしたい",
    ],
    "寝床": [
        "眠りたい",
        "寝床に行って",
        "ベッドで寝たい",
        "おうちに戻って休みたい",
    ],
}

print("AIモデルを読み込んでいます…", flush=True)
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    device="cpu"
)

labels, sentences = [], []
for label, texts in examples.items():
    labels.extend([label] * len(texts))
    sentences.extend(texts)
reference = model.encode(sentences, normalize_embeddings=True)

request = input(
    "\n猫へのお願いを入力してください。\n"
    "例：お腹がすいた、そのあと外を眺めたい、最後に眠りたい\n> "
).strip()

# 順番の区切りはルールで処理し、各文の行き先はAIで判定
clauses = [
    text.strip(" 、,。")
    for text in re.split(
        r"そのあと|その後|それから|次に|最後に|[、,。;\n→]",
        request)
    if text.strip(" 、,。")
]

if not clauses or len(clauses) > 6:
    sys.exit("お願いは1〜6個に区切って入力してください。")

steps = []
for clause in clauses:
    query = model.encode([clause], normalize_embeddings=True)[0]
    similarities = reference @ query
    scores = {
        label: float(max(
            similarities[i] for i, name in enumerate(labels)
            if name == label))
        for label in examples
    }
    ranking = sorted(scores, key=scores.get, reverse=True)
    best, second = ranking[:2]
    score = scores[best]
    margin = score - scores[second]

    print(f"\nお願い：{clause}", flush=True)
    for label in ranking:
        print(f"  {label}：類似度 {scores[label]:.3f}", flush=True)

    # 類似度は確率ではない。曖昧な判定では走行しない
    if score < 0.35 or margin < 0.04:
        sys.exit(
            "行き先をはっきり判定できませんでした。\n"
            "移動せず終了します。お願いを言い換えてください。")

    print(f"  AIの判定 → {best}", flush=True)
    steps.append({
        "clause": clause,
        "destination": best,
        "similarity": score,
        "margin": margin,
        "candidate_scores": scores,
    })

plan = {
    "request": request,
    "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "steps": steps,
}
path = folder / "ai_plan.json"
path.write_text(
    json.dumps(plan, ensure_ascii=False, indent=2),
    encoding="utf-8")

print("\n移動計画：" +
      " → ".join(step["destination"] for step in steps), flush=True)

if "--dry-run" in sys.argv:
    print("判定のみ完了。猫は動かしていません。")
else:
    print("猫が出発します！", flush=True)
    try:
        subprocess.run(
            ["/usr/bin/python3", "-u",
             str(folder / "cat_follow_plan.py"), str(path)],
            check=True)
    except KeyboardInterrupt:
        print("\n自動走行を中断しました。")
    except subprocess.CalledProcessError as error:
        sys.exit(f"走行プログラムが終了しました：{error.returncode}")
