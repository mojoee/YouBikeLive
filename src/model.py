import tensorflow as tf
from tensorflow.keras import layers

class PositionalEmbedding(layers.Layer):
    def __init__(self, maxlen, d_model, **kwargs):
        super().__init__(**kwargs)
        self.maxlen = maxlen
        self.d_model = d_model
        self.pos_emb = layers.Embedding(input_dim=maxlen, output_dim=d_model)

    def call(self, inputs, training=None, mask=None):
        positions = tf.range(start=0, limit=tf.shape(inputs)[1], delta=1)
        positions = self.pos_emb(positions)
        return inputs + positions

    def get_config(self):
        config = super().get_config()
        config.update({
            "maxlen": self.maxlen,
            "d_model": self.d_model
        })
        return config
