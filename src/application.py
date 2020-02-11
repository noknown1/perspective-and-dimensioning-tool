import tkinter as tk
from tkinter import Menu
from tkinter.filedialog import askopenfilename, asksaveasfilename
import PIL.Image
import PIL.ImageTk
import numpy as np
import cv2

WHITE = "#EEEFEA"
BLACK = "#1c1c1c"
RED = "#ff1111"
ORANGE = "#ffa511"
YELLOW = "#ffff11"
GREEN = "#118111"
BLUE = "#1111ff"
INDIGO = "#4b0082"
VIOLET = "#ee82ee"
PRIMARY = "#DCDCDC"
DEFAULT = "#F0F0F0"
FONT_PRIMARY = "Fixedsys"
FONT_SECONDARY = "System"
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET]
NAMES = ["A", "B", "C", "D", "E", "F", "G"]

window_main = tk.Tk()
window_main.title("Change Counter")
window_main.geometry("+5+5")
window_main.resizable(False, False)
window_main.configure(bg=WHITE)

window_main.source_image_path = ""      # Path for source image
window_main.output_image_path = ""      # Path where output image will be saved
window_main.source_image = []           # Source input image
window_main.output_image = []           # Processed output image
window_main.preview_image = []          # Preview image for GUI display
window_main.select_points = False       # Flag: For point selection
window_main.ran = False                 # Flag: True if an image has been processed, otherwise false

width_offset = 0                        # Offset for image pixel collection from mouse (subtracts width of black bar)
image = []                              # The image to process
clicked_points = []                     # Actual image coordinates for selected points
circle_points = []                      # Coordinates for drawn circles on screen
canvas_elements = []
processed_images = []                   # List holds all processed images
all_click_points = []                   # List of all points clicked by a user (user to remember points and lock edges)
all_circle_points = []                  # List of all coordinates for drawn circles on screen
canvas_job_elements = []                # List of all canvas_elements list (each outline box for each job)

# Menu commands (used for GUI menu bar)
# load_image: Asks user to choose a source image to process
def load_image():
    # Get the image's path, then load it into the program
    window_main.source_image_path = askopenfilename(title="Load Image")
    window_main.source_image = cv2.cvtColor(cv2.imread(window_main.source_image_path), cv2.COLOR_BGR2RGB)

    # Update program status and print to console
    update_status("Loaded image " + window_main.source_image_path + ".")

    # Show the image in the preview box
    show_image(window_main.source_image)

# save_image: Allows user to save the output image to a path
def save_image(img):
    window_main.output_image_path = asksaveasfilename(title="Save Output Image")
    cv2.imwrite(window_main.output_image_path, img)
    update_status("Saved output image " + window_main.output_image_path)


def order_points(points):
    rect = np.zeros((4, 2), dtype="float32")
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]
    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmin(diff)]
    return rect


def process_image(points):
    #global clicked_points, circle_points, image

    # assign points
    tl = points[0]
    tr = points[1]
    br = points[2]
    bl = points[3]

    # compute width of new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute height of new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # create new image array using new dimensions
    new_image = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]],
        dtype="float32")

    # compute perspective transform matrix
    selected_points = np.array(points, dtype="float32")
    transformation_matrix = cv2.getPerspectiveTransform(selected_points, new_image)
    warped_image = cv2.warpPerspective(image, transformation_matrix, (maxWidth, maxHeight))

    # add the processed image to the list of complete images
    processed_images.append(warped_image)


    #for i in canvas_elements:
    #    window_main.image_canvas.delete(i)

    # clear image variables
    #clicked_points = []
    #circle_points = []

    return warped_image


# Program functions (used to process the image)
# run: will process image and display it in the preview box
def run():

    # Make sure there is a selected image to process
    if window_main.source_image_path == "":
        update_status("No image selected. Please load an image then press run.")
        return

    update_status("Processing...")
    for i in range(all_click_points.__len__()):
        process_image(all_click_points[i])
    update_status("Image processed.")
    window_main.ran = True
    #show_output()

# Helper functions (used for misc. GUI)
# show image: will show an image in the preview box
def show_image(img):
    global width_offset, image

    img_height, img_width = img.shape[:2]
    img = cv2.resize(img, (int(570 * (img_width / img_height)), 570), interpolation=cv2.INTER_AREA)
    image = img
    window_main.preview_image = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(img))
    window_main.image_canvas.create_image(300, 285, anchor=tk.CENTER, image=window_main.preview_image)
    width_offset = int((window_main.preview_image.width() - 600) / 2)

# update_status: updates program status label
def update_status(status_str):
    window_main.status_label.configure(text=status_str)
    print(status_str)

def select_points():
    if window_main.source_image_path == "":
        update_status("Load an image first.")
    window_main.image_canvas.bind("<Button-1>", select_point)

