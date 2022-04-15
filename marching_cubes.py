import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage import measure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def open_image(image_path):
    """Open image"""
    image = cv2.imread(image_path)
    return image

# resize image to half size
def resize_image(image):
    """Resize image"""
    image = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
    return image

# blur the image
def blur_image(img):
    """Blur the image"""
    img_blur = cv2.GaussianBlur(img, (3, 3), 0)
    return img_blur

# gray scale image
def gray_scale_image(img):
    """Grayscale the image"""
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img_gray

def get_canny(image_gray):
    """Get canny edges"""
    edges = cv2.Canny(image_gray, 50, 255)
    return edges

def create_binary_image(img_gray):
    """Create binary image"""
    # convert to binary
    _, img_binary = cv2.threshold(img_gray, 80, 255, cv2.THRESH_BINARY)
    return img_binary



def make_volume(image_binary, image_contours):
    """Make volume"""
    # make volume of size image width x height x 25
    volume = np.zeros((image_binary.shape[1], image_binary.shape[0], 25))
    depth = 25
    for i in range(depth):
        # add 25 copies of image
        if i == 0:
            volume[:, :, i] = image_binary.transpose()
        elif i == depth - 1:
            volume[:, :, i] = image_binary.transpose()
        else:
            volume[:, :, i] = image_contours.transpose()

    return volume


def marching_cubes(data_volume):
    """Marching cubes"""
    verts, faces, normals, values = measure.marching_cubes(data_volume, 0)

    return verts, faces, normals, values

def show(verts, faces):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Fancy indexing: `verts[faces]` to generate a collection of triangles
    mesh = Poly3DCollection(verts[faces])
    mesh.set_edgecolor('k')
    ax.add_collection3d(mesh)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_zlim(0, 30)


    ax.set_xlabel("x-axis: a = 6 per ellipsoid")
    ax.set_ylabel("y-axis: b = 10")
    ax.set_zlabel("z-axis: c = 16")


    plt.tight_layout()
    plt.show()

def run():
    """Main function"""
    # open image
    image = open_image("images/logo.png")
    # resize image
    image = resize_image(image)
    # rotate image 90 degrees
    image = np.rot90(image)
    # flip image horizontally
    image = cv2.flip(image, 0)
    # blur image
    image_blur = blur_image(image)
    # gray scale image
    image_gray = gray_scale_image(image_blur)
    # create binary image
    image_binary = create_binary_image(image_gray)
    # find contours
    image_contours = get_canny(image_gray)
    # create rectangles

    volume = make_volume(image_binary, image_contours)
    # marching cubes
    verts, faces, normals, values = marching_cubes(volume)

    return verts, faces, normals
