import json
import math
import sys
import time
from pathlib import Path

from cat_patrol import CatPatrol, main as patrol_main


class PlannedCat(CatPatrol):
    def __init__(self, names):
        self.names = names
        super().__init__()

    def on_odom(self, msg):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z))
        self.pose = (p.x, p.y, yaw)
        self.last_odom = time.monotonic()

        if self.goals is None:
            # 毎回同じ場所へ行くよう、座標を固定する
            locations = {
                "ごはん": (0.6, 0.0),
                "窓辺": (0.6, 0.6),
                "寝床": (0.0, 0.0),
            }
            self.goals = [
                (name, *locations[name]) for name in self.names]
            self.goal_started = time.monotonic()
            self.get_logger().info(
                "AIの移動計画：" + " → ".join(self.names))
            self.get_logger().info(
                self.names[0] + "へ出発します！")

    def control(self):
        was_done = self.done
        super().control()
        if not was_done and self.done and self.index == len(self.goals or []):
            self.get_logger().info("AIのお願いを実行しました！")


if __name__ == "__main__":
    import cat_patrol
    plan = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    names = [step["destination"] for step in plan["steps"]]
    allowed = {"ごはん", "窓辺", "寝床"}
    if not names or any(name not in allowed for name in names):
        raise ValueError("移動計画が不正です")
    cat_patrol.CatPatrol = lambda: PlannedCat(names)
    patrol_main()
