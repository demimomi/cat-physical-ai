import math
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


def wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class CatPatrol(Node):
    def __init__(self):
        super().__init__("cat_patrol")
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.sub = self.create_subscription(
            Odometry, "/model/demoRobot/odometry", self.on_odom, 10)
        self.pose = None
        self.last_odom = None
        self.goals = None
        self.index = 0
        self.done = False
        self.wait_until = 0.0
        self.started = time.monotonic()
        self.goal_started = self.started
        self.create_timer(0.1, self.control)
        self.get_logger().info("位置情報を待っています…")

    def on_odom(self, msg):
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        yaw = math.atan2(
            2 * (q.w * q.z + q.x * q.y),
            1 - 2 * (q.y * q.y + q.z * q.z))
        self.pose = (p.x, p.y, yaw)
        self.last_odom = time.monotonic()

        if self.goals is None:
            # 開始位置・向きを基準に目的地を決める
            c, s = math.cos(yaw), math.sin(yaw)
            self.goals = []
            for name, dx, dy in [
                ("ごはん", 0.6, 0.0),
                ("窓辺", 0.6, 0.6),
                ("寝床", 0.0, 0.0),
            ]:
                self.goals.append(
                    (name, p.x + c * dx - s * dy,
                     p.y + s * dx + c * dy))
            self.goal_started = time.monotonic()
            self.get_logger().info(
                f"開始位置：({p.x:.2f}, {p.y:.2f})")
            self.get_logger().info("ごはんへ出発します！")

    def command(self, speed=0.0, turn=0.0):
        msg = Twist()
        msg.linear.x = float(speed)
        msg.angular.z = float(turn)
        self.pub.publish(msg)

    def fail(self, message):
        self.command()
        self.get_logger().error(message)
        self.done = True

    def control(self):
        now = time.monotonic()
        if self.done:
            self.command()
            return

        if self.pose is None:
            self.command()
            if now - self.started > 20:
                self.fail("位置情報が来ません。接続と▶を確認してください。")
            return

        if now - self.last_odom > 3:
            self.fail("位置情報が途切れたため停止しました。")
            return

        if now < self.wait_until:
            self.command()
            return

        if now - self.goal_started > 180:
            self.fail("目的地に到着できず、時間制限で停止しました。")
            return

        name, gx, gy = self.goals[self.index]
        x, y, yaw = self.pose
        dx, dy = gx - x, gy - y
        distance = math.hypot(dx, dy)

        if distance < 0.06:
            self.command()
            self.get_logger().info(f"{name}に到着！")
            self.index += 1
            if self.index == len(self.goals):
                self.get_logger().info(f"移動完了。{name}で待っています！")
                self.done = True
            else:
                self.wait_until = now + 2
                self.goal_started = self.wait_until
                next_name = self.goals[self.index][0]
                self.get_logger().info(
                    f"2秒休んで、{next_name}へ向かいます。")
            return

        error = wrap(math.atan2(dy, dx) - yaw)
        turn = max(-0.6, min(0.6, 1.5 * error))
        speed = min(0.12, 0.5 * distance)
        if abs(error) > 0.3:
            speed = 0.0
        self.command(speed, turn)


def main():
    rclpy.init()
    node = CatPatrol()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        print("\n巡回を中断します。")
    finally:
        if rclpy.ok():
            # 終了時にも停止指令を繰り返し送る
            for _ in range(5):
                node.command()
                time.sleep(0.05)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
