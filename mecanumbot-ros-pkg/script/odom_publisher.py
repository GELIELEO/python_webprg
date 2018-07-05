#!/usr/bin/env python
#coding=utf-8

import math
import time
import rospy
from geometry_msgs.msg import *
import tf2_ros.transform_broadcaster
import tf
'''
undo the encoder feedback,assume that every cmd
can be executed,and read the vel per x seconds

'''
class encoder:
    def __init__(self):
        self.pretime=rospy.rostime.get_time()
        self.curtime=rospy.rostime.get_time()
        self.x=0
        self.y=0
        self.th=0
        self.m=tf.TransformBroadcaster()
        self.t = geometry_msgs.msg.TransformStamped()
        self.t.header.frame_id = 'odom'
        #t.header.stamp = rospy.Time(0)
        self.t.child_frame_id = 'base_link'
        self.t.transform.translation.x = 0
        self.t.transform.translation.y = 0
        self.t.transform.translation.z = 0
        self.t.transform.rotation.w=0
        self.t.transform.rotation.x=0
        self.t.transform.rotation.y=0
        self.t.transform.rotation.z=0

    def callback(self,encoders):
        print "entered callback"
        self.curtime=rospy.rostime.get_time()
        dt = self.curtime - self.pretime
        self.pretime = self.curtime #要保证不停地发指令，即使不运动
        dx = encoders.linear.x*dt
        dy = encoders.linear.y*dt
        dth = encoders.angular.z*dt
        self.th += dth
        self.th = math.fmod(self.th, 2*math.pi)

        self.x += dx * math.cos(self.th) - dy * math.sin(self.th)
        self.y += dx * math.sin(self.th) + dy * math.cos(self.th)

        self.t.header.stamp =  rospy.Time.now()
        q=tf.transformations.quaternion_from_euler(0,0,self.th)
        self.t.transform.translation.x = self.x
        self.t.transform.translation.y = self.y
        self.t.transform.translation.z = 0
        self.t.transform.rotation.w=q[3]
        self.t.transform.rotation.x=q[0]
        self.t.transform.rotation.y=q[1]
        self.t.transform.rotation.z=q[2]
        self.m.sendTransformMessage(self.t)
        
        print self.t

    def run(self):
        rospy.Subscriber('/cmd_vel_mux/input/teleop', Twist, self.callback)
        rospy.spin()

if __name__=='__main__':
    rospy.init_node('odom_publisher', anonymous=False)
    en=encoder()
    en.run()