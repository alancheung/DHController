import numpy as np
import cv2
import os
from os import path
from numpy.linalg import norm

trainingDirPath = '/home/pi/Desktop/WandTraining/Shapes/'
trainingShapeDirPath = 'circle/'

class StatModel(object):
    def load(self, fn):
        self.model.load(fn)  # Known bug: https://github.com/opencv/opencv/issues/4969
    def save(self, fn):
        self.model.save(fn)

class KNearest(StatModel):
    def __init__(self, k = 3):
        self.k = k
        self.model = cv2.ml.KNearest_create()

    def train(self, samples, responses):
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    def predict(self, samples):
        _retval, results, _neigh_resp, _dists = self.model.findNearest(samples, self.k)
        return results.ravel()

class SVM(StatModel):
    def __init__(self, C = 1, gamma = 0.5):
        self.model = cv2.ml.SVM_create()
        self.model.setGamma(gamma)
        self.model.setC(C)
        self.model.setKernel(cv2.ml.SVM_RBF)
        self.model.setType(cv2.ml.SVM_C_SVC)

    def train(self, samples, responses):
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    def predict(self, samples):
        return self.model.predict(samples)[1].ravel()

def createTrainingImgName(shape, count):
    return shape + '-' + str(count) + '.png'

# Resize arg(image) with height and width = arg((height,width)) to scale = arg(scale)
def resizeImage(image, (height, width), scale):
    h = height * scale / 100
    w = width * scale / 100
    dim = (w, h)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def deskew(image, (height, width)):
    m = cv2.moments(image)
    if abs(m['mu02']) < 1e-2:
        return image
    skew = m['mu11']/m['mu02']
    # TODO fix height in M. It assumes square images.
    M = np.float32([[1, skew, -0.5*(height)*skew], [0, 1, 0]])
    image = cv2.warpAffine(image, M, (height, width), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
    return image

def preprocess_hog(images):
    samples = []
    for img in images:
        gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
        mag, ang = cv2.cartToPolar(gx, gy)
        bin_n = 16
        bin = np.int32(bin_n*ang/(2*np.pi))
        bin_cells = bin[:10,:10], bin[10:,:10], bin[:10,10:], bin[10:,10:]
        mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
        hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
        hist = np.hstack(hists)

        # transform to Hellinger kernel
        eps = 1e-7
        hist /= hist.sum() + eps
        hist = np.sqrt(hist)
        hist /= norm(hist) + eps

        samples.append(hist)
    return np.float32(samples)

# read all images and process data
shape1Count = 0
lineCount = 0

readImages = []
trainingImageData = []
for i in range(1, 500):
    fullPath = trainingDirPath + trainingShapeDirPath + createTrainingImgName('shape1', i)
    if path.exists(fullPath):
        shape1Count += 1
        image = cv2.imread(fullPath, cv2.IMREAD_GRAYSCALE)

        

        process = preprocess_hog(image)
        trainingImageData.append(process)

# read all images and process data
for i in range(1, 500):
    fullPath = trainingDirPath + 'HorizontalLine/' + createTrainingImgName('shape2', i)
    if path.exists(fullPath):
        lineCount += 1
        image = cv2.imread(fullPath, cv2.IMREAD_GRAYSCALE)

        

        process = preprocess_hog(image)
        trainingImageData.append(process)

processImages = preprocess_hog(trainingImageData)
print 'shape1 count ' + str(shape1Count)
print 'line ' + str(lineCount)
print processImages.shape

# TODO figure out how to make this dynamic
# for now hardcode
labels = np.mat([1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
print labels

svm = SVM(C = 2.67, gamma = 5.383)
svm.train(processImages, labels)


print 'Test Image 20'
fullPath = trainingDirPath + trainingShapeDirPath + createTrainingImgName('shape1', 20)
testImage = cv2.imread(fullPath, cv2.IMREAD_GRAYSCALE)
testImageProcess = preprocess_hog(testImage)
resp = svm.predict(testImageProcess)
print resp
confusion = np.zeros((10, 10), np.int32)
for i, j in zip(labels, resp):
    confusion[i, int(j)] += 1
print('confusion matrix:')
print(confusion)
print()

print 'Test Image Fail'
fullPath = trainingDirPath + 'HorizontalLine/shape2-108.png'
testImage = cv2.imread(fullPath, cv2.IMREAD_GRAYSCALE)
testImageProcess = preprocess_hog(testImage)
resp = svm.predict(testImageProcess)
print resp
confusion = np.zeros((10, 10), np.int32)
for i, j in zip(labels, resp):
    confusion[i, int(j)] += 1
print('confusion matrix:')
print(confusion)
print()