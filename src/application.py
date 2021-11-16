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
YELLOW = "#dddd44"
GREEN = "#118111"
BLUE = "#1111ff"
INDIGO = "#4b40c2"
VIOLET = "#ee82ee"
PINK = "#ff6f97"
PRIMARY = "#DCDCDC"
DEFAULT = "#F0F0F0"
FONT_PRIMARY = "Fixedsys"
FONT_SECONDARY = "System"
COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET, PINK]
NAMES = ["A", "B", "C", "D", "E", "F", "G", "H"]

window_main = tk.Tk()
window_main.title("Perspective Tool")
window_main.geometry("+5+5")
window_main.resizable(False, False)
window_main.configure(bg=WHITE)

window_main.source_image_path = ""      # Path for source image
window_main.output_image_path = ""      # Path where output image will be saved
window_main.source_image = []           # Source input image
window_main.output_image = []           # Processed output image
window_main.preview_image = []          # Preview image for GUI display
window_main.select_points = False       # Flag: For point selection
window_main.select_faces = False        # Flag: For face selection
# Flag: True if an image has been processed, otherwise false
window_main.ran = False

# Offset for image pixel collection from mouse (subtracts width of black bar)
width_offset = 0
image = []                              # The image to process
# Actual image coordinates for selected points
clicked_points = []
circle_points = []                      # Coordinates for drawn circles on screen
canvas_elements = []
processed_images = []                   # List holds all processed images
# List of all points clicked by a user (user to remember points and lock edges)
all_click_points = []
# List of all coordinates for drawn circles on screen
all_circle_points = []
# Holds all face letter coordinates on the canvas
face_letter_coordinates = []
# List of all canvas_elements list (each outline box for each job)
canvas_job_elements = []
# The user's selected face (value will be integer from 0 to 7)
selected_face = -1
removed = []                            # Tracks removed faces so they can be redrawn
edges = []                              # Holds edges

# Menu commands (used for GUI menu bar)
# load_image: Asks user to choose a source image to process


def load_image():
    # Get the image's path, then load it into the program
    window_main.source_image_path = askopenfilename(title="Load Image")
    window_main.source_image = cv2.cvtColor(cv2.imread(
        window_main.source_image_path), cv2.COLOR_BGR2RGB)

    # Update program status and print to console
    update_status("Loaded image " + window_main.source_image_path + ".")

    # Show the image in the preview box
    show_image(window_main.source_image)

# save_image: Allows user to save the output image to a path


def save_image(img, def_name):
    window_main.output_image_path = asksaveasfilename(
        title="Save Output Image", initialfile=def_name, defaultextension=".jpg")
    cv2.imwrite(window_main.output_image_path, img)
    update_status("Saved output image " + window_main.output_image_path)

# def order_points(points):
#     rect = np.zeros((4, 2), dtype="float32")
#     s = points.sum(axis=1)
#     rect[0] = points[np.argmin(s)]
#     rect[2] = points[np.argmax(s)]
#     diff = np.diff(points, axis=1)
#     rect[1] = points[np.argmin(diff)]
#     rect[3] = points[np.argmin(diff)]
#     return rect


def process_image(points):

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

    new_image = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]],
        dtype="float32")

    # compute perspective transform matrix
    selected_points = np.array(points, dtype="float32")
    transformation_matrix = cv2.getPerspectiveTransform(
        selected_points, new_image)
    warped_image = cv2.warpPerspective(
        image, transformation_matrix, (maxWidth, maxHeight))

    # add the processed image to the list of complete images
    processed_images.append(warped_image)

    return warped_image

# Program functions (used to process the image)
# run: will process image and display it in the preview box


def run():

    # Make sure there is a selected image to process
    if window_main.source_image_path == "":
        update_status(
            "No image selected. Please load an image then press run.")
        return

    update_status("Processing...")
    for i in range(all_click_points.__len__()):
        process_image(all_click_points[i])
    update_status("Image processed.")
    window_main.ran = True
    # show_output()

# Helper functions (used for misc. GUI)
# show image: will show an image in the preview box


def show_image(img):
    global width_offset, image

    img_height, img_width = img.shape[:2]
    img = cv2.resize(img, (int(570 * (img_width / img_height)),
                     570), interpolation=cv2.INTER_AREA)
    image = img
    window_main.preview_image = PIL.ImageTk.PhotoImage(
        image=PIL.Image.fromarray(img))
    window_main.image_canvas.create_image(
        300, 285, anchor=tk.CENTER, image=window_main.preview_image)
    width_offset = int((window_main.preview_image.width() - 600) / 2)