def select_point(event):
    global clicked_points, canvas_elements, circle_points

    # iterate color and name for selection with each new selection
    color = COLORS[all_click_points.__len__()]
    name = NAMES[all_click_points.__len__()]

    # mouse x,y are each point's coordinates on the actual source image
    mouse_x = event.x + width_offset
    mouse_y = event.y

    # circle x,y are each point's coordinates on the canvas image embedded in the gui
    circle_x = event.x
    circle_y = event.y

    # snap mouse clicks to already selected points if applicable (in a +/- 6 pixel range)
    for i in range(all_click_points.__len__()):
        for j in range(4):
            click_point = all_click_points[i][j]
            circle_point = all_circle_points[i][j]
            if (click_point[0] in range(mouse_x - 6, mouse_x + 6)) and (click_point[1] in range(mouse_y - 6, mouse_y + 6)):
                mouse_x = click_point[0]
                mouse_y = click_point[1]
                circle_x = circle_point[0]
                circle_y = circle_point[1]

    # if a user clicks in the left black box, set the mouse's x coordinate to 0 on the image
    if mouse_x < 0:
        mouse_x = 0
        circle_x = width_offset

    # if a user clicks in the right black box, set the mouse's x coordinate to the image's full width on the image
    if mouse_x > window_main.preview_image.width():
        mouse_x = window_main.preview_image.width()
        circle_x = width_offset + window_main.preview_image.width()

    # draw a circle on the canvas image where the user clicked
    canvas_elements.append(window_main.image_canvas.create_oval(circle_x - 6, circle_y - 6, circle_x + 6, circle_y + 6, fill=color))

    # save the point where the user clicked as a point on the image (mouse x,y) and on the canvas image (circle x,y)
    clicked_points.append([mouse_x, mouse_y])
    circle_points.append([circle_x, circle_y])

    # update status, print coordinates of clicked point
    update_status("Point Selected: " + "[" + str(mouse_x) + "," + str(mouse_y) + "]")

    # runs when all 4 points have been selected
    if clicked_points.__len__() == 4:

        # unbind left mouse click from the canvas
        window_main.image_canvas.unbind("<Button-1>")

        # append all the canvas elements for this job (all circles and lines drawn over the image)
        canvas_elements.append(window_main.image_canvas.create_line(circle_points[0][0], circle_points[0][1], circle_points[1][0], circle_points[1][1], width=3, dash=(4, 2), fill=color))
        canvas_elements.append(window_main.image_canvas.create_line(circle_points[1][0], circle_points[1][1], circle_points[2][0], circle_points[2][1], width=3, dash=(4, 2), fill=color))
        canvas_elements.append(window_main.image_canvas.create_line(circle_points[2][0], circle_points[2][1], circle_points[3][0], circle_points[3][1], width=3, dash=(4, 2), fill=color))
        canvas_elements.append(window_main.image_canvas.create_line(circle_points[3][0], circle_points[3][1], circle_points[0][0], circle_points[0][1], width=3, dash=(4, 2), fill=color))

        # average x and y to find center of the selection
        center_of_selection_x = int((circle_points[0][0] + circle_points[1][0] + circle_points[2][0] + circle_points[3][0]) / 4)
        center_of_selection_y = int((circle_points[0][1] + circle_points[1][1] + circle_points[2][1] + circle_points[3][1]) / 4)
        canvas_elements.append(window_main.image_canvas.create_text(center_of_selection_x, center_of_selection_y, text=name, font=(FONT_PRIMARY, 40), fill=color))

        # append this job's canvas elements and clicked points to the lists that hold all jobs elements and points
        canvas_job_elements.append(canvas_elements)
        all_circle_points.append(circle_points)
        all_click_points.append(clicked_points)

        # update status, display coordinates for all points selected
        update_status("Points selected: " + str(clicked_points))

        # reset the clicked points list, this current job is done
        clicked_points = []
        canvas_elements = []
        circle_points = []

def export_images():
    for i in processed_images:
        save_image(i)

# GUI CREATION #
# Create menu
menu = Menu(window_main)
file_items = Menu(menu, tearoff=0, bg=WHITE)
file_items.add_command(label="Load Image", command=load_image)
file_items.add_command(label="Save Output", command=save_image)
menu.add_cascade(label="File", menu=file_items)
adjust_items = Menu(menu, tearoff=0)
window_main.config(menu=menu)

# Create preview box for image
window_main.image_canvas = tk.Canvas(window_main, width=600, height=570, relief="flat")
window_main.image_canvas.create_rectangle(0, 0, 600, 570, fill=BLACK)

# Create buttons
window_main.button_show_source = tk.Button(window_main, text="Select Points", font=(FONT_PRIMARY, 12), command=select_points, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_show_output = tk.Button(window_main, text="Export Images", font=(FONT_PRIMARY, 12), command=export_images, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_run = tk.Button(window_main, text="Run", font=(FONT_PRIMARY, 12), command=run, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")

# Create status label
status_str = "Choose a source image (under 'File/Load Image'), and press run."
window_main.status_label = tk.Label(window_main, text=status_str, font=("Arial", 8), bg=WHITE, fg=BLACK)

# GUI LAYOUT #
# Image preview
window_main.image_canvas.grid(row=0, column=0, rowspan=7, columnspan=6, sticky="NESW", padx=8, pady=8)

# Buttons
window_main.button_show_source.grid(row=8, column=0, sticky="NWE", padx=8, pady=2)
window_main.button_show_output.grid(row=9, column=0, sticky="NWE", padx=8, pady=2)
window_main.button_run.grid(row=10, column=0, rowspan=2, sticky="NWES", padx=8, pady=2)

# Status label
window_main.status_label.grid(row=12, column=0, columnspan=6, sticky="NWS", padx=8, pady=(12,0))

# START #
window_main.mainloop()