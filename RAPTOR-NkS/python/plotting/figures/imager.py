import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Load the image
#img = mpimg.imread("img_3201.png")  # Change "image.png" to your file

# Display the image
#plt.imshow(img)
#plt.axis("off")  # Hide the axes
#plt.show()
import cv2
img = cv2.imread("img_3201.png")
cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
