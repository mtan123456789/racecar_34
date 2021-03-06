#!/usr/bin/env python
import os
import operator
import cv2
import rospy
import time
from std_msgs.msg import *
from sensor_msgs.msg import Image
from racecar_34.msg import BlobDetections
from cv_bridge import CvBridge, CvBridgeError
import threading
import numpy as np
from geometry_msgs.msg import Point
from matplotlib import pyplot as plt


class Echo:
    def __init__(self):
        self.node_name = "Echo"
        self.header = std_msgs.msg.Header()
        self.blob_colors = []
        self.blob_sizes = []
        self.blob_positions = []
        self.last_time_saved = rospy.get_time()
        self.thread_lock = threading.Lock()
        self.sub_image = rospy.Subscriber("/camera/rgb/image_rect_color",\
                Image, self.cbImage, queue_size=1)
        self.pub_image = rospy.Publisher("~echo_image",\
                Image, queue_size=1)
        self.pub_blob_detections = rospy.Publisher("blob_detections",BlobDetections, queue_size=1)
        self.pub_exploratory_matches = rospy.Publisher("/exploring_challenge", String, queue_size = 1)
        self.bridge = CvBridge()

        rospy.loginfo("[%s] Initialized." %(self.node_name))

	# This should NOT be in the callback -- SLOW
        os.chdir("/home/racecar/racecar-ws/src/week_3/template_images")
        template_ari = cv2.imread("ari.png", 0)
        template_racecar = cv2.imread("racecar.png", 0)
        template_sirtash = cv2.imread("sirtash.png", 0)
        template_cat = cv2.imread("cat.png", 0)
        hist_ari = cv2.calcHist([template_ari],[0],None,[256],[0,256])
        hist_racecar = cv2.calcHist([template_racecar],[0],None,[256],[0,256])
        hist_sirtash = cv2.calcHist([template_sirtash],[0],None,[256],[0,256])
        hist_cat = cv2.calcHist([template_cat],[0],None,[256],[0,256])
        self.hist_list = [hist_ari, hist_racecar, hist_sirtash, hist_cat]
        rospy.loginfo("Made Hists and Templates")

	# This should also not be in callback -- never changes why waist time
	# creating it each time the callback happens
	self.red_lower = np.array([0,150,80])
        self.red_upper = np.array([6,255,255])
        self.yellow_lower = np.array([20,175,100])
        self.yellow_upper = np.array([30,255,255])
        self.green_lower = np.array([50,100,100])
        self.green_upper = np.array([70,255,255])
        self.blue_lower = np.array([110, 175, 100])
        self.blue_upper = np.array([130, 255, 255])
        self.pink_lower = np.array([160, 100, 100])
        self.pink_upper = np.array([170, 255, 255])

    def cbImage(self,image_msg):
        thread = threading.Thread(target=self.processImage,args=(image_msg,))
        thread.setDaemon(True)
        thread.start()


    def processImage(self, image_msg):
        if not self.thread_lock.acquire(False):
            return

        isPink = False
        image_cv = self.bridge.imgmsg_to_cv2(image_msg)
        height,width,depth = image_cv.shape
        image_cv_hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)

        green_mask = cv2.inRange(image_cv_hsv, self.green_lower, self.green_upper)
        yellow_mask = cv2.inRange(image_cv_hsv, self.yellow_lower, self.yellow_upper)
        red_mask = cv2.inRange(image_cv_hsv, self.red_lower, self.red_upper)
        blue_mask = cv2.inRange(image_cv_hsv, self.blue_lower, self.blue_upper)
        pink_mask = cv2.inRange(image_cv_hsv, self.pink_lower, self.pink_upper)

	# MAKING THINGS GREY AND CREATING SO MANY IMAGES BREAKS EVERYTHING TOOOOOO SLOW
	# This was the real problem -- slowed it down from 5hz to 2hz
	'''
        red_obj = cv2.bitwise_and(image_cv, image_cv, mask = red_mask)
        yellow_obj = cv2.bitwise_and(image_cv, image_cv, mask = yellow_mask)
        green_obj = cv2.bitwise_and(image_cv, image_cv, mask = green_mask)
        blue_obj = cv2.bitwise_and(image_cv, image_cv, mask = blue_mask)
        pink_obj = cv2.bitwise_and(image_cv, image_cv, mask = pink_mask)

        # full_image = red_obj + yellow_obj + green_obj
        full_image = [red_obj, yellow_obj, green_obj, blue_obj, pink_obj]
	'''
	full_image = [red_mask, yellow_mask, green_mask, blue_mask, pink_mask]

        for i in range(0, len(full_image)):
	    '''
            im_gray = cv2.cvtColor(full_image[i], cv2.COLOR_BGR2GRAY)
            ret, tresh = cv2.threshold(im_gray,127,255,0)
            contours, hierarchy = cv2.findContours(im_gray,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	    '''
	    contours, hierarchy = cv2.findContours(full_image[i],cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            sorted_contours = sorted(contours, key = lambda x: cv2.contourArea(x), reverse=True)
	    # don't look at all contours what if there are TONS? -- SLOW
            if len(sorted_contours) > 10:
		sorted_contours = sorted_contours[0:9]
            for contour in contours:
                if cv2.contourArea(contour) > 1000:
                    if i == 0:
                        text = "THE RED COLOR"
                        self.blob_colors.append(ColorRGBA(255,0,0,1))
                        text_color = (0,0,255)
                        blob_message = "red"
                    if i == 1:
                        text = "THE YELLOW COLOUR"
                        self.blob_colors.append(ColorRGBA(0,255,255,1))
                        text_color = (0,255,255)
                        blob_message = "yellow"
                    if i == 2:
                        text = "THE GREEN COLLAR"
                        self.blob_colors.append(ColorRGBA(0,255,0,1))
                        text_color = (0,255,0)
                        blob_message = "green"
                    if i == 3:
                        text = "tHe BLUE CLOR"
                        self.blob_colors.append(ColorRGBA(255,0,0,1))
                        text_color = (255,0,0)
                        blob_message = "blue"
                    if i == 4:
                        text = "Is iT  PINK"
                        text_color = (147,20,255)
                        blob_message = "pink"
                        isPink = True
                    x,y,w,h = cv2.boundingRect(contour)
                    cv2.rectangle(image_cv, (x,y), (x+w, y+h), (147,20,255),2)
                    if isPink:
                        crop_img_b4 = cv2.bitwise_not(image_cv_hsv, image_cv_hsv, mask = pink_mask)
                        crop_img_b2 = crop_img_b4[y: y + h, x: x + w]

                        crop_img = cv2.cvtColor(crop_img_b2, cv2.COLOR_BGR2GRAY)

                        hist = cv2.calcHist([crop_img],[0],None,[256],[0,256])

                        results = [0]
                        
                        for hist_pic in self.hist_list:
                            results.append(cv2.compareHist(hist, hist_pic, cv2.cv.CV_COMP_CORREL))
                        max_index, max_value = max(enumerate(results), key=operator.itemgetter(1))
                        blob_message = str(max_index)
                        if max_value > 0:
                            if max_index == 1:
                                blob_message = "R E"
                            elif max_index == 2:
                                blob_message = "raseKar"
                            elif max_index == 3:
                                blob_message = "sErtacsh"
                            elif max_index == 4:
                                blob_message = "kiTTy"
			return
                    else:
                        shape = "unidentified"
			peri = cv2.arcLength(contour, True)
			approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
			area = cv2.contourArea(contour)
			rect_area = w*h
			extent = (float(area)/rect_area)
			
			if len(approx) == 4:
				if extent >= 0.7:
					shape ="square"
				else:
					shape = "rhombus"
			elif len(approx) == 12:
				if extent >= 0.69:
					shape = "X"
				else:
					shape = "+"
			else:
				shape = "circle"

			blob_message = shape
			#text = 
                    cv2.putText(image_cv,text,(x,y),4,1,text_color)
                    cv2.circle(image_cv, (x+(w/2),y+(h/2)), 5, (255,0,0),5)
                    self.blob_sizes.append(Float64(h))
                    print(Point(x+(w/2),y+(h/2),0))
                    self.blob_positions.append(Point(x+(w/2),y+(h/2),0))
                    self.ChallengePublisher(blob_message, image_cv)
	    
        try:
            print(self.header)
            print(self.blob_colors)
            print(self.blob_sizes)
            print(self.blob_positions)
            self.pub_image.publish(\
                self.bridge.cv2_to_imgmsg(image_cv, "bgr8"))
            self.pub_image.publish(self.bridge.cv2_to_imgmsg(image_cv, "bgr8"))
            self.pub_blob_detections.publish(BlobDetections(self.header,self.blob_colors,self.blob_sizes,self.blob_positions))
	    
            del self.blob_colors[:]
            del self.blob_sizes[:]
            del self.blob_positions[:]

        except CvBridgeError as e:
            print(e)
        self.thread_lock.release()

    def ChallengePublisher(self, blob_message, image):
        current_time = rospy.get_time()
        if current_time - self.last_time_saved > 1.5:
            os.chdir("/home/racecar/challenge_photos")
            cv2.imwrite(blob_message + str(current_time) + ".jpg", image)
            self.last_time_saved = current_time
        self.pub_exploratory_matches.publish(blob_message)

if __name__=="__main__":
    rospy.init_node('Echo')
    e = Echo()
    rospy.spin()