# update_status: updates program status label


def update_status(status_str):
    window_main.status_label.configure(text=status_str)
    print(status_str)


def select_faces():

    if not window_main.select_faces:
        # bind canvas to mouse click
        window_main.image_canvas.bind("<Button-1>", select_face)
        window_main.select_faces = True
        # instruct user to select faces to edit them
        update_status(
            "Left click the letter of a face to select it, click this button agian to cancel")
    else:
        # instruct user to select faces to edit them
        update_status("")
        window_main.select_faces = False
        # unbind left mouse click from the canvas
        window_main.image_canvas.unbind("<Button-1>")


def select_face(event):
    global selected_face

    # loop through each face letter coordinate, count a selection if its within a +/- 20 range
    for i in range(face_letter_coordinates.__len__()):
        face_x = face_letter_coordinates[i][0]
        face_y = face_letter_coordinates[i][1]
        if (face_x in range(event.x - 20, event.x + 20)) and (face_y in range(event.y - 20, event.y + 20)):
            # tell user what face they have selected
            update_status("Selected face " + NAMES[i])

            # unbind left mouse click from the canvas
            window_main.image_canvas.unbind("<Button-1>")
            selected_face = i


def select_edges():
    window_main.image_canvas.bind("<Button-1>", select_edge)


def select_edge(event):
    global all_click_points, all_circle_points, circle_points, canvas_elements, clicked_points, edges

    # mouse x,y are each point's coordinates on the actual source image
    mouse_x = event.x + width_offset
    mouse_y = event.y

    # circle x,y are each point's coordinates on the canvas image embedded in the gui
    circle_x = event.x
    circle_y = event.y

    # snap mouse clicks to already selected points
    for i in range(all_click_points.__len__()):
        for j in range(4):
            click_point = all_click_points[i][j]
            circle_point = all_circle_points[i][j]
            if (click_point[0] in range(mouse_x - 6, mouse_x + 6)) and (click_point[1] in range(mouse_y - 6, mouse_y + 6)):
                mouse_x = click_point[0]
                mouse_y = click_point[1]
                circle_x = circle_point[0]
                circle_y = circle_point[1]

                # save the point where the user clicked as a point on the image (mouse x,y) and on the canvas image (circle x,y)
                circle_points.append([circle_x, circle_y])

                canvas_elements.append(window_main.image_canvas.create_oval(
                    circle_x - 4, circle_y - 4, circle_x + 4, circle_y + 4, fill=WHITE))

                if circle_points.__len__() == 2:

                    # unbind left mouse click from the canvas
                    window_main.image_canvas.unbind("<Button-1>")

                    # append all the canvas elements for this job (all circles and lines drawn over the image)
                    canvas_elements.append(window_main.image_canvas.create_line(
                        circle_points[0][0], circle_points[0][1], circle_points[1][0], circle_points[1][1], width=3, fill=WHITE))

                    # append the edge to the set of edges
                    edge = [[circle_points[0][0], circle_points[0][1]],
                            [circle_points[1][0], circle_points[1][1]]]
                    edges.append(edge)

                    # append the canvas elements to the list of all elements
                    canvas_job_elements.append(canvas_elements)

                    # update status, display coordinates for all points selected
                    update_status("Edge created: " + str(edge))

                    # reset the clicked points list, this current job is done
                    clicked_points = []
                    canvas_elements = []
                    circle_points = []
                    return
                else:
                    return


def select_points():
    if window_main.source_image_path == "":
        update_status("Load an image first.")
    window_main.image_canvas.bind("<Button-1>", select_point)


