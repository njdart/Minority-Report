import cv2
import numpy as np
import json

scale = (0.8, 3)
offset = (100, 40)

# {
#     bounds: [
#         [
#             [x,y],
#             [x,y],
#             [x,y],
#             [x,y]
#         ],
#         [
#             [x,y],
#             [x,y],
#             [x,y],
#             [x,y]
#         ],
#         ...
#     ],
#     canvas: [
#         [x,y],
#         [x,y],
#         [x,y],
#         [x,y]
#     ]
# }

sampleCount = 5

def show(img):
    cv2.imshow("", img)
    cv2.waitKey()

def clockwise(points):
    rect = np.zeros_like(points)
    rect[0] = points[points.sum(axis=1).argmin()]
    rect[1] = points[np.diff(points, axis=1).argmin()]
    rect[2] = points[points.sum(axis=1).argmax()]
    rect[3] = points[np.diff(points, axis=1).argmax()]
    return rect

def overlay(original, overlay, alpha = 0.8):
    scaled = cv2.resize(overlay, (0,0), fx=scale[0], fy=scale[1])

    canvas = np.zeros_like(original)
    canvas[:overlay.shape[0], :overlay.shape[1]] = overlay

    matrix = np.array([
        [scale[0], 0,        offset[0]],
        [0,        scale[1], offset[1]],
        [0,        0,        1]
    ], dtype=np.float32)
    trans = cv2.warpPerspective(canvas, matrix, dsize=(canvas.shape[1], canvas.shape[0]))

    original = cv2.addWeighted(original, 0.5, trans, alpha, 0)
    return original

def drawRect(img, points, colour=(255, 0, 0), thickness=2):
    ordered = clockwise(points)
    for i in range(4):
        cv2.line(img, tuple(ordered[i]), tuple(ordered[(i + 1) % 4]), colour, thickness)

# orig = cv2.imread("toucan.jpg")
# over = cv2.imread("parrots.jpg")
# combined = overlay(orig, over)
# show(combined)
# 
# p = np.array([
#     [100, 100],
#     [500, 400],
#     [300, 100],
#     [100, 500]
# ])
# drawRect(combined, p)
# show(combined)

for i in range(1, sampleCount + 1):
    colourImg = cv2.imread("colour.png")
    img = cv2.imread("body_index_{}.png".format(i))
    combined = overlay(colourImg, img)
    data = json.loads(open("body_index_{}.json".format(i), "r").read())
    for box in data["bounds"]:
        points = np.array(box)
        drawRect(combined, points)
    coords = np.array(data["canvas"])
    drawRect(combined, coords, (0, 0, 255), 3)