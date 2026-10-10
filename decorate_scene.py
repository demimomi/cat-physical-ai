from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

folder = Path.cwd()
path = folder / "world_cat.sdf"
backup = folder / "world_cat_before_scene.sdf"
if not backup.exists():
    shutil.copy2(path, backup)

tree = ET.parse(path)
world = tree.getroot().find("world")

# 再実行しても飾りが重複しないようにする
for model in list(world.findall("model")):
    if model.get("name", "").startswith("cat_place_"):
        world.remove(model)

def place(name, x, y):
    model = ET.SubElement(world, "model", name="cat_place_" + name)
    ET.SubElement(model, "static").text = "true"
    ET.SubElement(model, "pose").text = f"{x} {y} 0 0 0 0"
    return ET.SubElement(model, "link", name="decoration")

def shape(link, name, pose, kind, values, color):
    v = ET.SubElement(link, "visual", name=name)
    ET.SubElement(v, "pose").text = pose
    geometry = ET.SubElement(v, "geometry")
    primitive = ET.SubElement(geometry, kind)
    for key, value in values.items():
        ET.SubElement(primitive, key).text = str(value)
    material = ET.SubElement(v, "material")
    for key in ("ambient", "diffuse"):
        ET.SubElement(material, key).text = color

def mat(link, color):
    shape(link, "mat", "0 0 0.002 0 0 0",
          "cylinder", {"radius": 0.18, "length": 0.002}, color)

food = place("Food_Orange", 0.6, 0.0)
mat(food, "0.96 0.65 0.30 1")
shape(food, "dish", "0.30 0 0.014 0 0 0",
      "cylinder", {"radius": 0.065, "length": 0.026},
      "0.94 0.92 0.85 1")
shape(food, "food_surface", "0.30 0 0.028 0 0 0",
      "cylinder", {"radius": 0.049, "length": 0.003},
      "0.38 0.22 0.12 1")
for i, (x, y) in enumerate([
    (0.28, -0.02), (0.32, -0.02),
    (0.28, 0.02), (0.32, 0.02), (0.30, 0),
]):
    shape(food, f"kibble_{i}", f"{x} {y} 0.034 0 0 0",
          "sphere", {"radius": 0.009}, "0.65 0.37 0.15 1")

window = place("Window_Mint", 0.6, 0.6)
mat(window, "0.40 0.78 0.66 1")
shape(window, "glass", "0 0.34 0.22 0 0 0",
      "box", {"size": "0.36 0.018 0.28"},
      "0.58 0.82 0.93 1")
frame = "0.55 0.36 0.21 1"
for name, x in [("frame_left", -0.19), ("frame_right", 0.19)]:
    shape(window, name, f"{x} 0.33 0.22 0 0 0",
          "box", {"size": "0.025 0.035 0.32"}, frame)
for name, z in [("frame_bottom", 0.065), ("frame_top", 0.375)]:
    shape(window, name, f"0 0.33 {z} 0 0 0",
          "box", {"size": "0.40 0.035 0.025"}, frame)
shape(window, "frame_middle", "0 0.325 0.22 0 0 0",
      "box", {"size": "0.015 0.035 0.30"}, frame)

bed = place("Bed_Blue", 0.0, 0.0)
mat(bed, "0.46 0.62 0.89 1")
shape(bed, "pillow", "-0.25 0 0.025 0 0 0",
      "box", {"size": "0.10 0.15 0.045"},
      "0.90 0.92 1.0 1")

# 床を暖かい色に変更
ground = world.find("./model[@name='ground_plane']")
if ground is not None:
    for material in ground.findall(".//visual/material"):
        for key in ("ambient", "diffuse"):
            element = material.find(key)
            if element is not None:
                element.text = "0.91 0.87 0.78 1"

# 耳の参照を、別のPCでも使える形式に変更
for uri in world.findall(".//visual/geometry/mesh/uri"):
    if uri.text and uri.text.endswith("/cat_ear.stl"):
        uri.text = "model://cat_ear.stl"

ET.indent(tree, space="  ")
tree.write(path, encoding="utf-8", xml_declaration=True)
ET.parse(path)

# 最終地点が寝床以外でも正しいメッセージにする
patrol = folder / "cat_patrol.py"
text = patrol.read_text(encoding="utf-8")
text = text.replace(
    'self.get_logger().info("巡回完了。寝床でおやすみ！")',
    'self.get_logger().info(f"移動完了。{name}で待っています！")')
patrol.write_text(text, encoding="utf-8")

print("3地点の目印を追加しました！")