def select_point(event):
    global clicked_points, canvas_elements, circle_points

    # set what color and name this face should use
    if removed.__len__() != 0:
        # see if there is a color to reuse, if there is then use that color/name id for the face
        face_id = removed[0]
    else:
        # if not, then use the next face color/name in the list
        face_id = all_click_points.__len__()

    # iterate color and name for selection with each new selection
    color = COLORS[face_id]
    name = NAMES[face_id]

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
    canvas_elements.append(window_main.image_canvas.create_oval(
        circle_x - 6, circle_y - 6, circle_x + 6, circle_y + 6, fill=color))

    # save the point where the user clicked as a point on the image (mouse x,y) and on the canvas image (circle x,y)
    clicked_points.append([mouse_x, mouse_y])
    circle_points.append([circle_x, circle_y])

    # update status, print coordinates of clicked point
    update_status("Point Selected: " +
                  "[" + str(mouse_x) + "," + str(mouse_y) + "]")

    # runs when all 4 points have been selected
    if clicked_points.__len__() == 4:

        # remove the reused face is applicable
        if removed.__len__() != 0:
            removed.pop()

        # unbind left mouse click from the canvas
        window_main.image_canvas.unbind("<Button-1>")

        # append all the canvas elements for this job (all circles and lines drawn over the image)
        canvas_elements.append(window_main.image_canvas.create_line(
            circle_points[0][0], circle_points[0][1], circle_points[1][0], circle_points[1][1], width=3, dash=(4, 2), fill=color))
        canvas_elements.append(window_main.image_canvas.create_line(
            circle_points[1][0], circle_points[1][1], circle_points[2][0], circle_points[2][1], width=3, dash=(4, 2), fill=color))
        canvas_elements.append(window_main.image_canvas.create_line(
            circle_points[2][0], circle_points[2][1], circle_points[3][0], circle_points[3][1], width=3, dash=(4, 2), fill=color))
        canvas_elements.append(window_main.image_canvas.create_line(
            circle_points[3][0], circle_points[3][1], circle_points[0][0], circle_points[0][1], width=3, dash=(4, 2), fill=color))

        # average x and y to find center of the selection
        center_of_selection_x = int(
            (circle_points[0][0] + circle_points[1][0] + circle_points[2][0] + circle_points[3][0]) / 4)
        center_of_selection_y = int(
            (circle_points[0][1] + circle_points[1][1] + circle_points[2][1] + circle_points[3][1]) / 4)
        face_letter_coordinates.append(
            [center_of_selection_x, center_of_selection_y])
        canvas_elements.append(window_main.image_canvas.create_text(
            center_of_selection_x, center_of_selection_y, text=name, font=(FONT_PRIMARY, 40), fill=color))

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


def delete_face():
    global selected_face

    # check to see if a face was selected
    if selected_face == -1:
        update_status(
            "Click 'select face' to select a face first, then this button to delete it")
        return

    # delete all of the face's data and clear it from the canvas
    all_click_points.remove(all_click_points[selected_face])
    all_circle_points.remove(all_circle_points[selected_face])
    for element in canvas_job_elements[selected_face]:
        window_main.image_canvas.delete(element)

    # append the face to the removed list so the name and color can be reused
    removed.append(selected_face)
    selected_face = -1


def redraw_face():
    global selected_face

    # check to see if a face was selected
    if selected_face == -1:
        update_status(
            "Click 'select face' to select a face first, then this button to redraw it")
        return

    # delete the face then call select_points so the user can redraw it
    delete_face()
    select_points()


def export_images():
    num = 0
    for i in processed_images:
        def_name = "Selection_" + NAMES[num]
        save_image(i, def_name)
        num += 1


