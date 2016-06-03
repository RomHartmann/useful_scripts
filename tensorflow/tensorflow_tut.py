import numpy as np
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

#-----get dataset
oMnistDataset = input_data.read_data_sets("MNIST_data/", one_hot=True)

#-----draw tensorflow graph and initialize
#get dimensions of dataset
iVarLen = np.size(oMnistDataset.train.images[0]) #728
iSolLen = np.size(oMnistDataset.train.labels[0]) #10

#create variable placeholders which will contain training data later
tfaXTrain = tf.placeholder(tf.float32, [None, iVarLen])  #is the size of the input variable data
tfaYTrain = tf.placeholder(tf.float32, [None, iSolLen])  #is the size of the desired solution data

#create variables for which we shall solve in training
tfmWeight = tf.Variable(tf.zeros([iVarLen, iSolLen]))    #consider matrix multiplication for its dimenstions
tfaBias = tf.Variable(tf.zeros([iSolLen]))   #must be the same size as solution space

#define the model we use
#   our model is akin to linear regression
#   our weighting matrix mWeight defines all of solution space
#   bias vector adjusts (mWeight*aXData)
tfaYPredict = tf.nn.softmax(tf.matmul(tfaXTrain, tfmWeight) + tfaBias)

#define misfit function for which we shall minimize:  cross entropy
tfrMisfit = tf.reduce_mean(
    -tf.reduce_sum(
        tfaYTrain * tf.log(tfaYPredict), reduction_indices=[1]
    )
)

# #define misfit function: least squares
# tfrMisfit = tf.reduce_mean(
#     tf.reduce_sum(
#         tf.square(tfaYPredict - tfaYTrain)
#     )
# )


#define training algorithm:  How the model reacts to each iteration
tfTrainStep = tf.train.GradientDescentOptimizer(0.5).minimize(tfrMisfit)

#draw graph
tfInit = tf.initialize_all_variables()

#----- create session and run training
oSess = tf.Session()
oSess.run(tfInit)



#train dataset using random data from oMnistDataset
for i in range(1000):
    aaXDataBatch, aaYDataBatch = oMnistDataset.train.next_batch(100)
    oSess.run(tfTrainStep, feed_dict={tfaXTrain:aaXDataBatch, tfaYTrain:aaYDataBatch} )


#-------------- work with results

tfabCorrectPrediction = tf.equal(tf.argmax(tfaYPredict, 1), tf.argmax(tfaYTrain, 1))
tfrAccuracy = tf.reduce_mean(tf.cast(tfabCorrectPrediction, tf.float32))
print('accuracy', oSess.run(tfrAccuracy, feed_dict={tfaXTrain: oMnistDataset.test.images, tfaYTrain: oMnistDataset.test.labels}))


llRand = np.random.normal(loc=0.0, scale=1.0, size=(1, iVarLen))
llIm, llRes = oMnistDataset.test.next_batch(1)


tfiPrediction = tf.argmax(tfaYPredict, 1)
liPredict = tfiPrediction.eval(feed_dict={tfaXTrain: llIm}, session=oSess)
llPredict = tfaYPredict.eval(feed_dict={tfaXTrain: llIm}, session=oSess)
liPredictRand = tfiPrediction.eval(feed_dict={tfaXTrain: llRand}, session=oSess)
llPredictRand = tfaYPredict.eval(feed_dict={tfaXTrain: llRand}, session=oSess)


print 'eval method', liPredict, llPredict, llRes
print 'rand eval method', liPredictRand, llPredictRand


from matplotlib import pyplot as plt
aaIm = np.reshape(llIm[0], [28,28])
aaRand = np.reshape(llRand[0], [28,28])

oFig = plt.figure()
oFig.add_subplot(121)
plt.imshow(aaIm)
oFig.add_subplot(122)
plt.imshow(aaRand)
plt.show()



oSess.close()











