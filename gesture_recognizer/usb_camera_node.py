"""USB camera publisher node."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2


class UsbCameraNode(Node):
    """Simple camera publisher for a USB webcam."""

    def __init__(self):
        super().__init__('usb_camera_node')
        self.declare_parameter('device_id', 0)
        self.declare_parameter('frame_id', 'camera_frame')
        self.declare_parameter('topic', '/camera/image_raw/uncompressed')

        device_id = self.get_parameter('device_id').value
        self.frame_id = self.get_parameter('frame_id').value
        self.topic = self.get_parameter('topic').value

        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(device_id)
        if not self.cap.isOpened():
            self.get_logger().error(f'Unable to open camera device {device_id}')

        self.publisher_ = self.create_publisher(Image, self.topic, 10)
        self.timer = self.create_timer(1.0 / 30.0, self.timer_callback)

    def timer_callback(self):
        if not self.cap.isOpened():
            return
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().warning('Failed to capture image')
            return
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        self.publisher_.publish(msg)

    def destroy_node(self):
        if self.cap.isOpened():
            self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = UsbCameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
