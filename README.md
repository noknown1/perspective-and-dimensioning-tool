# perspective-and-dimensioning-tool
Get dimensions and top down schematic like images from photos of objects.

# What is this?

This tool is used generate flat top-down view images from an image of a 3D object. First, the diffrent faces of the 3D object are selected
by hand from the source image. Each of those faces will then be converted to a 'flat' top down view. Using the edges feature, a composite
image that stiches all flattened faces into one single image.

# How to use

1) **Load Image**: Load an image via File -> Load Image from the menu. 

2) **Add Faces**: To add a face over your image, press the 'Add Face' button then click four points on the image which define the desired face. You can
repeat this step to add additional faces over your image. To delete or redraw a face press the 'Select Face' button, click on the letter
of the face you wish to delete/redraw, then press the 'Delete Face' or 'Redraw Button'.

3) **Add Edges**: Edges are used for the composite image. They are not needed if you do not wish to generate a composite image. Edges define how a composite
image will be stitched together. Add edges by pressing the 'Add Edge' button then clicking on two already existing points shared by at least two faces.
This will conjoin these faces via the selected edge when the composite image is generated.

4) **Export Images**: Once all the desired faces have been selected, press the 'Process All' button to compute the flattened images. Once this is done, pressing
the 'Export Images' button will prompt you to save each flattened image individually. The 'Export Composite' button can be clicked to 
save a single composite image consisting of all the flattened faces stitched together.
