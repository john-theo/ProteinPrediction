import numpy as np
import tensorflow as tf
import os, shutil
# from src.simply_ann.mnistdata import read_data_sets
from src.simple_ann.dataset import read_data_sets

feature_length = 284
learning_rate = 0.006
train_iteration = 100
batch_size = 100
display_step = 10
time_stamp = '20180612_211120'  # 20180612_211120
data_dir = '../../data/ANN_data/'+time_stamp+'/'
log_dir = data_dir + 'logs'
if os.path.exists(log_dir):
    shutil.rmtree(log_dir)

# mnist = read_data_sets("data", one_hot=True, reshape=False)
mnist = read_data_sets(data_dir)

x = tf.placeholder('float', shape=[None, feature_length])
y = tf.placeholder('float', shape=[None, 10])

# five layers and their number of neurons (tha last layer has 10 softmax neurons)
L = 160
M = 90
N = 50
O = 20

W1 = tf.Variable(tf.truncated_normal([feature_length, L], stddev=0.1))  # 784 = 28 * 28
B1 = tf.Variable(tf.zeros([L]))
W2 = tf.Variable(tf.truncated_normal([L, M], stddev=0.1))
B2 = tf.Variable(tf.zeros([M]))
W3 = tf.Variable(tf.truncated_normal([M, N], stddev=0.1))
B3 = tf.Variable(tf.zeros([N]))
W4 = tf.Variable(tf.truncated_normal([N, O], stddev=0.1))
B4 = tf.Variable(tf.zeros([O]))
W5 = tf.Variable(tf.truncated_normal([O, 10], stddev=0.1))
B5 = tf.Variable(tf.zeros([10]))


# The model
XX = tf.reshape(x, [-1, feature_length])
Y1 = tf.nn.sigmoid(tf.matmul(XX, W1) + B1)
Y2 = tf.nn.sigmoid(tf.matmul(Y1, W2) + B2)
Y3 = tf.nn.sigmoid(tf.matmul(Y2, W3) + B3)
Y4 = tf.nn.sigmoid(tf.matmul(Y3, W4) + B4)
Ylogits = tf.matmul(Y4, W5) + B5

with tf.name_scope("Wx_b") as scope:
    model = tf.nn.softmax(Ylogits)

with tf.name_scope("cost_function"):
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=Ylogits, labels=y)
    cost_function = tf.reduce_mean(cross_entropy) * 100
    # cost_function = -tf.reduce_sum(y * tf.log(tf.clip_by_value(model, 1e-20, 1.0)))
    tf.summary.scalar("cost_function", cost_function)

with tf.name_scope("train"):
    optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost_function)

init = tf.initialize_all_variables()
merge_summary_op = tf.summary.merge_all()

predictions = tf.equal(tf.argmax(model, 1), tf.argmax(y, 1))
accuracy = tf.reduce_mean(tf.cast(predictions, "float"))

with tf.Session() as sess:
    sess.run(init)
    summary_writer = tf.summary.FileWriter(log_dir, sess.graph)
    for iteration in range(train_iteration):
        avg_cost = 0.
        accu = 0.
        total_batch = int(mnist.train.num_examples / batch_size)
        for i in range(total_batch):
            batch_xs, batch_ys = mnist.train.next_batch(batch_size)
            batch_xs = np.reshape(batch_xs, (-1, feature_length))
            sess.run(optimizer, feed_dict={x: batch_xs, y: batch_ys})
            avg_cost += sess.run(cost_function, feed_dict={x: batch_xs, y: batch_ys}) / total_batch
            summary_str = sess.run(merge_summary_op, feed_dict={x: batch_xs, y: batch_ys})
            summary_writer.add_summary(summary_str, iteration * total_batch + i)
            accu = sess.run(accuracy, feed_dict={x: batch_xs, y: batch_ys})
        if iteration % display_step == 0:
            print('Iteration: %04d, loss = %.3f, accuracy = %.1f%%' % (iteration + 1, avg_cost, accu*100))
    print('Complete successfully!')

    test_images = np.reshape(mnist.test.features, (-1, feature_length))
    test_labels = mnist.test.labels
    accu = accuracy.eval({x: test_images, y: test_labels})
    print('Accuracy: %.2f%%' % (accu * 100))
