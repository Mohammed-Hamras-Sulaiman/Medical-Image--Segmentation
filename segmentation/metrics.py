import tensorflow as tf

def jaccard_index(y_true, y_pred, smooth=100):
    """
    Calculates the Jaccard index (Intersection over Union).
    :param y_true: Ground truth tensor.
    :param y_pred: Predicted tensor.
    :param smooth: Smoothing factor to avoid division by zero.
    :return: Jaccard index.
    """
    y_true_f = tf.reshape(tf.cast(y_true, tf.float32), [-1])
    y_pred_f = tf.reshape(tf.cast(y_pred, tf.float32), [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    total = tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) - intersection
    return (intersection + smooth) / (total + smooth)


def dice_coefficient(y_true, y_pred, smooth=1):
    """
    Calculates the Dice Coefficient for similarity between two sets.
    :param y_true: Ground truth tensor.
    :param y_pred: Predicted tensor.
    :param smooth: Smoothing factor to avoid division by zero.
    :return: Dice Coefficient.
    """
    y_true_f = tf.reshape(tf.cast(y_true, tf.float32), [-1])
    y_pred_f = tf.reshape(tf.cast(y_pred, tf.float32), [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)
