import cv2 as cv
import numpy as np
import imageio

square_half_len = 20
puncta_size_threshold = 100
puncta_move_threshold = 10
puncta_radius = 10
image_size = 200
red = (255, 0, 0)
blue = (0, 0, 255)

# laser target coordinate, record the start position during the experiment!
start_x, start_y = 77, 31


def draw_area(image, x, y):
    cv.circle(image, (x, y), puncta_radius, red, 1, lineType=cv.LINE_AA)
    cv.rectangle(
        image,
        (x - square_half_len, y - square_half_len),
        (x + square_half_len, y + square_half_len),
        blue, 2
    )


def get_mean_intensity(image, x, y):
    mask_img = np.zeros((image_size, image_size), np.uint8)
    mask = cv.circle(mask_img, (x, y), puncta_radius, 255, -1, lineType=cv.LINE_AA)
    image_masked = cv.bitwise_and(image, image, mask=mask)
    count = np.nonzero(image_masked)[0].size

    cv.imshow('mask', image_masked)
    cv.waitKey(100)
    return np.sum(image_masked) / count


gif = imageio.mimread('frap.gif')
gif_processed = list()
mean_intensity = list()
cv.namedWindow('gif', cv.WINDOW_NORMAL)
cv.namedWindow('mask', cv.WINDOW_NORMAL)
cur_x, cur_y = start_x, start_y

for j, img in enumerate(gif):
    # find contour
    imgray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    ret, thresh = cv.threshold(imgray, 20, 255, 0)
    contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    nearest_dist = image_size
    nearest_x, nearest_y = -1, -1
    nearest_i = -1

    # find nearest contour to the previous frame
    for i in range(len(contours)):
        M = cv.moments(contours[i])
        if M['m00'] > puncta_size_threshold:
            cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
            dist = np.sqrt((cx - cur_x) ** 2 + (cy - cur_y) ** 2)
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_x, nearest_y = cx, cy
                nearest_i = i

    # calculate ROI size from the first frame
    if j == 0:
        area = cv.contourArea(contours[nearest_i])
        puncta_radius = int(np.sqrt(area / np.pi))

    # update current center of the puncta, label it
    if nearest_dist < puncta_move_threshold:
        draw_area(img, nearest_x, nearest_y)
        mean_intensity.append(get_mean_intensity(imgray, nearest_x, nearest_y))
        cur_x, cur_y = nearest_x, nearest_y

    # valid contour not found, center of the puncta unchanged
    else:
        draw_area(img, cur_x, cur_y)
        mean_intensity.append(get_mean_intensity(imgray, cur_x, cur_y))

    # show current frame
    img_BGR = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    cv.imshow('gif', img_BGR)
    gif_processed.append(img)
    if cv.waitKey(100) & 0xFF == 27:
        break

# save and exit
imageio.mimsave('frap_track.gif', gif_processed)
result = np.array(mean_intensity).T
np.savetxt('frap.txt', result, fmt='%3.2f')
cv.destroyAllWindows()
