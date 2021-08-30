#!/usr/bin/env python
import rospy
import time
from std_msgs.msg import String, Int32, Bool
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import PoseStamped,PoseWithCovarianceStamped
from mavros_msgs.srv import *
from mavros_msgs.msg import *
from indoor_uav.msg import Progress, Feedback


class Commander:
	def __init__(self):
		rospy.init_node("commander_node", anonymous=True)
		self.rate = rospy.Rate(30)
		self.locPub = rospy.Publisher('/mavros/setpoint_position/local',PoseStamped,queue_size=10)
		self.feedbackPub = rospy.Publisher('/iris/feedback',Feedback,queue_size=10)
		rospy.Subscriber("/mavros/global_position/raw/fix", NavSatFix, self.globalPositionCallback)
		rospy.Subscriber("/mavros/local_position/pose", PoseStamped, self.localPositionCallback)
		rospy.Subscriber("/iris/next_point", PoseStamped, self.nextPointCallback)
		rospy.Subscriber("/iris/progress", Progress, self.progressCallback)

		self.latitude = 0.0
		self.longitude = 0.0
		self.altitude = 0.0

		self.current_order = 0
		self.reachFlag = 0        
		self.path_length = 0
		self.current_node = 0

		self.x = 0
		self.y = 0
		self.z = 0
		self.next_x = 0
		self.next_y = 0
		self.next_z = 0

		self.goalPos = PoseStamped()
		self.feedback = Feedback()

	def setArm(self):
		rospy.wait_for_service('/mavros/cmd/arming')
		try:
			armService = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)
			armService(True)
		except rospy.ServiceException as e:
			print("Service arm call failed: %s"%e)
			
	def setDisarm(self):
		rospy.wait_for_service('/mavros/cmd/arming')
		try:
			armService = rospy.ServiceProxy('/mavros/cmd/arming', mavros_msgs.srv.CommandBool)
			armService(False)
		except rospy.ServiceException as e:
			print("Service arm call failed: %s"%e)

	def setTakeoff(self):
		rospy.wait_for_service('/mavros/cmd/takeoff')
		try:
			takeoffService = rospy.ServiceProxy('/mavros/cmd/takeoff', mavros_msgs.srv.CommandTOL) 
			takeoffService(altitude = 3, latitude = 47.3977420, longitude = 8.5455936, min_pitch = 0, yaw = 0)
			# takeoffService(altitude = 50, latitude = latitude, longitude = longitude, min_pitch = 0, yaw = 0)
		except rospy.ServiceException as e:
			print("Service takeoff call failed: %s"%e)

	def setLand(self):
		rospy.wait_for_service('/mavros/cmd/land')
		try:
			landService = rospy.ServiceProxy('/mavros/cmd/land', mavros_msgs.srv.CommandTOL)
			landService(altitude = 0, latitude = 0, longitude = 0, min_pitch = 0, yaw = 0)
		except rospy.ServiceException as e:
			print("service land call failed: %s. The vehicle cannot land "%e)

	def setLocation(self):
		while not rospy.is_shutdown():

			if self.path_length + 1 == self.current_order:
				print("reach goal")
				self.setLand()
				break

			self.goalPos.pose.position.x = self.next_x
			self.goalPos.pose.position.y = self.next_y
			self.goalPos.pose.position.z = self.next_z
			self.goalPos.header.stamp = rospy.Time.now()
			self.goalPos.header.frame_id = 'base_link'

			self.feedback.quad_current = self.current_order
			self.feedback.reach_current = self.reachFlag

			self.locPub.publish(self.goalPos)
			self.setOffboard()

			if abs(self.x-self.goalPos.pose.position.x)<0.2 and abs(self.y-self.goalPos.pose.position.y)<0.2 and abs(self.z-self.goalPos.pose.position.z)<0.2:
				# current_node==self.current_order and
				print("Reached target")
				if self.reachFlag == 0:
					self.current_order = self.current_order + 1
					self.reachFlag = 1
				self.reachFlag = 1
			else:
				self.reachFlag = 0
			
			self.feedbackPub.publish(self.feedback)
			self.rate.sleep()

	def setOffboard(self):
		rospy.wait_for_service('/mavros/set_mode')
		try:
			landService = rospy.ServiceProxy('/mavros/set_mode', mavros_msgs.srv.SetMode)
			landService(custom_mode = "OFFBOARD")
		except rospy.ServiceException as e:
			print("service switch to offboard call failed: %s. The vehicle cannot land "%e)

	def globalPositionCallback(self, globalPos):
		self.latitude = globalPos.latitude
		self.altitude = globalPos.altitude
		self.longitude = globalPos.longitude

	def localPositionCallback(self, localPos):
		self.x = localPos.pose.position.x
		self.y = localPos.pose.position.y
		self.z = localPos.pose.position.z

	def nextPointCallback(self, nextPoint):
		self.next_x = nextPoint.pose.position.x
		self.next_y = nextPoint.pose.position.y
		self.next_z = nextPoint.pose.position.z

	def progressCallback(self, progress):
		self.current_node = progress.current_node
		self.path_length = progress.total_length


	def userInput(self):
		enter ='1'
		while (not rospy.is_shutdown()):
			print("1: Set mode to ARM")
			print("2: Set mode to DISARM")
			print("3: Set mode to TAKEOFF")
			print("4: Set mode to LAND")
			print("5: Set mode to AVOID OBSTACLE")
			print("e: Exit")
			enter = raw_input("Enter your input: ")
			if (enter=='1'):
				self.setArm()
			elif(enter=='2'):
				self.setDisarm()
			elif(enter=='3'):
				self.setTakeoff()
			elif(enter=='4'):
				self.setLand()
			elif(enter=='5'):
				self.setLocation()
			elif(enter=='e'): 
				print("Exit")
				break
			else:
				print("Invalid command!")

if __name__ == '__main__':
	o = Commander()
	o.userInput()