import pickle
import tkinter as tk
from tkinter import filedialog
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

class ParticleInfoWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Particle Info")
        #self.root.geometry("300x400")

        self.info_label = tk.Label(root, text="Particle Info", font=("Helvetica", 16, "bold"))
        self.info_label.pack(pady=10)

        self.info_frame = tk.Frame(root)
        self.info_frame.pack(expand=True, fill="both")

        self.populate_info()
    
    def populate_info(self):
        particle_info = {
            "Air": "Empty space",
            "Stone": "Stationary particle",
            "Sand": "Affected by gravity\nPiles up\nHeavier than water",
            "Water": "Affected by gravity\nFills available space",
            "Wood": "Stationary particle\nFlammable",
            "Fire": "Ignores gravity\nSpreads to flammable particles\nDies if there is no flammable particle\nDoused by water",
            "" : ""
        }
        # parse through this and populate a grid with tk.Text objects
        for index, (particle, description) in enumerate(particle_info.items()):
            particle_name = tk.Label(self.info_frame, text=particle, bd=1, relief=tk.SUNKEN, padx=5, pady=5)
            particle_name.grid(row=index, column=1, sticky="nsew")

            particle_description = tk.Label(self.info_frame, text=description, bd=1, relief=tk.SUNKEN, anchor="nw", padx=10, pady=5)
            particle_description.grid(row=index, column=2, sticky="nsew")

