import numpy as np
import pandas as pd
from keras.layers import Input, Dense, Bidirectional, GRU, Embedding, Dropout
from keras.layers import concatenate, SpatialDropout1D, GlobalAveragePooling1D, GlobalMaxPooling1D
from keras.models import Model
from sklearn.model_selection import train_test_split
from utils import *


maxlen = 150
max_features = 2500


gop = pd.read_csv('Data/gop.csv')
data = gop[['text','sentiment']]

# Balance Negative - Positive tweets
data[data['sentiment'] == 'Negative'] = data[data['sentiment'] == 'Negative'][:2236]
data[data['sentiment'] == 'Neutral'] = data[data['sentiment'] == 'Neutral'][:2236]
data = data.dropna()

data['sentiment'].value_counts() #Negative: 8493; Neutral: 3142; Positive: 2236
X, Y = format_data(data, max_features, maxlen)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.25, random_state = 42)

# Input shape
inp = Input(shape=(maxlen,))

# Embedding and GRU
x = Embedding(max_features, 150)(inp)
x = SpatialDropout1D(0.25)(x)
x = Bidirectional(GRU(75, return_sequences=True, recurrent_dropout=0.2))(x)
x = Bidirectional(GRU(50, return_sequences=True, recurrent_dropout=0.1))(x)

# Pooling
avg_pool = GlobalAveragePooling1D()(x)
max_pool = GlobalMaxPooling1D()(x)
conc = concatenate([avg_pool, max_pool])

# Output layer
output = Dense(1, activation='sigmoid')(conc)

model = Model(inputs=inp, outputs=output)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


# model.load_weights('Weights/gru_double1.h5')
model.fit(X_train, Y_train, epochs=3, batch_size=32, verbose=1)
model.save_weights('Weights/gru_double1.h5')

results = model.predict(X_test, batch_size=1, verbose=1)
run_test(results, Y_test)
