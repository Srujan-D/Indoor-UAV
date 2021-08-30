#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from indoor_uav.msg import Progress,Feedback
# from indoor_uav.scripts.planner import Node

class Node():    
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        self.parent = None

class Controller():
	def __init__(self):
		rospy.init_node("controller_node", anonymous=True)
		self.rate = rospy.Rate(30)
		
		self.current_node = 0
		self.reach = 0
		self.quad_at = 0

		# self.path = [Node(0, 0, 5), Node(-9, 0, 5), Node(-9, 7, 5), Node(6, 7, 5), Node(21, 7, 5), Node(21, 1, 5), Node(6, 1, 5), Node(-9, 1, 5), Node(-9, -5, 5), Node(6, -5, 5), Node(21, -5, 5), Node(21, -11, 5), Node(6, -11, 5), Node(-9, -11, 5), Node(-9, 17, 5), Node(6, -17, 5), Node(21, -17, 5), Node(21, -23, 5), Node(6, -23, 5), Node(9, -23, 5), Node(9, -29, 5), Node(6, -29, 5), Node(21, -29, 5), Node(21, 7, 5), Node(-9, 7, 5)]
		self.path = [Node(0,0,5), Node(6,0,5), Node(6,-5,5), Node(6,-11,5), Node(6,-17,5), Node(6,-23,5), Node(6, -29, 5)]

		self.next_goal = PoseStamped()
		self.current_progress = Progress()

		self.point_publisher = rospy.Publisher('/iris/next_point', PoseStamped, queue_size=10)
		self.progress_publisher = rospy.Publisher('/iris/progress', Progress, queue_size=10)

		rospy.Subscriber("/iris/feedback", Feedback, self.FeedbackCallback)

	def SetNextGoal(self):
		while not rospy.is_shutdown():
			if (self.current_node == len(self.path)):
				print("Done\n")
				break

			# Send the pose position of the target point
			self.next_goal.pose.position.x = self.path[self.current_node].x
			self.next_goal.pose.position.y = self.path[self.current_node].y
			self.next_goal.pose.position.z = self.path[self.current_node].z

			self.next_goal.header.stamp = rospy.Time.now()
			self.next_goal.header.frame_id = 'base_link'

			self.current_progress.total_length = len(self.path) - 1
			self.current_progress.current_node = self.current_node

			self.point_publisher.publish(self.next_goal)
			self.progress_publisher.publish(self.current_progress)

			if(self.reach == 1 and self.quad_at == self.current_node + 1):
				# Set the target point to the next waypoint
				print("Going to next waypoint")
				self.current_node = self.quad_at
			
			self.rate.sleep()

	def FeedbackCallback(self, feedback):
		self.reach = feedback.reach_current
		self.quad_at = feedback.quad_current


if __name__ == '__main__':
	o = Controller()
	o.SetNextGoal()
	


