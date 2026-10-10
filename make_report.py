from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

fonts = list(Path("/usr/share/fonts").rglob("ipaexg.ttf"))
if not fonts:
    raise SystemExit("日本語フォントが見つかりません")
pdfmetrics.registerFont(TTFont("JP", str(fonts[0])))

output = Path.cwd() / "出水利樹_最終課題_demimomi.pdf"
c = canvas.Canvas(str(output), pagesize=A4)
c.setTitle("日本語のお願いを理解して移動する猫型ロボット")
c.setAuthor("出水利樹")

W, H = A4
style = ParagraphStyle(
    "body", fontName="JP", fontSize=10,
    leading=17, textColor=colors.HexColor("#253242"),
    wordWrap="CJK")
y = H - 55

def paragraph(text):
    global y
    p = Paragraph(escape(text), style)
    _, height = p.wrap(W - 100, H)
    if y - height < 65:
        raise RuntimeError("ページの内容が多すぎます")
    p.drawOn(c, 50, y - height)
    y -= height + 9

def heading(text):
    global y
    c.setFillColor(colors.HexColor("#276A68"))
    c.setFont("JP", 12)
    c.drawString(50, y, text)
    y -= 24

def footer(page):
    c.setFillColor(colors.HexColor("#6B7280"))
    c.setFont("JP", 8)
    c.drawString(50, 35, "Physical AI応用1 最終課題 | 出水利樹 / demimomi")
    c.drawRightString(W - 50, 35, str(page))

c.setFillColor(colors.HexColor("#203A45"))
c.setFont("JP", 17)
c.drawString(50, y, "日本語のお願いを理解して移動する")
y -= 27
c.drawString(50, y, "猫型ロボット")
y -= 32
paragraph("氏名：出水利樹　アカウント：demimomi　作成日：2026年10月10日")

heading("1. 概要・目的")
paragraph(
    "自然な日本語のお願いから行き先を選び、猫型の車輪ロボットが"
    "指定された順序で移動するシステムを制作した。"
    "親しみやすい外観とAIによる指示の解釈を組み合わせ、"
    "言葉をロボットの物理的な動作につなげることを目的とした。")

heading("2. 使用環境・構成")
paragraph(
    "Windows上のWSL 2／Ubuntu 22.04、ROS 2 Humble、"
    "Gazebo Fortress、Python 3.10を使用した。"
    "ROSとGazebo間の通信にはros_gz_bridgeを利用した。")
paragraph(
    "処理の流れは、日本語入力 → 文の分割 → AIによる行き先判定 → "
    "移動計画の作成 → ROSの速度指令 → Gazeboでの移動、である。"
    "GazeboのオドメトリをROSへ受信し、現在位置と向きを制御に使用した。")

heading("3. AIの活用")
paragraph(
    "学習済みモデルsentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2をCPUで推論した。"
    "追加学習は行わず、入力文と各行き先の例文を文章ベクトルに変換し、"
    "コサイン類似度が最も高い行き先を選択した。")
paragraph(
    "文の区切りと順序はルール処理、各文の意味に基づく行き先の選択はAI、"
    "移動制御はルール処理が担当する。"
    "類似度は確率や正解率ではない。"
    "類似度0.35未満、または1位と2位の差0.04未満では走行しない処理を実装した。")

heading("4. ロボットと移動制御")
paragraph(
    "元の差動二輪ロボットの駆動機構を活用し、球・円柱・三角形メッシュで"
    "胴体、頭、耳、顔、しっぽを制作した。猫型の外観だが、四足歩行ではなく"
    "車輪で移動する。目的地はごはん(0.6, 0.0)、窓辺(0.6, 0.6)、"
    "寝床(0.0, 0.0)の3地点で、単位はメートル。")
paragraph(
    "向きのずれが大きい間は旋回し、向きが合うと前進する。"
    "最大前進速度は0.12m/s、到着判定は目的地から6cm以内とした。"
    "位置情報が3秒以上途切れた場合や、1地点への移動が180秒を超えた場合は停止する。")

footer(1)
c.showPage()
y = H - 55

heading("5. 工夫した点")
paragraph(
    "猫の外観に加え、ごはんはオレンジ、窓辺はミント、寝床は青の目印を配置し、"
    "動画で行き先を見分けやすくした。"
    "到着後は次の移動まで2秒待機する。飾りには衝突判定を付けず、走行への干渉を避けた。")
paragraph(
    "AIの入力、候補ごとの類似度、選択結果、移動順を表示し、"
    "ai_plan.jsonにも保存した。"
    "実行環境で発生した3D画面の点滅は、CPU描画とOgre 2を組み合わせた"
    "起動設定で解消し、その設定を起動スクリプトに保存した。")

heading("6. 動作確認結果")
paragraph(
    "「何か食べたい、それから窓から外を見たい、最後にベッドで休みたい」"
    "という言い換え入力を、ごはん → 窓辺 → 寝床と判定できた。"
    "選択先との類似度は順に0.962、0.935、0.847だった。")
paragraph(
    "順序を変更した「窓から外を見たい、それから何か食べたい、"
    "最後にベッドで休みたい」も、窓辺 → ごはん → 寝床と判定した。"
    "提出用にコピーしたコードで、3地点への到着と最終停止を確認した。"
    "この走行ログでは、出発から完了まで約39秒だった。")
paragraph(
    "提出動画は1分6秒で、通常速度で録画した。"
    "上記は確認した入力例の結果であり、すべての日本語指示への"
    "対応や一般的な正解率を示すものではない。")

heading("7. 制約・今後の改善")
paragraph(
    "行き先は3地点に限定され、複雑な指示や否定文への対応は保証できない。"
    "障害物回避、画像認識、四足歩行、しっぽの関節アニメーションは未実装である。"
    "車体の衝突形状と質量特性は元モデルを利用しており、猫の外観に厳密には一致しない。")
paragraph(
    "今後は未対応指示の判定を改善し、障害物回避やカメラによる認識、"
    "到着時のアニメーションを追加することで、より自然な猫型ロボットを目指す。")

heading("8. 参考・利用元")
paragraph("元モデル・コード：OsawaKousei/2DRoboPrac_ws（LICENSEを同梱）")
paragraph("https://github.com/OsawaKousei/2DRoboPrac_ws")
paragraph("参考記事：https://qiita.com/N622/items/9d89f77d85d9da0af29e")
paragraph(
    "AIモデル：https://huggingface.co/sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2")

footer(2)
c.save()
print("PDFを作成しました：", output)