def export_composite():
    global all_circle_points, processed_images, edges

    update_status("Building composite...")

    # compute the width and height of the stitched image
    # tl, tr, br, bl

    # get number of faces (this is equal to the number of processed images we have)
    num_faces = all_click_points.__len__()

    # this list holds what side of each image should be glued together (each side is defined by two corner points
    sides_to_glue = []
    # what faces those sides will be glued to (list of faces)
    face_connections = []
    face_edges_all = []

    # iterate through each selection (set of four points)
    i = 1
    for selection in all_circle_points:

        # create lists to hold what relative points are part of the edge (bottom left, top right, etc), and the actual
        # coordinate value of the edge [x, y]
        face_sides = []
        face_edges = []

        # iterate through each edge (set of two points)
        for edge in edges:

            side = []
            face_edge = []
            found = False

            # check if the top left point is part of the edge
            if selection[0] in edge:
                found = True
                side.append('tl')
            # check if the top right point is part of the edge
            if selection[1] in edge:
                found = True
                side.append('tr')
            # check if the bottom right point is part of the edge
            if selection[2] in edge:
                found = True
                side.append('br')
            # check if the bottom left point is part of the edge
            if selection[3] in edge:
                found = True
                side.append('bl')

            # if an edge was found, append it
            if found:
                face_edge.append(edge)

            if side.__len__() == 2:
                face_sides.append(side)
                face_edges.append(face_edge)

        # add the side information to the list of all sides that must be glued
        sides_to_glue.append(face_sides)
        face_edges_all.append(face_edges)

        i += 1

    # for each face, find what other faces they are connected to
    # how: for each face i iterate through every other face j, then iterate through these faces edges k (for face i) and
    # h (for face j). if an edge k in i is equal to an edge h in j, we know that face i will need to be glued to face j
    for i in range(num_faces):
        face_list = []
        for j in range(num_faces):
            for k in range(face_edges_all[i].__len__()):
                for h in range(face_edges_all[j].__len__()):
                    if face_edges_all[i][k] == face_edges_all[j][h] and j != i:
                        face_list.append(j)
        face_connections.append(face_list)

    # compute width and height of composite image, start with face A
    width = processed_images[0].shape[1]
    height = processed_images[0].shape[0]

    TOP = ['tl', 'tr']
    RIGHT = ['tr', 'br']
    LEFT = ['tl', 'bl']
    BOTTOM = ['br', 'bl']

    # for i in range(1, num_faces):
    #     w = processed_images[i].shape[0]
    #     h = processed_images[i].shape[1]
    #
    #     for j in range(sides_to_glue[i].__len__()):
    #         if sides_to_glue[i][j] == TOP:
    #             height += h

    # this list holds the faces that have already been counted to compute the total width and height, its needed to not count images twice
    counted_faces = []

    # this list holds where each image should be written in the larger image (the top left corner coordinate)
    image_write_start = []
    for i in range(num_faces):
        image_write_start.append([0, 0])

    # this list holds booleans that say if an image needs to be rotated (will be true if image is glued to the left or right of a face)
    need_to_rotate = []
    for i in range(num_faces):
        need_to_rotate.append(False)

    for i in range(num_faces):

        # get the current face's width and height
        current_face_width = processed_images[i].shape[1]
        current_face_height = processed_images[i].shape[0]

        print("Face " + str(i) + ": " + str(current_face_width) +
              ", " + str(current_face_height))
        for j in range(face_connections[i].__len__()):

            # find the connected face
            connected_face = face_connections[i][j]

            # if the connected face has already been counted, don't do the following computations
            if connected_face in counted_faces:
                break

            # boolean controls if this side was counted for width or height of the compleate image
            counted = False

            # image_write_start[i][0] = current_face_width
            # image_write_start[i][1] = current_face_height

            # get the connected face's width and height
            connected_face_width = processed_images[connected_face].shape[1]
            connected_face_height = processed_images[connected_face].shape[0]

            # depending on what side is connected, add to the width of height
            if sides_to_glue[i][j] == TOP:
                print("face " + str(i) +
                      " will be glued to the bottom of " + str(connected_face))
                height += connected_face_height
                counted = True

                # top left corner should share x of parent image x, and y of parent image y - this images height
                image_write_start[connected_face][0] = image_write_start[i][0]
                image_write_start[connected_face][1] = image_write_start[i][1] - \
                    current_face_height

            if sides_to_glue[i][j] == BOTTOM:
                print("face " + str(i) +
                      " will be glued to the top of " + str(connected_face))
                height += connected_face_height
                counted = True

                # top left corner should share x of parent image x, and y of parent image y + this images height
                image_write_start[connected_face][0] = image_write_start[i][0]
                image_write_start[connected_face][1] = image_write_start[i][1] + \
                    current_face_height

            if sides_to_glue[i][j] == LEFT:
                print("face " + str(i) +
                      " will be glued to the right of " + str(connected_face))
                width += connected_face_height
                counted = True
                need_to_rotate[connected_face] = True

                # top left corner should share x of parent image x - this images width, and y of parent image y
                image_write_start[connected_face][0] = image_write_start[i][0] - \
                    current_face_width
                image_write_start[connected_face][1] = image_write_start[i][1]

            if sides_to_glue[i][j] == RIGHT:
                print("face " + str(i) +
                      " will be glued to the left of " + str(connected_face))
                width += connected_face_height
                counted = True
                need_to_rotate[connected_face] = True

                # top left corner should share x of parent image x + this images width, and y of parent image y
                image_write_start[connected_face][0] = image_write_start[i][0] + \
                    current_face_width
                image_write_start[connected_face][1] = image_write_start[i][1]

            if counted:
                counted_faces.append(i)
    print("Total image: " + str(width) + ", " + str(height))

    # generate a blank image with the total width and height
    composite_image = np.zeros((height, width, 3), dtype="uint8")

    # iterate through all images
    for img in range(num_faces):

        # compute where the next image write should start (this will be where the top left corner is)
        x_in_composite = image_write_start[img][0]
        y_in_composite = image_write_start[img][1]

        if need_to_rotate[img]:
            for i in range(processed_images[img].shape[0]):
                for j in range(processed_images[img].shape[1]):
                    v = processed_images[img][i][j]
                    composite_image[y_in_composite + j][x_in_composite + i] = v
        else:
            for i in range(processed_images[img].shape[0]):
                for j in range(processed_images[img].shape[1]):
                    v = processed_images[img][i][j]
                    composite_image[y_in_composite + i][x_in_composite + j] = v

    # Save the image
    save_image(composite_image, "Composite")
    update_status("Composite image built.")


