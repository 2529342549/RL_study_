#!/usr/bin/env python
#################################################################################
# Copyright 2018 IWIN, SJTU
#
# https://iwin-fins.com
#################################################################################

# Authors: Hongbo Li, Han Wang#

import rospy
from geometry_msgs.msg import Twist, Point, Quaternion
import tf
from math import radians, copysign, sqrt, pow, pi, atan2, cos, sin
from tf.transformations import euler_from_quaternion
import numpy as np
from sensor_msgs.msg import LaserScan

msg = """
control your Turtlebot3!
-----------------------
this is tb3_0
-----------------------
"""
tb3_0_pos = Point()
tb3_1_pos = Point()
tb3_2_pos = Point()
tb3_3_pos = Point()
tb3_4_pos = Point()
tb3_4_vel = Twist()
tb3_0_vel = Twist()
K1 = 0.2
K2 = 0.1
K3 = 1
detect_R = 1
safe_r = 0.3
ID = 0


class GotoPoint():
    def __init__(self):
        rospy.init_node('tb3_0', anonymous=False)
        # turtlebot3_model = rospy.get_param("model")

        rospy.on_shutdown(self.shutdown)
        self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=5)
        self.tb3_0_positon = rospy.Publisher('/tb3_0_pos', Point, queue_size=5)
        position = Point()
        move_cmd = Twist()
        r = rospy.Rate(10)
        self.tf_listener = tf.TransformListener()
        self.odom_frame = '/tb3_0/odom'
        try:
            self.tf_listener.waitForTransform(self.odom_frame, '/tb3_0/base_footprint', rospy.Time(),
                                              rospy.Duration(1.0))
            self.base_frame = '/tb3_0/base_footprint'
        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            try:
                self.tf_listener.waitForTransform(self.odom_frame, '/tb3_0/base_link', rospy.Time(),
                                                  rospy.Duration(1.0))
                self.base_frame = '/tb3_0/base_link'
            except (tf.Exception, tf.ConnectivityException, tf.LookupException):
                rospy.loginfo("Cannot find transform between odom and base_link or base_footprint")
                rospy.signal_shutdown("tf Exception")
        print 66
        (position, rotation) = self.get_odom()
        rospy.Subscriber('/tb3_1_pos', Point, point_callback_1)
        rospy.Subscriber('/tb3_2_pos', Point, point_callback_2)
        rospy.Subscriber('/tb3_3_pos', Point, point_callback_3)
        rospy.Subscriber('/tb3_4_pos', Point, point_callback_4)
        rospy.Subscriber('/tb3_4_vel', Twist, vel_callback_4)
        self.tb3_0_positon.publish(position)
        print 11
        global tb3_0_vel
        global tb3_0_pos
        global tb3_1_pos
        global tb3_2_pos
        global tb3_3_pos
        global tb3_4_pos

        tb3_0_vel_delta_x = (
                    (tb3_1_pos.x - position.x) + (tb3_2_pos.x - position.x - 2) + (tb3_3_pos.x - position.x - 2) + (
                        tb3_4_pos.x - position.x - 4))
        tb3_0_vel_delta_y = (
                    (tb3_1_pos.y - position.y + 4) + (tb3_2_pos.y - position.y) + (tb3_3_pos.y - position.y + 4) + (
                        tb3_4_pos.y - position.y + 2))
        if abs(tb3_0_vel_delta_x) < 0.05:
            tb3_0_vel_delta_x = 0
        if abs(tb3_0_vel_delta_y) < 0.05:
            tb3_0_vel_delta_y = 0
        goal_x = tb3_0_vel_delta_x + position.x
        goal_y = tb3_0_vel_delta_y + position.y
        goal_z = atan2(tb3_0_vel_delta_y, tb3_0_vel_delta_x)
        print tb3_0_vel_delta_x;
        print tb3_0_vel_delta_y
        if tb3_0_vel_delta_x == 0 and tb3_0_vel_delta_y == 0:
            goal_z = 0

        global tb3_4_vel
        angular_now = rotation
        phi = goal_z
        avoid_delta = 0

        tb3_0_pos = position
        obstacle_pos = self.lidar(position)
        rospy.loginfo('position.x of the obstacle : %f', obstacle_pos.x)
        rospy.loginfo('position.y of the obstacle : %f', obstacle_pos.y)

        # pos_nodes=[tb3_0_pos,tb3_1_pos,tb3_2_pos,tb3_3_pos,tb3_4_pos]
        pos_nodes = [tb3_0_pos, obstacle_pos]
        temp_x_sum = 0
        temp_y_sum = 0
        for i in range(len(pos_nodes)):
            print i
            if i != ID:
                print i
                print pos_nodes[i].x
                r = sqrt(pow(pos_nodes[i].x - pos_nodes[ID].x, 2) + pow(pos_nodes[i].y - pos_nodes[ID].y, 2))
                print ('distance between %d is %f' % (i, r))
                if r > safe_r and r < detect_R:
                    # temp_x=(pow(detect_R,2)-pow(safe_r,2))*(pos_nodes[i].x-pos_nodes[ID].x)
                    # temp_y=(pow(detect_R,2)-pow(safe_r,2))*(pos_nodes[i].y-pos_nodes[ID].y)
                    # temp_d2=pow(pos_nodes[i].x-pos_nodes[ID].x,2)+pow(pos_nodes[i].y-pos_nodes[ID].y,2)
                    # temp_fenmu=temp_d2-pow(safe_r,2)
                    # temp_fenmu=pow(temp_fenmu,3)
                    # temp_x=temp_x/temp_fenmu*(temp_d2-pow(detect_R,2))
                    # temp_y=temp_y/temp_fenmu*(temp_d2-pow(detect_R,2))
                    # temp_x_sum=temp_x_sum+temp_x
                    # temp_y_sum=temp_y_sum+temp_y

                    temp_x = (1 / r - 1 / detect_R) * (pos_nodes[ID].x - pos_nodes[i].x)
                    temp_y = (1 / r - 1 / detect_R) * (pos_nodes[ID].y - pos_nodes[i].y)
                    temp_fenmu = pow(r, 3)
                    temp_x = temp_x / temp_fenmu
                    temp_y = temp_y / temp_fenmu
                    temp_x_sum = temp_x_sum + temp_x
                    temp_y_sum = temp_y_sum + temp_y

        avoid_delta = temp_x_sum * cos(angular_now) + temp_y_sum * sin(angular_now)
        tb3_0_vel.linear.x = K1 * (tb3_0_vel_delta_x * cos(angular_now) + tb3_0_vel_delta_y * sin(
            angular_now)) + tb3_4_vel.linear.x + K3 * avoid_delta
        delta_theta = self.compute_theta(phi, angular_now)
        print ('the delta_ang=%f' % (delta_theta))
        # tb3_3_vel.angular.z=tb3_4_vel.angular.z+K2*(tb3_0_vel_delta_x+tb3_0_vel_delta_y)
        tb3_0_vel.angular.z = K2 * delta_theta + tb3_4_vel.angular.z
        self.cmd_vel.publish(tb3_0_vel)

    def lidar(self, tb_pos):
        msg = rospy.wait_for_message("scan", LaserScan)
        LIDAR_ERR = 0.05
        LIDAR_MAX = 1.5
        obstacle = []
        min_dis = 10
        min_ang = 0
        min_point = Point()
        for i in range(360):
            if i <= 45 or i > 315:
                obstacle_pos = Point()
                if msg.ranges[i] >= LIDAR_ERR and msg.ranges[i] <= LIDAR_MAX:
                    obstacle_pos.x = tb_pos.x + msg.ranges[i] * cos(i)
                    obstacle_pos.y = tb_pos.y + msg.ranges[i] * sin(i)
                    obstacle.append(obstacle_pos)
                    if msg.ranges[i] < min_dis:
                        min_dis = msg.ranges[i]
                        min_ang = i
        if min_dis < 10:
            min_point.x = tb_pos.x + min_dis * cos(i)
            min_point.y = tb_pos.y + min_dis * sin(i)
        else:
            min_point.x = 10
        return min_point

    def compute_theta(self, theta, rotation1):
        if theta * rotation1 < 0:
            if theta > 0:
                if abs(rotation1) + theta <= pi:
                    w = abs(rotation1) + theta
                else:
                    w = -(2 * pi + rotation1 - theta)
            else:
                if rotation1 + abs(theta) <= pi:
                    w = -(abs(theta) + rotation1)
                else:
                    w = (2 * pi - rotation1 + theta)
        else:
            w = theta - rotation1
        return w

    def get_odom(self):
        try:
            (trans, rot) = self.tf_listener.lookupTransform(self.odom_frame, self.base_frame, rospy.Time(0))
            rotation = euler_from_quaternion(rot)

        except (tf.Exception, tf.ConnectivityException, tf.LookupException):
            rospy.loginfo("TF Exception")
            return

        return (Point(*trans), rotation[2])

    def shutdown(self):
        self.cmd_vel.publish(Twist())
        rospy.sleep(1)


def point_callback_1(data):
    global tb3_1_pos
    tb3_1_pos.x = data.x
    tb3_1_pos.y = data.y


def point_callback_2(data):
    global tb3_2_pos
    tb3_2_pos.x = data.x
    tb3_2_pos.y = data.y


def point_callback_3(data):
    global tb3_3_pos
    tb3_3_pos.x = data.x
    tb3_3_pos.y = data.y


def point_callback_4(data):
    global tb3_4_pos
    tb3_4_pos.x = data.x
    tb3_4_pos.y = data.y


def vel_callback_4(data):
    global tb3_4_vel
    tb3_4_vel = data


if __name__ == '__main__':
    try:
        while not rospy.is_shutdown():
            print(msg)
            GotoPoint()

    except:
        rospy.loginfo("shutdown program.")
