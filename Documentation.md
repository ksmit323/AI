Traffic
Video Demo: https://youtu.be/e0CsCKRjoew
Description:
Experimentation Process

First, for the input layer I added the "rescaling" feature as it was recommended by TensorFlow's documentation for standardizing data. Once I added the convolutional and pooling layers, I tried adjusting the hidden layers and dropout rate. It became very apparent that these two layers influenced the accuracy the most. Removing the dropout rate dramatically increased accuracy. However, as one can imagine, this would likely not generalize well and would be a case of overfitting. So, in order to include a significant dropout rate, I increased the size of the hidden layer. Between moderating the hidden layer size and the dropout rate, the overall accuracy began to balance pretty well. However, once it stabilized between these two factors, nothing much more seemed required to create better performance. Adding extra hidden layers definitely improved the accuracy but made me wonder about if overfitting was a concern. So then adding anothe dropout layer for the second hidden layer did not perform any better than just having one hidden and dropout layer. In the end one hidden layer with about 100 nodes seemed to strike a balance between accuracy and performance. Greatly increasing the size of this hidden layer only made the performance suffer terribly without gaining much.

The following are some other things I tried. However, none of these variables seem to have a large impact on overall accuracy or performance. First, I compounded another stack of convolutional and pooling layers. This was recommended in the TensorFlow documentation, siting it was a "common pattern" to "define a convolutional base". Although I don't feel my accuracy or loss was affected that much by adding these additional layers, I did instantly notice how much longer my program was taking to run. Next, I increased the pooling size from a 2x2 to a 3x3. My accuracy dropped and that's about the only change I noticed so I switched it back. Finally, I had a play around with adjusting the variables in the convolutional layer such as increasing the size, particularly in the second convolutional layer. Ultimately, I don't feel that much changed as far as managing performance and accuracy with any of these details. What seemed to work best was balancing the dropout rate with the hidden layers after flattening the convoluted pooling layers.

Notes:

Added "Rescaling" to the input layer as recommended by TF's documentation for standardizing data.
Taking out the dropout() or decreasing it greatly increases accuracy but surely ran the risk of overfitting
increasing hidden layer size greatly increased accuracy
Added another convo and pooling layer per the suggestions of TF's documentation on stacking Conv2D and MaxPooling2D to define a convolutional base. According to TF, this is a common pattern
Increasing the pooling size didn't seem to affect all that much except my accuracy went down slightly
Adding the extra convo/pooling layers seem to really slow things down
Didn't seem necessary to add more hidden layers as it didn't change much and accuracy was already pretty good with just one.
Around a 100 nodes in the hidden layer seemed to work best with a 0.4 Dropout. Any less and accuracy was too low. Any more and the performance suffered with not much accuracy to gain.