# GUI CREATION #
# Create menu
menu = Menu(window_main)
file_items = Menu(menu, tearoff=0, bg=WHITE)
file_items.add_command(label="Load Image", command=load_image)
menu.add_cascade(label="File", menu=file_items)
adjust_items = Menu(menu, tearoff=0)
window_main.config(menu=menu)

# Create preview box for image
window_main.image_canvas = tk.Canvas(
    window_main, width=600, height=570, relief="flat")
window_main.image_canvas.create_rectangle(0, 0, 600, 570, fill=BLACK)

# Create buttons
window_main.button_select_points = tk.Button(window_main, text="Add Face", font=(
    FONT_PRIMARY, 12), command=select_points, padx="2", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_export_images = tk.Button(window_main, text="Export Images", font=(
    FONT_PRIMARY, 12), command=export_images, padx="2", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_export_composite = tk.Button(window_main, text="Export Composite", font=(
    FONT_PRIMARY, 12), command=export_composite, padx="2", bg=PRIMARY, fg=BLACK, relief="groove")

window_main.button_run = tk.Button(window_main, text="Process All", font=(
    FONT_PRIMARY, 12), command=run, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_clear_all = tk.Button(window_main, text="Clear All", font=(
    FONT_PRIMARY, 12), command=run, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_edit_face = tk.Button(window_main, text="Select Face", font=(
    FONT_PRIMARY, 12), command=select_faces, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_delete_face = tk.Button(window_main, text="Delete Face", font=(
    FONT_PRIMARY, 12), command=delete_face, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_redraw_face = tk.Button(window_main, text="Redraw Face", font=(
    FONT_PRIMARY, 12), command=redraw_face, padx="10", bg=PRIMARY, fg=BLACK, relief="groove")
window_main.button_select_edges = tk.Button(window_main, text="Add Edge", font=(
    FONT_PRIMARY, 12), command=select_edges, padx="2", bg=PRIMARY, fg=BLACK, relief="groove")

# Create status label
status_str = "Choose a source image (under 'File/Load Image'), and press run."
window_main.status_label = tk.Label(
    window_main, text=status_str, font=("Arial", 8), bg=WHITE, fg=BLACK)

# GUI LAYOUT #
# Image preview
window_main.image_canvas.grid(
    row=0, column=0, rowspan=9, columnspan=8, sticky="NESW", padx=8, pady=8)

# Buttons
window_main.button_select_points.grid(
    row=10, column=1, sticky="NESW", padx=2, pady=2)
window_main.button_run.grid(row=10, column=2, sticky="NESW", padx=2, pady=2)
window_main.button_export_images.grid(
    row=10, column=7, sticky="NESW", padx=8, pady=2)
window_main.button_export_composite.grid(
    row=11, column=7, sticky="NESW", padx=8, pady=2)
window_main.button_clear_all.grid(
    row=10, column=0, sticky="NESW", padx=(8, 2), pady=2)
window_main.button_edit_face.grid(
    row=11, column=0, sticky="NESW", padx=(8, 2), pady=2)

window_main.button_delete_face.grid(
    row=11, column=1, sticky="NESW", padx=2, pady=2)
window_main.button_redraw_face.grid(
    row=11, column=2, sticky="NESW", padx=2, pady=2)

window_main.button_select_edges.grid(
    row=11, column=2, sticky="NESW", padx=2, pady=2)

# Status label
window_main.status_label.grid(
    row=12, column=0, columnspan=8, sticky="NWS", padx=8, pady=(12, 0))

# START #
window_main.mainloop()