class FallingSand:
    def __init__(self, root, title, width, height, cell_size, target_fps, debug):
        # Window Variables
        self.root = root
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False,False)
        
        # debug logging
        self.debug = debug
        self.debug_index = 0
        self.debug_time = time.time()
        self.debug_log = []

        # Build the options menu
        self.current_particle = SAND
        self.build_menu()
       
        # Simulation Variables
        self.columns = width // cell_size  # x
        self.rows    = height // cell_size # y
        self.grid    = np.zeros((self.rows, self.columns), dtype=[('particle_type', int),('particle_color','U10')])
        self.grid.fill((AIR,AIR_COLOR))
        
        # Canvas Variables
        self.canvas_width   = width
        self.canvas_height  = height
        self.cell_size      = cell_size
        self.drawing = False
        self.mouse_position = (0,0)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.canvas = tk.Canvas(root, width=width, height=height, bg=AIR_COLOR)
        self.canvas.pack()

        # Create an FPS counter label
        self.fps_label = tk.Label(root, text="FPS: 0", font=("Helvetica", 8))
        self.fps_label.place(x=2, y=2)
        self.last_time = time.time()
        
        # Draw and update the sand particles
        self.canvas.bind("<ButtonPress-1>", self.start_drawing) # start drawing sand when mouse is pressed down
        self.canvas.bind("<ButtonRelease-1>", self.stop_drawing) # stop drawing sand when mouse is released
        self.canvas.bind("<Motion>", self.track_mouse) # update the current mouse position in relation to the canvas
        self.last_time = time.time()

        self.update_particle()


    def on_closing(self):
        print("Closing Falling Sand")
        with open("./bin/debug_log.txt", "wb") as file:
            pickle.dump(str(self.debug_log), file)
        self.root.quit()


    def debug_logger(self, method_call, method_name):
        self.debug_log.append((method_call, method_name,(time.time() - self.debug_time)))
        self.debug_last_time = time.time()

    def start_drawing(self, event):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started start_drawing()")
        self.drawing = True
        self.draw_particle()
        
        self.debug_logger(debug_temp_index, "ended start_drawing()")
    
    def stop_drawing(self, event):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started stop_drawing()")
        self.drawing = False
        self.debug_logger(debug_temp_index, "ended stop_drawing()")
    
    def track_mouse(self, event):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started track_mouse()")
        self.mouse_position = (event.x, event.y)
        self.debug_logger(debug_temp_index, "ended track_mouse()")
    
    def vary_color(self, color):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started vary_color()")
        # color is set to hex values
        # so formatted as #RRGGBB
        # if i want the color to vary a bit once spawned i just need to remove and vary the last character of each group of 2
        hex_range = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
        varied_color = f"#{color[1]}{choice(hex_range)}{color[3]}{choice(hex_range)}{color[5]}{choice(hex_range)}"
        self.debug_logger(debug_temp_index, "ended vary_color()")
        return varied_color

    def swap_particles(self, particle_1, particle_2):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started swap_particles()")
        grid_row1, grid_col1 = particle_1
        grid_row2, grid_col2 = particle_2
        # pass the particle location as a tuple(row, column)
        temp = tuple(self.grid[grid_row1][grid_col1])
        self.grid[grid_row1][grid_col1] = self.grid[grid_row2][grid_col2]
        self.grid[grid_row2][grid_col2] = temp

        canvas_x1 = grid_col1 * self.cell_size
        canvas_y1 = grid_row1 * self.cell_size
        canvas_x2 = grid_col2 * self.cell_size
        canvas_y2 = grid_row2 * self.cell_size
        # delete the old rectangles
        self.canvas.delete(self.canvas.find_overlapping(canvas_x1+1, canvas_y1+1, canvas_x1+2, canvas_y1+2))
        self.canvas.delete(self.canvas.find_overlapping(canvas_x2+1, canvas_y2+1, canvas_x2+2, canvas_y2+2))

        if self.grid[grid_row1][grid_col1][0] != AIR:
            self.canvas.create_rectangle(canvas_x1, canvas_y1, canvas_x1 + self.cell_size, canvas_y1 + self.cell_size, fill=self.grid[grid_row1][grid_col1][1], outline="")
        if self.grid[grid_row2][grid_col2][0] != AIR:
            self.canvas.create_rectangle(canvas_x2, canvas_y2, canvas_x2 + self.cell_size, canvas_y2 + self.cell_size, fill=self.grid[grid_row2][grid_col2][1], outline="")
        
        
        self.debug_logger(debug_temp_index, "ended swap_particles()")

    def draw_particle(self):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started draw_particles()")
        if self.drawing:
            # draw the sand particle when the event is triggered
            column  = self.mouse_position[0] // self.cell_size
            row     = self.mouse_position[1] // self.cell_size

            # Checks to see if in the bounds of the canvas
            if 0 <= row < self.rows and 0 <= column < self.columns:
                if self.current_particle == SAND: # If current particle is SAND
                    self.grid[row][column] = (SAND, self.vary_color(SAND_COLOR))
                elif self.current_particle == WATER: # If current particle is WATER
                    self.grid[row][column] = (WATER, self.vary_color(WATER_COLOR))
                elif self.current_particle == STONE:
                    self.swap_particles((row,column),(row,column))
                    self.grid[row][column] = (STONE, self.vary_color(STONE_COLOR))
                elif self.current_particle == WOOD:
                    self.grid[row][column] = (WOOD, self.vary_color(WOOD_COLOR))
                    self.swap_particles((row,column),(row,column))
                elif self.current_particle == AIR:
                    self.grid[row][column] = (AIR, AIR_COLOR)
                    self.swap_particles((row,column),(row,column))
            self.root.after_idle(self.draw_particle)
        self.debug_logger(debug_temp_index, "ended draw_particles()")
    
    def update_sand(self, sand_location):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "update_sand()")
        # If we're at the bottom of the grid, stay in place
        row, column = sand_location
        # Are we at the bottom of the grid?
        if row == self.rows - 1:
            return
        
        particle_below = self.grid[row+1][column][0]
        # Is the particle below us AIR or WATER?
        if particle_below in {AIR, WATER}:
            # TODO: Change this so it isn't just a swap
            # straight water float can just parse the grid upward(and checking it's neighbors) until if finds an AIR tile and move the water to that instead of swapping with the sand
            self.swap_particles(sand_location, (row+1,column))
            return
        else:
            # pick a random direction
            direction = choice([-1, 0, 1])
            # Is that in-bounds
            if direction !=0 and 0 <= column + direction < self.columns:
                particle_diagonal = self.grid[row+1][column+direction][0]
                # is the particle diagonally below us AIR or WATER?
                if particle_diagonal in {AIR, WATER}:
                    # TODO: Change this so it isn't just a swap when dealing with WATER
                    # Diagonal water float can probably just parse the grid directly up for an AIR tile to move the water particle to
                    # maybe more realistically we can have the water particle "push" it's neighbors to create a similar effect
                    self.swap_particles(sand_location, (row+1,column+direction))
                    return
                # if the particle is not AIR or WATER, stay in place
                return
            # if out of bounds, stay in place
            return
    
        print("Update_sand(): Something went wrong, you shouldn't be able to reach this point")

    def update_water(self, water_location):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index,"update_water()")
        row, column = water_location
        
        # Are we at the bottom of the grid?
        if row == self.rows -1:
            # pick a random direction
            direction = choice([-1,1])
            # is that in-bounds?
            if direction != 0 and 0 <= column + direction < self.columns:
                # is the particle to that direction AIR?
                if self.grid[row][column+direction][0] == AIR:
                    self.swap_particles(water_location, (row,column+direction))
                    return
                # if it's not AIR, stay in place
                return
            # if out of bounds, stay in place
            return
        
        # Is there empty space below us?
        if self.grid[row+1][column][0] == AIR:
            self.swap_particles(water_location, (row+1,column))
            return
        # is there something below us?
        else:
            # pick a random direction
            direction = choice([-1,1])
            # is that in-bounds?
            if direction != 0 and 0 <= column + direction < self.columns:
                # is the particle to that direction AIR?
                if self.grid[row][column+direction][0] == AIR:
                    # move to that spot
                    self.swap_particles(water_location, (row,column+direction))
                    return
                # if it's not AIR, stay in place
                return
            # if out of bounds, stay in place
            return
        
        print("Update_water(): Something went wrong, you shouldn't be able to reach this point")

    def update_particle(self):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started update_particle()")
        # parse through the entire grid
        for row in range(self.rows - 1, -1, -1): # parse from down to up
            for column in range(self.columns): # parse from left to right
                particle_type = self.grid[row][column][0]
                # SAND
                if particle_type == SAND:
                    self.update_sand((row, column))
                #WATER
                elif particle_type == WATER:
                    self.update_water((row, column))
                # STONE
                elif particle_type == STONE:
                    # STONE does not move once placed
                    pass
                # WOOD
                elif particle_type == WOOD:
                    # WOOD does not move once placed
                    pass
                elif particle_type == AIR:
                    # AIR does not move once placed
                    pass
                else:
                    print("Update_particle(): Something went wrong, you shouldn't be able to reach this point")
        
        self.root.after(1, self.update_particle)
        self.debug_logger(debug_temp_index, "ended update_particle()")

    def set_particle(self, value):
        debug_temp_index = self.debug_index
        self.debug_index += 1
        self.debug_logger(debug_temp_index, "started set_particle()")
        self.current_particle = value
        self.debug_logger(debug_temp_index, "ended set_particle()")
    
    def reset_scene(self):
        #self.debug_logger("reset_scene()")
        self.grid.fill((AIR,AIR_COLOR))
        self.canvas.delete("all")

    def save_scene(self, filename):
        #self.debug_logger("save_scene()")
        with open(filename, 'wb') as file:
            pickle.dump(self.grid, file)

    def load_scene(self, filename):
        #self.debug_logger("load_scene()")
        with open(filename, 'rb') as file:
            self.grid = pickle.load(file)

    def save_scene_dialog(self):
        #self.debug_logger("save_scene_dialog()")
        filename = filedialog.asksaveasfilename(defaultextension=".sand")
        if filename:
            self.save_scene(filename)
    
    def load_scene_dialog(self):
        #self.debug_logger("load_scene_dialog()")
        filename = filedialog.askopenfilename(filetypes=[("Sand Simulator Scenes", "*.sand")])
        if filename:
            self.load_scene(filename)

    def particle_info_window(self):
        #self.debug_logger("particle_info_window()")
        particle_info_window = tk.Toplevel(self.root)
        ParticleInfoWindow(particle_info_window)

    def build_menu(self):
        #self.debug_logger("build_menu()")
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
        particle_menu.add_radiobutton(label="Wood", command=lambda: self.set_particle(WOOD))
        particle_menu.add_radiobutton(label="Erase", command=lambda: self.set_particle(AIR))
        menu_bar.add_cascade(label="Particles", menu=particle_menu)
        
        info_menu = tk.Menu(menu_bar, tearoff=0)
        info_menu.add_command(label="Particle Info", command=self.particle_info_window)
        info_menu.add_command(label="About...")
        menu_bar.add_cascade(label="Help", menu=info_menu)
        
        self.root.config(menu=menu_bar)
    
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    window_width, window_height = 800,600
    cell_size = 10
    target_fps = 60
    application_title = "Python Sand Simulator"
    debug = False
    root = tk.Tk()
    app = FallingSand(root, application_title, window_width, window_height, cell_size, target_fps, debug)
    app.run()

    