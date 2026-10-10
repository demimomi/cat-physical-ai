from pathlib import Path
import xml.etree.ElementTree as ET

folder = Path.cwd()
tree = ET.parse(folder / "world.sdf")
world = tree.getroot().find("world")
robot = world.find("./model[@name='demoRobot']")
base = robot.find("./link[@name='base_link']")
assert base is not None, "base_linkが見つかりません"

# 元の車体の外観だけを置き換える
for visual in list(base.findall("visual")):
    base.remove(visual)

cream = "0.95 0.81 0.58 1"
white = "1.0 0.95 0.84 1"
dark = "0.10 0.08 0.07 1"
pink = "0.95 0.48 0.52 1"

def visual(name, pose, kind, values, color):
    v = ET.SubElement(base, "visual", name=name)
    ET.SubElement(v, "pose").text = pose
    shape = ET.SubElement(ET.SubElement(v, "geometry"), kind)
    for key, value in values.items():
        ET.SubElement(shape, key).text = str(value)
    material = ET.SubElement(v, "material")
    ET.SubElement(material, "ambient").text = color
    ET.SubElement(material, "diffuse").text = color
    return v

def ball(name, x, y, z, radius, color):
    return visual(name, f"{x} {y} {z} 0 0 0",
                  "sphere", {"radius": radius}, color)

# 丸い胴体と頭。進行方向は+x
ball("cat_body_back", 0.035, 0, 0.09, 0.065, cream)
ball("cat_body_front", 0.10, 0, 0.10, 0.065, cream)
ball("cat_head", 0.17, 0, 0.16, 0.068, cream)

# 顔
for side, y in [("left", 0.028), ("right", -0.028)]:
    ball("eye_" + side, 0.230, y, 0.18, 0.012, dark)
    ball("eye_light_" + side, 0.239, y - 0.003,
         0.184, 0.0035, white)

ball("muzzle_left", 0.234, 0.014, 0.144, 0.020, white)
ball("muzzle_right", 0.234, -0.014, 0.144, 0.020, white)
ball("nose", 0.253, 0, 0.154, 0.009, pink)

# 三角耳の形状を小さなSTLとして作成
vertices = [
    (-0.009, -0.025, 0), (-0.009, 0.025, 0),
    (-0.009, 0, 0.060),
    (0.009, -0.025, 0), (0.009, 0.025, 0),
    (0.009, 0, 0.060),
]
faces = [
    (0, 2, 1), (3, 4, 5),
    (0, 1, 4), (0, 4, 3),
    (1, 2, 5), (1, 5, 4),
    (2, 0, 3), (2, 3, 5),
]
lines = ["solid cat_ear"]
for face in faces:
    a, b, c = [vertices[i] for i in face]
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = (u[1]*v[2] - u[2]*v[1],
         u[2]*v[0] - u[0]*v[2],
         u[0]*v[1] - u[1]*v[0])
    length = sum(x*x for x in n) ** 0.5
    n = [x / length for x in n]
    lines += ["facet normal " + " ".join(map(str, n)),
              "outer loop"]
    for point in (a, b, c):
        lines.append("vertex " + " ".join(map(str, point)))
    lines += ["endloop", "endfacet"]
lines.append("endsolid cat_ear")
ear_path = folder / "cat_ear.stl"
ear_path.write_text("\n".join(lines), encoding="utf-8")

for side, y in [("left", 0.043), ("right", -0.043)]:
    visual("ear_" + side, f"0.17 {y} 0.205 0 0 0",
           "mesh", {"uri": ear_path.as_uri()}, cream)
    visual("ear_inner_" + side,
           f"0.180 {y} 0.215 0 0 0",
           "mesh",
           {"uri": ear_path.as_uri(), "scale": "0.2 0.65 0.65"},
           pink)

# 上向きのしっぽと丸い先端
visual("tail", "-0.035 0 0.155 0 -0.6 0",
       "cylinder", {"radius": 0.014, "length": 0.10}, cream)
ball("tail_tip", -0.063, 0, 0.196, 0.017, white)

# 車輪は落ち着いた茶色にする。重複したmaterialも整理
for wheel in ("wheel_left_link", "wheel_right_link"):
    for v in robot.findall(f"./link[@name='{wheel}']/visual"):
        for material in list(v.findall("material")):
            v.remove(material)
        material = ET.SubElement(v, "material")
        for tag in ("ambient", "diffuse"):
            ET.SubElement(material, tag).text = "0.25 0.18 0.13 1"

# キー操作の前後速度をゆっくりにする
for output in world.findall("./plugin/output"):
    if output.text:
        output.text = output.text.replace("x: 0.5", "x: 0.12")
        output.text = output.text.replace("x: -0.5", "x: -0.12")

# Spaceキーで停止できるようにする
plugin = ET.SubElement(
    world, "plugin",
    filename="libignition-gazebo-triggered-publisher-system.so",
    name="ignition::gazebo::systems::TriggeredPublisher")
inp = ET.SubElement(plugin, "input",
                    type="ignition.msgs.Int32",
                    topic="/keyboard/keypress")
ET.SubElement(inp, "match", field="data").text = "32"
ET.SubElement(plugin, "output",
              type="ignition.msgs.Twist",
              topic="/cmd_vel").text = \
    "linear: {x: 0.0}, angular: {z: 0.0}"

ET.indent(tree, space="  ")
target = folder / "world_cat.sdf"
tree.write(target, encoding="utf-8", xml_declaration=True)
ET.parse(target)
print("猫型モデルを作成しました：", target)
