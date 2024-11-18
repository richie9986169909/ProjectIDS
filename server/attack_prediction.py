import pandas as pd
import numpy as np
import pickle
import yagmail
from tensorflow.keras.models import load_model
from flask import Flask, request, render_template

app = Flask(__name__)

# Load the model and scaler
model = load_model(filepath="models/ArtificialNeuralNetwork_model.h5", compile=False)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

with open(file="models/Scaler.pkl", mode="rb") as file:
    scaler = pickle.load(file=file)

with open(file='Important_Columns.txt', mode='r') as file:
    imp_cols = file.read().split('\n')[:-1]

class_labels = ['BENIGN', 'DDoS', 'PortScan']

def intrusionPrediction(file_path):
    print("file_path_Prediction : ", file_path)

    try:
        # Read input file and preprocess
        input_ = pd.read_excel(file_path)
        # ip_address = input_.pop("IP_Add")
        input_.columns = [col.strip() for col in input_.columns]
        input_ = input_[imp_cols]
        inp_cols = input_.columns
        scaled_input_ = scaler.transform(input_)
        input_df = pd.DataFrame(data=scaled_input_, columns=inp_cols)


        model_pred = model.predict(input_df)
        print("model_pred : ", model_pred)
        model_pred_class = np.argmax(model_pred[0])
        model_pred_label = class_labels[model_pred_class]

        print("model_pred_label : ", model_pred_label)

        # Calculate the probability score for the predicted class
        probability_score = model_pred[0][model_pred_class]
        print("probability_score : ", probability_score)
        

        return model_pred_label, probability_score

    except Exception as e:
        print(f"Error in intrusionPrediction: {e}")
        return "Error during prediction"