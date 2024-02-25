import cv2
import numpy as np
from PIL import Image
from item_analysis import get_Score

epsilon = 12 #image error sensitivity
test_sensitivity_epsilon = 10 #bubble darkness error sensitivity
answer_choices = ['a', 'b', 'c', 'd', 'e', '?'] #answer choices

#load tracking tags
tags = [cv2.imread("markers/top_left.png", cv2.IMREAD_GRAYSCALE),
        cv2.imread("markers/top_right.png", cv2.IMREAD_GRAYSCALE),
        cv2.imread("markers/bottom_left.png", cv2.IMREAD_GRAYSCALE),
        cv2.imread("markers/bottom_right.png", cv2.IMREAD_GRAYSCALE)]

#test sheet specific scaling constants
scaling = [605.0, 835.0] #scaling factor for 8.5in. x 11in. paper
columns = [[72.0 / scaling[0], 33 / scaling[1]], [430.0 / scaling[0], 33 / scaling[1]]] #dimensions of the columns of bubbles
radius = 7.0 / scaling[0] #radius of the bubbles
spacing = [35.0 / scaling[0], 32.0 / scaling[1]] #spacing of the rows and columns

def ProcessPage(paper, answer_key):
    answers = [] #contains answers
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) #convert image to grayscale
    corners = FindCorners(paper) #find the corners of the bubbled area

    #if we can't find the markers, return an error
    if corners is None:
        return [-1], paper, [-1]

    #calculate dimensions for scaling
    dimensions = [corners[1][0] - corners[0][0], corners[2][1] - corners[0][1]]

    #iterate over test questions
    for k in range(0, 2): #columns
        for i in range(0, 25): #rows
            question_index = i if k == 0 else i + 25
            questions = []
            for j in range(0, 5): #answers
                #coordinates of the answer bubble
                x1 = int((columns[k][0] + j*spacing[0] - radius*1.5)*dimensions[0] + corners[0][0])
                y1 = int((columns[k][1] + i*spacing[1] - radius)*dimensions[1] + corners[0][1])
                x2 = int((columns[k][0] + j*spacing[0] + radius*1.5)*dimensions[0] + corners[0][0])
                y2 = int((columns[k][1] + i*spacing[1] + radius)*dimensions[1] + corners[0][1])

                #draw rectangles around bubbles
                cv2.rectangle(paper, (x1, y1), (x2, y2), (255, 0, 0), thickness=1, lineType=8, shift=0)

                #crop answer bubble
                questions.append(gray_paper[y1:y2, x1:x2])

            #find image means of the answer bubbles
            means = []

            #coordinates to draw detected answer
            x1 = int((columns[k][0] - radius*8)*dimensions[0] + corners[0][0])
            y1 = int((columns[k][1] + i*spacing[1] + 0.5*radius)*dimensions[1] + corners[0][1])

            #calculate the image means for each bubble
            for question in questions:
                means.append(np.mean(question))

            #sort by minimum mean; sort by the darkest bubble
            min_arg = np.argmin(means)
            min_val = means[min_arg]

            #find the second smallest mean
            means[min_arg] = 255
            min_val2 = means[np.argmin(means)]

            #check if the two smallest values are close in value
            if min_val2 - min_val < test_sensitivity_epsilon:
                #if so, then the question has been double bubbled and is invalid
                min_arg = 5

            #write the answer
            cv2.putText(paper, answer_choices[min_arg], (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 150, 0), 1)

            #append the answers to the array
            answers.append(answer_choices[min_arg])

            correct_answer = answer_key.get(str(question_index + 1))  # Assuming answer key starts from 1
            if correct_answer:  # Check if a correct answer is available
                correct_index = answer_choices.index(correct_answer)
                # coordinates of the correct answer bubble
                x1_correct = int((columns[k][0] + correct_index * spacing[0] - radius * 1.5) * dimensions[0] + corners[0][0])
                y1_correct = int((columns[k][1] + i * spacing[1] - radius) * dimensions[1] + corners[0][1])
                x2_correct = int((columns[k][0] + correct_index * spacing[0] + radius * 1.5) * dimensions[0] + corners[0][0])
                y2_correct = int((columns[k][1] + i * spacing[1] + radius) * dimensions[1] + corners[0][1])
                # Calculate the center coordinates of the circle
                cx = (x1_correct + x2_correct) // 2
                cy = (y1_correct + y2_correct) // 2

                circle_color = (0, 255, 0) if answer_choices[min_arg] == correct_answer else (0, 0, 255)
                # Draw filled circle on the correct answer bubble
                cv2.circle(paper, (cx, cy), int(radius), circle_color, 5)
    score = 0
    if answers[0] != -1:
        if answer_key and answers:
            score = get_Score(answers, answer_key)
            print(score)
    
    if score:
        cv2.putText(paper, f"Score: {str(score)}", (int(0.95*dimensions[0]), int(0.115*dimensions[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

    return answers, paper, score

def FindCorners(paper):
    gray_paper = cv2.cvtColor(paper, cv2.COLOR_BGR2GRAY) #convert image of paper to grayscale

    gray_paper = cv2.adaptiveThreshold(gray_paper, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    #scaling factor used later
    ratio = len(paper[0]) / 816.0

    #error detection
    if ratio == 0:
        return -1

    corners = [] #array to hold found corners

    #try to find the tags via convolving the image
    for tag in tags:
        tag = cv2.resize(tag, (0,0), fx=ratio, fy=ratio) #resize tags to the ratio of the image

        #convolve the image
        convimg = (cv2.filter2D(np.float32(cv2.bitwise_not(gray_paper)), -1, np.float32(cv2.bitwise_not(tag))))

        #find the maximum of the convolution
        corner = np.unravel_index(convimg.argmax(), convimg.shape)

        #append the coordinates of the corner
        corners.append([corner[1], corner[0]]) #reversed because array order is different than image coordinate

    #draw the rectangle around the detected markers
    for corner in corners:
        cv2.rectangle(paper, (corner[0] - int(ratio * 25), corner[1] - int(ratio * 25)),
        (corner[0] + int(ratio * 25), corner[1] + int(ratio * 25)), (0, 255, 0), thickness=2, lineType=8, shift=0)

    #check if detected markers form roughly parallel lines when connected
    if corners[0][0] - corners[2][0] > epsilon:
        return None

    if corners[1][0] - corners[3][0] > epsilon:
        return None

    if corners[0][1] - corners[1][1] > epsilon:
        return None

    if corners[2][1] - corners[3][1] > epsilon:
        return None

    return corners
