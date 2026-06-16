import time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan, PointCloud2
from rosgraph_msgs.msg import Clock


def stamp_to_sec(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


class MultiStampMonitor(Node):
    def __init__(self):
        super().__init__('multi_stamp_monitor')

        self.clock = None
        self.data = {}

        topics = {
            'front': ('/front/point_cloud', PointCloud2),
            'rear': ('/rear/point_cloud', PointCloud2),
            'merged': ('/merged/point_cloud', PointCloud2),
            'scan': ('/scan', LaserScan),
        }

        for name, (topic, msg_type) in topics.items():
            self.data[name] = {
                'stamp': None,
                'rx_wall': None,
                'width': None,
            }
            self.create_subscription(
                msg_type,
                topic,
                self.make_cb(name),
                qos_profile_sensor_data
            )

        self.create_subscription(Clock, '/clock', self.clock_cb, 10)
        self.create_timer(0.2, self.print_status)

    def clock_cb(self, msg):
        self.clock = stamp_to_sec(msg.clock)

    def make_cb(self, name):
        def cb(msg):
            self.data[name]['stamp'] = stamp_to_sec(msg.header.stamp)
            self.data[name]['rx_wall'] = time.time()
            if hasattr(msg, 'width'):
                self.data[name]['width'] = msg.width
        return cb

    def fmt(self, v):
        if v is None:
            return 'None'
        if isinstance(v, float):
            return f'{v:.3f}'
        return str(v)

    def print_status(self):
        now_wall = time.time()
        parts = [f'sim={self.fmt(self.clock)}']

        for name in ['front', 'rear', 'merged', 'scan']:
            d = self.data[name]
            stamp = d['stamp']
            age = None if self.clock is None or stamp is None else self.clock - stamp
            rx_gap = None if d['rx_wall'] is None else now_wall - d['rx_wall']
            width = d['width']

            if width is None:
                parts.append(
                    f'{name}: stamp={self.fmt(stamp)} age={self.fmt(age)} rx={self.fmt(rx_gap)}'
                )
            else:
                parts.append(
                    f'{name}: stamp={self.fmt(stamp)} age={self.fmt(age)} rx={self.fmt(rx_gap)} width={width}'
                )

        print(' | '.join(parts), flush=True)


def main():
    rclpy.init()
    node = MultiStampMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()