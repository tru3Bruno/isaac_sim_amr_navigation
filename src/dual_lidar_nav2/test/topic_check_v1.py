import time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, PointCloud2
from rosgraph_msgs.msg import Clock


def stamp_to_sec(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


class TopicStampMonitor(Node):
    def __init__(self):
        super().__init__('topic_stamp_monitor')

        self.scan_stamp = None
        self.cloud_stamp = None
        self.clock_stamp = None

        self.scan_wall_rx = None
        self.cloud_wall_rx = None

        self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_cb,
            qos_profile_sensor_data
        )

        self.create_subscription(
            PointCloud2,
            '/merged/point_cloud',
            self.cloud_cb,
            qos_profile_sensor_data
        )

        self.create_subscription(
            Clock,
            '/clock',
            self.clock_cb,
            10
        )

        self.create_timer(0.2, self.print_status)

    def scan_cb(self, msg):
        self.scan_stamp = stamp_to_sec(msg.header.stamp)
        self.scan_wall_rx = time.time()

    def cloud_cb(self, msg):
        self.cloud_stamp = stamp_to_sec(msg.header.stamp)
        self.cloud_wall_rx = time.time()

    def clock_cb(self, msg):
        self.clock_stamp = stamp_to_sec(msg.clock)

    def fmt(self, value):
        if value is None:
            return 'None'
        return f'{value:.6f}'

    def print_status(self):
        now_wall = time.time()

        if self.clock_stamp is None:
            sim_now = None
        else:
            sim_now = self.clock_stamp

        scan_age = None
        cloud_age = None
        stamp_delta = None

        if sim_now is not None and self.scan_stamp is not None:
            scan_age = sim_now - self.scan_stamp

        if sim_now is not None and self.cloud_stamp is not None:
            cloud_age = sim_now - self.cloud_stamp

        if self.scan_stamp is not None and self.cloud_stamp is not None:
            stamp_delta = self.scan_stamp - self.cloud_stamp

        scan_rx_gap = None
        cloud_rx_gap = None

        if self.scan_wall_rx is not None:
            scan_rx_gap = now_wall - self.scan_wall_rx

        if self.cloud_wall_rx is not None:
            cloud_rx_gap = now_wall - self.cloud_wall_rx

        print(
            f'sim_now={self.fmt(sim_now)} | '
            f'scan_stamp={self.fmt(self.scan_stamp)} '
            f'scan_age={self.fmt(scan_age)} '
            f'scan_rx_gap={self.fmt(scan_rx_gap)} | '
            f'cloud_stamp={self.fmt(self.cloud_stamp)} '
            f'cloud_age={self.fmt(cloud_age)} '
            f'cloud_rx_gap={self.fmt(cloud_rx_gap)} | '
            f'scan-cloud={self.fmt(stamp_delta)}',
            flush=True
        )


def main():
    rclpy.init()
    node = TopicStampMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()