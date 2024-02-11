import numpy as np
import cv2
from grade_paper import ProcessPage
import os

class PaperFinder():
	def __init__(self):

		self.path = ''
		self.my = None
		self.mx = None
		self.answers = []
		self.answer_key = {}
		self.score = 0

	def clockwise_sort(self ,x):
		return (np.arctan2(x[0] - self.mx, x[1] - self.my) + 0.5 * np.pi) % (2*np.pi)
	
	def findpaper(self, img):
		cv2.namedWindow('Original Image')
		cv2.namedWindow('Scanned Paper')

		#ret, image = cap.read()
		image = cv2.imread(img)
		ratio = len(image[0]) / 2000.0 #used for resizing the image
		original_image = image.copy() #make a copy of the original image

		#find contours on the smaller image because it's faster
		image = cv2.resize(image, (0,0), fx=1/ratio, fy=1/ratio)

		#gray and filter the image
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		blur = cv2.GaussianBlur(gray, (5, 5), 0)

		#bilateral filtering removes noise and preserves edges
		gray = cv2.bilateralFilter(blur, 11, 17, 17)
		#find the edges
		edged = cv2.Canny(gray, 150, 300)

		#find the contours
		contours, temp_img = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

		#find the biggest contour
		rectCont = []
		biggestContour = None

		# loop over our contours
		for contour in contours:
    	# Convert contour points to np.int32
			contour = contour.astype(np.int32)
    		# Calculate perimeter
    		# Handle further processing
			peri = cv2.arcLength(contour, True)
			approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

			#return the biggest 4 sided approximated contour
			if len(approx) == 4:
				rectCont.append(approx)
		
		rectCont = sorted(rectCont, key=cv2.contourArea, reverse=True)
		biggestContour = rectCont[0]

		#used for the perspective transform
		points = []
		desired_points = [[0,0], [425, 0], [425, 550], [0, 550]] #8.5in by 11in. paper

		#convert to np.float32
		desired_points = np.float32(desired_points)

		#extract points from contour
		if biggestContour is not None:
			for i in range(0, 4):
				points.append(biggestContour[i][0])

		mx = sum(point[0] for point in points) / 4
		my = sum(point[1] for point in points) / 4

		self.mx = mx
		self.my = my

		#sort points
		points.sort(key=self.clockwise_sort, reverse=True)

		#convert points to np.float32
		points = np.float32(points)

		#resize points so we can take the persepctive transform from the
		#original image giving us the maximum resolution
		paper = []
		points *= ratio
		answers = 1
		if biggestContour is not None:
			#create persepctive matrix
			M = cv2.getPerspectiveTransform(points, desired_points)
			#warp persepctive
			paper = cv2.warpPerspective(original_image, M, (425, 550))
			answers, paper, codes = ProcessPage(paper)
			cv2.imwrite(os.path.join(self.path, 'paperResults.jpg'), paper)

		# draw the contour
		if biggestContour is not None:
			if answers != -1:
				cv2.drawContours(image, [biggestContour], -1, (0, 255, 0), 3)
				print(answers)
				self.answers = answers
				if codes is not None:
					print(codes)

			else:
				cv2.drawContours(image, [biggestContour], -1, (0, 0, 255), 3)

		print("image.jpg saved")
		cv2.imwrite(os.path.join(self.path, 'image.jpg'), image)
