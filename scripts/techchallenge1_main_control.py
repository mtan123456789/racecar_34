#!/usr/bin/env python
import rospy
from ackermann_msgs.msg import AckermannDriveStamped
from std_msgs.msg import *

class MainControl:
    #Other nodes will be controlled from here
    def __init__(self):
        self.node_name = "tech_challenge_1_main_control_node"
        rospy.Subscriber("/transition", String, self.transition_callback)
        self.joy_control = rospy.Subscriber("/vesc/joy", Joy, joy_buttons)
        self.sub_blob_detection = rospy.Subscriber("blob_detections", BlobDetections, blob_cb)
        self.sub_winter = rospy.Subscriber("main_drive", AckermannDriveStamped, movement_cb) 

        #Add publisher for every node that is to be controlled
        self.wall_pub = rospy.Publisher("/wallfollow", String, queue_size=1)
        #rospy.Publisher("/transition", String, queue_size=10)

	#

    #When message recieved from /transition topic, start the appropriate node by publishing a message 
    def transition_callback(self, msg):
        if msg.data == "follow left" or msg.data == "follow right" or msg.data == "stop follow"
            self.wall_pub.publish(msg)

    def movement_cb(self, msg):
        
    #Optional function to start programs using the joystick
    #def joy_buttons(self, msg):


if __name__=="__main__":
    rospy.init_node("MainControl")
    node = Control()
    rospy.spin()