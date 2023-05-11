import os

import tensorflow.lite as tflite

from keras import layers, models, Model # , optimizers
from keras.preprocessing.image import ImageDataGenerator

class Model():

    # argmax, max functions handler to avoid installing numpy
    def maxes(myArray):
    
        myMax = 0 # initialise
        counter = 0
        
        for i in myArray:
            if i >  myMax:
                argmax=counter
                myMax=i
            counter+=1    
        return(argmax,myMax)
    
    
    
    def runInference(self,dlImageArray):

        test_datagen =  ImageDataGenerator(
            rescale=1./255
        )

        img_height, img_width = 224,224

        category_names = ["Bikes","Forbidden_for_traffic", "Intersection", "No_entry", "Pedestrians", "Right_of_way", "Slippery_road", "Speed_60", "Stop", "Yield", "Festive"]

        # image_array = np.expand_dims(image_array, axis=0) # using below instead to avoid install of numpy
        # print(image_array.shape)
        # shape should be (1, 224, 224, 3)
        image_array = dlImageArray.reshape(1, dlImageArray.shape[0],dlImageArray.shape[1],dlImageArray.shape[2]) 

        #normalize image - important otherwise all classifications will have probability 1
        image_array = image_array / 255.0
     
        # .tflite model 
        interpreter = tflite.Interpreter(model_path='./python/tfliteConv-model.tflite') # looks for model in same folder. NB as we are setting up an instance of the MOdel class, the actual invocation is at the same level as main python script (main.py)
        interpreter.allocate_tensors()

        # Get a list of details from the model
        input_index = interpreter.get_input_details()[0]['index'] 
        output_index = interpreter.get_output_details()[0]['index']

        # Turn the image into a Numpy array with float32 data type
        image_array = image_array.astype('float32')

        # set the value of the input tensor
        interpreter.set_tensor(input_index, image_array)
        interpreter.invoke()

        # get the value of the output tensor
        predProb=interpreter.get_tensor(output_index)[0]
      
        predicted_label, predicted_prob = Model.maxes(predProb)

        print(predProb)
        print(predicted_label) # formerly print(pred)
        print_msg = str(category_names[predicted_label-1]) + " (probability: " + str(predicted_prob) + ")" # NEW

        #return category_names[pred] #, pred_prob, msg
        return print_msg

        # for testing function is called - comment out rest of function
"""         myString = "hello"
        return myString """


    
