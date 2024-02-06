import pickle
import tkinter as tk
import tkinter.filedialog as tkFileDialog
import numpy as np
from random import choice
import time

AIR = 0     # Empty tile
STONE = 1   # stationary and indestructible
SAND = 2    # falls down and piles up, heavier than water
WATER = 3   # falls down and spreads out
WOOD = 4    # stationary but flammable
FIRE = 5    # spreads onto flammable particles

# element colors
# https://www.plus2net.com/python/tkinter-colors.php
AIR_COLOR = "#FAEBD7" # note: we should never actually be drawing air rectangles, this is just for the canvas background
STONE_COLOR = "#808A87" # coldgrey
WOOD_COLOR = "#8B4513" # chocolate
SAND_COLOR = "#F4A460" # saddlebrown
WATER_COLOR = "#7FFFD4" # aquamarine1
FIRE_COLOR = "#FF6103" #cadmiumorange

class FallingSand:
    def __init__(self, root, title, width, height, cell_size, target_fps, debug):
        # Window Variables
        self.root = root
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False,False)
        self.debug = debug
        
        # Build the options menu
        self.current_particle = SAND
        self.build_menu()
       
        # Simulation Variables
        self.columns = width // cell_size  # x
        self.rows    = height // cell_size # y
        self.grid    = np.zeros((self.rows, self.columns), dtype=[('particle_type', int),('particle_color','U10')])
        self.grid.fill((AIR,AIR_COLOR))
        self.drawing = False
        self.mouse_position = (0,0)
        self.target_fps = target_fps
        self.delay = 0
        
        # Canvas Variables
        self.canvas_width   = width
        self.canvas_height  = height
        self.cell_size      = cell_size
        
        self.vary_color(SAND_COLOR)
        
        self.canvas = tk.Canvas(root, width=width, height=height, bg=AIR_COLOR)
        self.canvas.pack()
        if self.debug:
            #print(f"rows: {self.rows}\ncolumns: {self.columns}")
            self.debug_tile_labels()        
        
        # Create an FPS counter label
        self.fps_label = tk.Label(root, text="FPS: 0", font=("Helvetica", 12))
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
    
    def debug_tile_labels(self):
        print(f"rows: {self.rows}\ncolumns:{self.columns}")
        for row in range(self.rows):
            for column in range(self.columns):
                self.canvas.create_text(column*self.cell_size + 10, row*self.cell_size + 10, text=f"{row},{column}", font=("Helvetica", 8)) 

    def swap_particles(self, particle_1, particle_2):
        grid_x1, grid_y1 = particle_1
        grid_x2, grid_y2 = particle_2
        # pass the particle location as a tuple(row, column)
        temp = tuple(self.grid[grid_x1][grid_y1])
        self.grid[grid_x1][grid_y1] = self.grid[grid_x2][grid_y2]
        self.grid[grid_x2][grid_y2] = temp

        canvas_y1 = grid_x1 * self.cell_size
        canvas_x1 = grid_y1 * self.cell_size
        canvas_y2 = grid_x2 * self.cell_size
        canvas_x2 = grid_y2 * self.cell_size

        # delete whatever rectangles were at the old locations
        self.canvas.delete(self.canvas.find_overlapping(canvas_x1+1,canvas_y1+1,canvas_x1+2,canvas_y1+2))
        self.canvas.delete(self.canvas.find_overlapping(canvas_x2+1,canvas_y2+1,canvas_x2+2,canvas_y2+2))

        # draw the new rectangles if they're not AIR
        if self.grid[grid_x1][grid_y1][0] != AIR:
            self.canvas.create_rectangle(canvas_x1, canvas_y1, canvas_x1+cell_size, canvas_y1+cell_size, fill=self.grid[grid_x1][grid_y1][1], outline="")
        if self.grid[grid_x2][grid_y2][0] != AIR:
            self.canvas.create_rectangle(canvas_x2, canvas_y2, canvas_x2+cell_size, canvas_y2+cell_size, fill=self.grid[grid_x2][grid_y2][1], outline="")


    def draw_particle(self):
        if self.drawing:
            # draw the sand particle when the event is triggered
            column  = self.mouse_position[0] // self.cell_size
            row     = self.mouse_position[1] // self.cell_size

            # Checks to see if in the bounds of the canvas
            if 0 <= row < self.rows and 0 <= column <= self.columns-1:
                if self.current_particle == SAND: # If current particle is SAND
                    self.grid[row][column] = (SAND, self.vary_color(SAND_COLOR))
                elif self.current_particle == WATER: # If current particle is WATER
                    self.grid[row][column] = (WATER, self.vary_color(WATER_COLOR))
                elif self.current_particle == STONE:
                    self.grid[row][column] = (STONE, self.vary_color(STONE_COLOR))
                    self.swap_particles((row,column),(row,column))
                elif self.current_particle == AIR:
                    self.grid[row][column] = (AIR, AIR_COLOR)
                    self.swap_particles((row,column),(row,column))
            self.root.after_idle(self.draw_particle)
    
    def update_particle(self): 
        # parse through the entire grid
        for row in range(self.rows - 1, -1, -1): # parse from down to up
            for column in range(self.columns): # parse from left to right
                # SAND
                if self.grid[row][column][0] == SAND:
                    # if it's the bottom of the grid
                    if row == self.rows - 1:
                        # DO NOTHING, particle stays in place
                        pass
                    # If it encounter a non-AIR, non-WATER obstacle
                    elif self.grid[row+1][column][0] != AIR and self.grid[row+1][column][0] != WATER:
                        # pick a random direction
                        direction = choice([-1,1])
                        # if the tile down one and to the direction on is AIR or WATER, then swap with that tile
                        if 0<= column+direction < self.columns:
                            if (self.grid[row+1][column+direction][0] == AIR or self.grid[row+1][column+direction][0] == WATER) and (self.grid[row][column+direction][0] == AIR or self.grid[row][column+direction][0] == WATER):
                                self.swap_particles((row,column),(row+1,column+direction))
                        # if both diagonal spots have non-AIR or non-WATER particles, then stay in place
                    # If there is no obstacles below it
                    else:
                        # move down one
                        self.swap_particles((row,column),(row+1,column))
                #WATER
                elif self.grid[row][column][0] == WATER:
                    # if its the bottom of the grid, move back and forth
                    # if there is a non-AIR particle, move back and forth
                    if row == self.rows-1 or self.grid[row+1][column][0] != AIR:
                        direction = choice([-1,0,1, 1,1,1,1,1]) # the more 0's in this the slower the water will slosh
                        if direction != 0:
                            # if the tile in the direction is AIR, swap
                            if 0<= column+direction < self.columns:
                                if self.grid[row][column+direction][0] == AIR:
                                    self.swap_particles((row,column),(row,column+direction))
                            # else if the tile in the other direction is AIR, swap
                            if 0<= column-direction < self.columns:
                                if self.grid[row][column-direction][0] == AIR:
                                    self.swap_particles((row,column),(row,column-direction))
                            # else if both neighbors are occupied, do nothing
                    #else if there is no obstacles below it
                    else:
                        # move down one
                        self.swap_particles((row,column),(row+1,column))
                # STONE
                elif self.grid[row][column][0] == STONE:
                    # STONE does not move once placed
                    pass
        
        # Calculate FPS
        current_time = time.time()
        elapsed_time = current_time - self.last_time
        if elapsed_time > 0:
            fps = int(1/elapsed_time)
            
            # Adjust delay to hit target FPS
            self.delay = max(0, int((500 / self.target_fps) - elapsed_time))
            
            self.last_time = current_time
            
            # Update FPS label
            self.fps_label.config(text=f"FPS: {fps}")
        
        self.root.after(self.delay, self.update_particle)

    def set_particle(self, value):
        self.current_particle = value
    
    def reset_scene(self):
        self.grid.fill((AIR,AIR_COLOR))
        self.canvas.delete("all")

    def save_scene(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.grid, file)

    def load_scene(self, filename):
        with open(filename, 'rb') as file:
            self.grid = pickle.load(file)
        
        self.canvas.delete("all")
        for row in range(self.rows):
            for column in range(self.columns):
                if self.grid[row][column][0] != AIR:
                    self.canvas.create_rectangle(column * self.cell_size, row * self.cell_size, (column + 1) * self.cell_size, (row + 1) * self.cell_size, fill=self.grid[row][column][1], outline="")

    def save_scene_dialog(self):
        filename = tk.filedialog.asksaveasfilename(defaultextension=".sand")
        if filename:
            self.save_scene(filename)
    
    def load_scene_dialog(self):
        filename = tk.filedialog.askopenfilename(filetypes=[("Sand Simulator Scenes", "*.sand")])
        if filename:
            self.load_scene(filename)

    def build_menu(self):
        menu_bar = tk.Menu(self.root)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Scene (Ctrl + N)", command=self.reset_scene)
        file_menu.add_command(label="Open Scene (Ctrl + O)", command=self.load_scene_dialog)
        file_menu.add_command(label="Save Scene (Ctrl + S)", command=self.save_scene_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        particle_menu = tk.Menu(menu_bar, tearoff=0)
        particle_menu.add_radiobutton(label="Sand", command=lambda: self.set_particle(SAND))
        particle_menu.add_radiobutton(label="Water", command=lambda: self.set_particle(WATER))
        particle_menu.add_radiobutton(label="Stone", command=lambda: self.set_particle(STONE))
        particle_menu.add_radiobutton(label="Erase", command=lambda: self.set_particle(AIR))
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
    application_title = "Python Sand Simulator"
    debug = False
    root = tk.Tk()
    app = FallingSand(root, application_title, window_width, window_height, cell_size, target_fps, debug)
    app.run()