import tkinter as tk
import numpy as np
from random import choice
import time

# These are not being used yet
AIR = 0
WALL = 1
SAND = 2
WATER = 3

# element colors
# https://www.plus2net.com/python/tkinter-colors.php
AIR_COLOR = "#FAEBD7"
WALL_COLOR = "gray27"
SAND_COLOR = "#F4A460"
WATER_COLOR = "CadeyBlue1"

class FallingSand:
    def __init__(self, root, title, width, height, cell_size, target_fps):
        # Window Variables
        self.root = root
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False,False)
        
        # Build the options menu
        self.current_particle = tk.IntVar()
        self.current_particle.set(SAND)
        self.build_menu()
       
        # Simulation Variables
        self.rows    = height // cell_size
        self.columns = width // cell_size
        self.grid    = np.zeros((self.rows, self.columns, 2), dtype=object) # creates a 2d grid, each containing a tuple with an int representing the particle type and a string for the color
        self.drawing = False
        self.mouse_position = (0,0)
        self.target_fps = target_fps
        
        # Canvas Variables
        self.canvas_width   = width
        self.canvas_height  = height
        self.cell_size      = cell_size
        self.changed_particles = {(row, column): False for row in range(self.rows) for column in range(self.columns)}
        
        self.vary_color(SAND_COLOR)
        
        self.canvas = tk.Canvas(root, width=width, height=height, bg=AIR_COLOR)
        self.canvas.pack()
        
        # Create an FPS counter label
        self.fps_label = tk.Label(root, text="FPSL 0", font=("Helvetica", 12))
        self.fps_label.place(x=10, y=10)
        self.last_time = time.time()
        
        # Draw and update the sand particles
        self.canvas.bind("<ButtonPress-1>", self.start_drawing) # start drawing sand when mouse is pressed down
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing) # stop drawing sand when mouse is released
        self.canvas.bind("<Motion>", self.track_mouse) # update the current mouse position in relation to the canvas
        self.last_time = time.time()
        self.update_particle()

    def start_drawing(self, event):
        self.drawing = True
        self.draw_particle()
    
    def stop_drawing(self, event):
        self.drawing = False
    
    def track_mouse(self, event):
        self.mouse_position = (event.x, event.y)
    
    def vary_color(self, color):
        # color is set to hex values
        # so formatted as #RRGGBB
        # if i want the color to vary a bit once spawned i just need to remove and vary the last character of each group of 2
        hex_range = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
        varied_color = f"#{color[1]}{choice(hex_range)}{color[3]}{choice(hex_range)}{color[5]}{choice(hex_range)}"
        return varied_color
    
    def draw_particle(self):
        if self.drawing:
            # draw the sand particle when the event is triggered
            row     = self.mouse_position[1] // self.cell_size
            column  = self.mouse_position[0] // self.cell_size
            
            # Checks to see if in the bounds of the canvas
            if 0 <= row < self.rows and 0 <= column <= self.columns-1:
                
                self.grid[row][column] = (SAND, self.vary_color(SAND_COLOR))
                self.changed_particles[(row, column)] = True
            self.root.after(10, self.draw_particle)
    
    def update_particle(self):
        new_grid = np.zeros((self.rows, self.columns, 2), dtype=object)
                
        # parse through the entire grid
        for row in range(self.rows - 1, -1, -1): # parse from down to up
            for column in range(self.columns): # parse from left to right
                # SAND
                # falls straight down then slides diagonally down if possible
                if self.grid[row][column][0] == SAND:
                    if row == self.rows - 1: # if you're at the bottom, stay in place
                        new_grid[row][column] = self.grid[row][column]
                    elif self.grid[row+1][column][0] > 0: # if there is a something(not AIR) below you,
                        dir = choice([-1,1]) # pick a random direction, -1 left or +1 right
                        if (0 <= column+dir < self.columns) and (self.grid[row+1][column+dir][0] == AIR) and (new_grid[row+1][column+dir][0] == AIR): # if the tile down one and to the direction 1 is in bounds AND empty AND there is not already a new sand in that spot
                            new_grid[row+1][column+dir] = self.grid[row][column]
                            self.changed_particles[(row, column)] = True
                            self.changed_particles[(row+1,column+dir)] = True
                        elif (0 <= column-dir < self.columns) and (self.grid[row+1][column-dir][0] == AIR) and (new_grid[row+1][column-dir][0] == AIR): # if the other tile down one and to the other direction is in bounds AND empty AND there is not already a new sand in that spot
                            new_grid[row+1][column-dir] = self.grid[row][column]
                            self.changed_particles[(row, column)] = True
                            self.changed_particles[(row+1,column-dir)] = True
                        else: # otherwise stay in place
                            new_grid[row][column] = self.grid[row][column]
                    else: # no obsticals or out of bounds, move down one
                        new_grid[row + 1][column] = self.grid[row][column]
                        self.changed_particles[(row, column)] = True
                        self.changed_particles[(row+1,column)] = True
                # TODO: Add different element's logic here
                # WATER
                # falls straight down then slides left or right if possible
        self.grid = new_grid
        self.update_canvas()
        
        # Calculate FPS
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        if elapsed_time > 0:
            fps = int(1/elapsed_time)
            
            # Adjust delay to hit target FPS
            delay = max(0, int((500 / self.target_fps) - elapsed_time))
            
            self.last_time = current_time
            
            # Update FPS label
            self.fps_label.config(text=f"FPS: {fps}")
        
        self.root.after(delay, self.update_particle)
    
    def update_canvas(self):
        # delete any particles in the changed particles dictionary
        # then draw the particles in the new locations
        for row, column in self.changed_particles.keys():
            x = column * self.cell_size
            y = row * self.cell_size
            # delete the rectangle if the new spot is air
            if self.grid[row][column][0] == AIR:
                self.canvas.delete(self.canvas.find_overlapping(x,y,x+1,y+1))    
            # draw the sand
            if self.grid[row][column][0] == SAND:
                self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=self.grid[row][column][1], outline="")
        self.root.update_idletasks()
        # clear the list of changed particles
        self.changed_particles = {}

    def set_particle(self):
        pass
    
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

        particle_menu = tk.Menu(menu_bar, tearoff=0)
        particle_menu.add_radiobutton(label="Sand", variable=self.current_particle, value=SAND, command=self.set_particle)
        particle_menu.add_radiobutton(label="Water", variable=self.current_particle, value=WATER, command=self.set_particle)
        particle_menu.add_radiobutton(label="Wall", variable=self.current_particle, value=WALL, command=self.set_particle)
        particle_menu.add_radiobutton(label="Erase", variable=self.current_particle, value=AIR, command=self.set_particle)
        menu_bar.add_cascade(label="Particles", menu=particle_menu)
        
        info_menu = tk.Menu(menu_bar, tearoff=0)
        info_menu.add_command(label="Particle Info")
        info_menu.add_command(label="About...")
        menu_bar.add_cascade(label="Help", menu=info_menu)
        
        self.root.config(menu=menu_bar)
    
    
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    window_width, window_height = 800,600
    cell_size = 10
    target_fps = 30
    applicaiton_title = "Python Sand Simulator"
    root = tk.Tk()
    app = FallingSand(root, applicaiton_title, window_width, window_height, cell_size, target_fps)
    app.run()