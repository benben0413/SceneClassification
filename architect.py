import os, datetime
import numpy as np
import tensorflow as tf
import CNNModels

class alexnet_model:
    def __init__(self, x, y, seg_labels, obj_class, keep_dropout, train_phase):
        self.logits_class=CNNModels.alexnet(x, keep_dropout, train_phase)
        self.loss_class =loss_class(y,self.logits_class)
        self.loss_seg =  tf.reduce_mean(self.logits_class)

class vgg_model:
    def __init__(self, x, y, seg_labels, obj_class, keep_dropout, train_phase):
        self.logits_class = CNNModels.VGG(x, keep_dropout, train_phase, num_classes=100)
        self.loss_class =loss_class(y,self.logits_class)
        self.loss_seg =  tf.reduce_mean(self.logits_class)

class vgg_bn_model:
    def __init__(self, x, y, seg_labels, obj_class, keep_dropout, train_phase):
        self.logits_class=CNNModels.VGG(x, keep_dropout, train_phase, num_classes=100, batch_norm=True)
        self.loss_class =loss_class(y,self.logits_class)
        self.loss_seg = tf.reduce_mean(self.logits_class)
        
class vgg_objnet:
    def __init__(self, x, y, seg_labels, obj_class, keep_dropout, train_phase):
        self.logits_class,self.logits_seg=CNNModels.VGG(x, keep_dropout, train_phase,num_classes=100, batch_norm=True, seg=True, seg_mode=2, num_classes_seg=176)
        self.loss_class =loss_class(y,self.logits_class)
        self.loss_seg = loss_seg(obj_class,self.logits_seg)

class vgg_segnet:
    def __init__(self, x, y, seg_labels, keep_dropout, train_phase):
        self.prob_class, self.logits_seg = CNNModels.VGG_SegNet(x, keep_dropout, train_phase, debug=True)
        self.loss_seg = loss_seg(seg_labels, self.logits_seg)
        one_hot_y = tf.one_hot(y, 100)
        self.loss_class = -tf.reduce_mean(tf.reduce_sum(one_hot_y * tf.log(self.prob_class + 1e-8), axis=-1))
        self.logits_class = self.prob_class

def loss_class(y,logits):
    return tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y, logits=logits))

def loss_seg(y,logits):
    sumy=tf.reduce_mean(y)
    return tf.cond(tf.equal(sumy, 0),lambda: sumy,lambda: loss_seg_norm(y,logits))

def loss_seg_norm(y, logits):     
    if len(y.get_shape().as_list())==4:
        size=(1,1,1,176)
    if len(y.get_shape().as_list())==2:
        size=(1,176)
    newy = y/tf.tile(tf.expand_dims(tf.reduce_sum(y,axis=-1), axis=-1), size)
    return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=newy, logits=logits))

