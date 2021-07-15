import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import sort
from pdf2image import convert_from_path

security_pages = 34
security_file = 'PDFs/security.pdf' 

mi_pages = 36
mi_file = 'PDFs/mi.pdf'

num_pages = security_pages
file_name = security_file


def pdf_to_pages():
    pages = convert_from_path(file_name)

    i = 0
    for page in pages:
        print("pdf_to_pages ",i)
        i += 1
        page.save('images/img'+str(i)+'.jpg', 'JPEG')


def binary_images():
    threshold = 130
    for i in range(1,num_pages + 1):
        print("binary ", i)
        gray_image = cv.imread('images/img'+str(i)+'.jpg', cv.IMREAD_GRAYSCALE)

        _ , im_bw = cv.threshold(gray_image, threshold, 255, cv.THRESH_BINARY)

        cv.imwrite('binary/bin'+str(i)+'.jpg', im_bw)


def remove_tables(gray):
    gray2 = 255 - gray
    ret, bin_img = cv.threshold(gray2,40,255,cv.THRESH_BINARY)
    major = cv.__version__.split('.')[0]
    if major == '3': img2, contours, hierarchy= cv.findContours(bin_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    else: contours, hierarchy= cv.findContours(bin_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    lines = []
    width_threshold = 0.1 * gray.shape[1]
    for contour in contours:    
        [x,y, w, h] = cv.boundingRect(contour)
        if(w > width_threshold):
            lines.append(y)
        
    lines.sort()
    table_threshold = 0.2 * gray.shape[0]
    h_line_width = 2
    last_y = 0
    for y in lines:
        # remove_lines
        print(y)
        gray[max(y-h_line_width, 0):min(y+h_line_width, gray.shape[0]),:] = 255
        # remove tables
        if(y - last_y < table_threshold):
            gray[last_y:min(y+h_line_width, gray.shape[0]),:] = 255
        last_y = y
    return gray

#def betweenLines(gray):
#    # remove borders
#    y_min, y_max = detect_border_lines(gray)
#    threshold = gray.shape[0] * 0.1
#    no_lines_image = np.copy(gray)
#    if (no_lines_image.shape[0] - y_max < threshold):
#        no_lines_image = no_lines_image[0:y_max,:]
#    if (y_min < threshold):
#        no_lines_image = no_lines_image[y_min:no_lines_image.shape[0],:]
#    
#    # remove tables
#    y_min, y_max = detect_border_lines(no_lines_image)
#    if y_max > 0 and y_min < no_lines_image.shape[0]:
#        no_lines_image[y_min:y_max+1,:] = 255
#    
#    return no_lines_image


def test_tables():
    for i in range(1,num_pages + 1):
        print("tables ", i)
        gray_image = cv.imread('binary/bin'+str(i)+'.jpg', cv.IMREAD_GRAYSCALE)

        #border_thre = int(gray_image.shape[0] / 14)
        gray = remove_tables(gray_image)
        #gray = gray_image[border_thre:gray_image.shape[0] - border_thre,:]
        cv.imwrite('tables/tb'+str(i)+'.jpg', gray)
    #scale_percent = 40 # percent of original size
    #width = int(gray.shape[1] * scale_percent / 100)
    #height = int(gray.shape[0] * scale_percent / 100)
    #dim = (width, height)
    #
    ## resize image
    #resized = cv.resize(gray, dim, interpolation = cv.INTER_AREA)
#
    #cv.imshow("image", resized)
    #cv.waitKey(0)

def imageHist(img):
    out = np.ones(img.shape)*255
    out = out.astype(np.uint8)
    img = 255 - img
    
    mean = np.sum(img)/img.shape[0]
    std = 0
    #print(mean,img.shape)
    # for y in img.shape[0]:
    #     std += (np.sum(img[y,:])-mean)**2
    
    # np.
    vec = []
    for y in range(img.shape[0]):
        vec.append(np.sum(img[y,:]))
    
    mn = 0.6 * np.max(vec)
    # after_offset = 5
    # before_offset = 25
    # print ("MN: ",mn)
    # for y in range(len(vec)):
    #     if vec[y] >= mn:
    #         out[max(y-before_offset,0):min(y+after_offset+1,img.shape[0]),:] = 255-np.copy(img[max(y-before_offset,0):min(y+after_offset+1,img.shape[0]),:])
    
    rng = 40
    lst = 0

    for y in range(len(vec)):
        if vec[y] >= mn:
            lst = y
        
        if np.abs(y-lst) <= rng:
            out[y] = 255-np.copy(img[y])

    lst = img.shape[0]-1
    for y in range(len(vec)-1, -1, -1):
        if vec[y] >= mn:
            lst = y
        
        if np.abs(y-lst) <= rng:
            out[y] = 255-np.copy(img[y])

    # plt.hist(vec, bins=255)
    #plt.plot(vec)
    #plt.show()    
    
    return out


    # m = np.sum(vec)/img.shape[1]
    # print(m)
    
def test_histogram():
    for i in range(1,num_pages + 1):
        print("histogram ", i)
        gray_image = cv.imread('tables/tb'+str(i)+'.jpg', cv.IMREAD_GRAYSCALE)

        gray = imageHist(gray_image)
        cv.imwrite('histogram/hist'+str(i)+'.jpg',gray)

pdf_to_pages()
binary_images()
test_tables()
test_histogram()

#gray_image = cv.imread('binary/bin'+str(2)+'.jpg', cv.IMREAD_GRAYSCALE)
#
#gray = remove_tables(gray_image)
#
#cv.imwrite('borders/bor'+str(2)+'.jpg', gray)
