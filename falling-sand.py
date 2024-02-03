import tkinter as tk
from random import choice
import time

# These are not being used yet
AIR = 0
WALL = 1
SAND = 2
WATER = 3
FIRE = 4

class FallingSand:
    def __init__(self, root, title, width, height, cell_size):
        # Window Variables
        self.root = root
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False,False)
        
        # Build the options menu
        self.build_menu()
       
        # Simulation Variables
        self.rows    = height // cell_size
        self.columns = width // cell_size
        self.grid    = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        self.drawing = False
        self.mouse_position = (0,0)
        
        # Canvas Variables
        self.canvas_width   = width
        self.canvas_height  = height
        self.cell_size      = cell_size
        
        self.canvas = tk.Canvas(root, width=width, height=height, bg="white")
        self.canvas.pack()
        
        # Create an FPS counter label
        self.fps_label = tk.Label(root, text="FPSL 0", font=("Helvetica", 12))
        self.fps_label.place(x=10, y=10)
        
        # Draw and update the sand particles
        self.canvas.bind("<ButtonPress-1>", self.start_drawing) # start drawing sand when mouse is pressed down
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing)# stop drawing sand when mouse is released
        self.canvas.bind("<Motion>", self.track_mouse) # update the current mouse position in relation to the canvas
        self.last_time = time.time()
        self.update_sand()

    def start_drawing(self, event):
        self.drawing = True
        self.draw_sand()
    
    def stop_drawing(self, event):
        self.drawing = False
    
    def track_mouse(self, event):
        self.mouse_position = (event.x, event.y)
    
    def draw_sand(self):
        if self.drawing:
            # draw the sand particle when the event is triggered
            row     = self.mouse_position[1] // self.cell_size
            column  = self.mouse_position[0] // self.cell_size
            
            # Checks to see if in the bounds of the canvas
            if 0 <= row < self.rows and 0 <= column <= self.columns-1:
                self.grid[row][column] = 1
                self.updated = True
            self.root.after(10, self.draw_sand)
    
    def update_sand(self):
        new_grid = [[0 for _ in range(self.columns)] for _ in range(self.rows)]
        
        # parse through the entire grid
        for row in range(self.rows - 1, -1, -1): # parse from down to up
            for column in range(self.columns): # parse from left to right
                if self.grid[row][column] > 0:
                    if row == self.rows - 1: # if you're at the bottom, stay in place
                        new_grid[row][column] = self.grid[row][column]
                    elif self.grid[row+1][column] > 0: # if there is a sand below you,
                        dir = choice([-1,1]) # pick a random direction, -1 left or +1 right
                        if 0 <= column+dir < self.columns and self.grid[row+1][column+dir] == 0 and new_grid[row+1][column+dir] == 0: # if the tile down one and to the direction 1 is empty, and there is not already a new sand in that spot
                            new_grid[row+1][column+dir] = self.grid[row][column]
                        elif 0 <= column-dir < self.columns and self.grid[row+1][column-dir] == 0 and new_grid[row+1][column-dir] ==0:
                            new_grid[row+1][column-dir] = self.grid[row][column]
                        else:
                            new_grid[row][column] = self.grid[row][column]
                    else: # no obsticals or out of bounds, move down one
                        new_grid[row + 1][column] = self.grid[row][column]
        
        self.grid = new_grid
        self.update_canvas()
        
        # Calculate FPS
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        fps = int(1/elapsed_time)
        self.last_time = current_time
        
        # Update FPS label
        self.fps_label.config(text=f"FPS: {fps}")
        
        self.root.after_idle(self.update_sand)
    
    def update_canvas(self):
        self.canvas.delete("all")
        for row in range(self.rows):
            for column in range(self.columns):
                if self.grid[row][column] == 1:
                    x = column * self.cell_size
                    y = row * self.cell_size
                    self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill="black", outline="")
        self.root.update_idletasks()
    
    def build_menu(self):
        # TODO: Make the menus work
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save (Ctrl + S)")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo (Ctrl + Z)")
        edit_menu.add_command(label="Redo (Ctrl + Y)")
        menu_bar.add_cascade(label="Edit", menu=edit_menu)

        info_menu = tk.Menu(menu_bar, tearoff=0)
        info_menu.add_command(label="Particle Info")
        info_menu.add_command(label="About...")
        menu_bar.add_cascade(label="Help", menu=info_menu)
        
        self.root.config(menu=menu_bar)
    
    
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    window_width, window_height = 600,500
    cell_size = 5
    applicaiton_title = "Python Sand Simulator"
    root = tk.Tk()
    app = FallingSand(root, applicaiton_title, window_width, window_height, cell_size)
    app.run()