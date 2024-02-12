import tkinter as tk            # Creates tkinter windows
from tkinter import filedialog  # Save/load tkinter interfaces
import pickle                   # allows saving and loading of files
import numpy as np              # easy array interface
from random import choice       # for particle physics
import time

AIR = 0     # Empty tile
STONE = 1   # stationary and indestructible
SAND = 2    # falls down and piles up, heavier than water
WATER = 3   # falls down and spreads out
WOOD = 4    # stationary but flammable
FIRE = 5    # spreads onto flammable particles

# element colors
# https://www.plus2net.com/python/tkinter-colors.php
AIR_COLOR = "#FAEBD7" # antiquewhite note: we should never actually be drawing AIR rectangles, this is just for the canvas background really
STONE_COLOR = "#808A87" # coldgrey
WOOD_COLOR = "#8B4513" # chocolate
SAND_COLOR = "#F4A460" # saddlebrown
WATER_COLOR = "#7FFFD4" # aquamarine1
FIRE_COLOR = "#FF6103" #cadmiumorange

# Create the info window with information about the different particles
class ParticleInfoWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Particle Info")

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
        }# Empty entry is because the anchor="nw" isn't being applied to the last created label for some reason
        # parse through particle_info and populate a grid with tk.Label objects
        for index, (particle, description) in enumerate(particle_info.items()):
            particle_name = tk.Label(self.info_frame, text=particle, bd=1, relief=tk.SUNKEN, padx=5, pady=5)
            particle_name.grid(row=index, column=1, sticky="nsew")
            
            particle_description = tk.Label(self.info_frame, text=description, bd=1, relief=tk.SUNKEN, anchor="nw", padx=10, pady=5)
            particle_description.grid(row=index, column=2, sticky="nsew")

class FallingSand:
    def __init__(self, root, title, width, height, cell_size):
        # Tk window variables
        self.root = root
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False,False)
        
        # Debug settings
        self.debug_log = "DEBUG LOG\n\n"
        self.debug_time = time.time()

        # Particle settings
        self.current_particle = SAND
        
        # Simulation Variables
        self.columns = width // cell_size  # x
        self.rows    = height // cell_size # y
        # Creates a grid of size [rows][columns] filled with tuples that contain (int, 7 character string).  The string is 7characters since it should only be a hex value starting with '#'
        self.particle_grid = np.zeros((self.rows, self.columns), dtype=[('particle_type', int),('particle_color','U7')])
        # Fill the grid with default value of AIR. AIR_COLOR is probably not needed
        self.particle_grid.fill((AIR,AIR_COLOR))
        self.buffer_grid = np.copy(self.particle_grid)
        self.updated_particles = []
        
        # Canvas Variables
        self.canvas_width   = width
        self.canvas_height  = height
        self.cell_size      = cell_size

        # Mouse Variables
        self.mouse_down     = False
        self.mouse_position = (0,0)
        
        #self.root.protocol("WM_DELETE_WINDOW", self.debug_on_closing)
        
        # Create the canvas to display the simulation
        self.canvas = tk.Canvas(root, width=width, height=height, bg=AIR_COLOR)
        self.canvas.pack()
        
        # Draw and update the sand particles
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down) # start drawing sand when mouse is pressed down
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up) # stop drawing sand when mouse is released
        self.canvas.bind("<Motion>", self.track_mouse) # update the current mouse position in relation to the canvas

        # Create the menu bar at the top of the window
        self.build_menu()

        self.root.after(0, self.update_canvas)

    # Debug methods
    def debug_on_closing(self):
        with open("./bin/debug_log.txt", "wb") as file:
            pickle.dump(self.debug_log, file)
        self.root.quit()
    def debug_log_message(self, message):
        current_time = time.time()
        self.debug_log += f"{message} took {(current_time-self.debug_time):3f}milliseconds\n"
        self.debug_time = time.time()


    # Mouse control methods
    def on_mouse_down(self, event):
        '''
        Called when the mouse button1 is pressed
        Sets the mouse_down boolean to true and calls the draw_particle method
        '''
        self.mouse_down = True
        self.place_particle()
    def on_mouse_up(self, event):
        '''
        Called when the mouse button1 is released
        Sets the mouse_down boolean to false
        '''
        self.mouse_down = False
    def track_mouse(self, event):
        '''
        Called when the mouse/cursor is moved
        Updates the cursor position in relation to the grid
        '''
        #if self.mouse_down:
            #(row,column) <=> (y, x)
        self.mouse_position = (event.y // self.cell_size, event.x // self.cell_size)

    # Saving/Loading methods
    def save_scene(self, path):
        '''
        Saves the current particle_grid to the specified path

        Args:
            path (str): The [relative/absolute] path where to save the .sand file to
        '''
        with open(path, 'wb') as file:
            pickle.dump(self.particle_grid, file)
    def load_scene(self, path):
        '''
        Loads the file at the specified path and dumps it into the particle_grid
        
        Args:
            path (str): The [absolute/relative] path to the .sand file to be loaded
        '''
        with open(path, 'rb') as file:
            self.particle_grid = pickle.load(file)

    # Save/Load dialog windows
    def save_dialog(self):
        '''
        Creates a save dialog window
        Opens a file dialog to set the path for the current scene to be saved as
        '''
        filename = filedialog.asksaveasfilename(defaultextension=".sand")
        if filename:
            self.save_scene(filename)
    def load_dialog(self):
        '''
        Creates a load dialog window
        Opens a file dialog to retrieve the path to a scene to be loaded from
        '''
        filename = filedialog.askopenfilename(filetypes=[("PyFallingSand Scenes", "*.sand")])
        if filename:
            self.load_scene(filename)

    # Helper methods
    def vary_color(self, color):
        '''
        Takes a hex color string and returns a slightly varied hex string
        
        Args:
            color (str): A 7 character hex color string "#RRBBGG"
        
        Returns:
            varied_color (str): A 7 character hex color string
        '''
        hex_range = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        varied_color = f"#{color[1]}{choice(hex_range)}{color[3]}{choice(hex_range)}{color[5]}{choice(hex_range)}"
        return varied_color

    # Particle methods
    def swap_particles(self, particle_1, particle_2):
        '''
        Swap the particles at the input grid location tuples

        Args:
            particle_1 (int, int): Tuple of integers representing the row and column of a particle to be swapped
            particle_2 (int, int): Tuple of integers representing the row and column of a particle to be swapped
        '''
        p1_row, p1_column = particle_1
        p2_row, p2_column = particle_2

        # create a copy of particle_1
        # move particle_2 to particle_1's location
        # move the copy of particle_1 to particle_2's location
        temp = tuple(self.particle_grid[p1_row, p1_column])
        self.particle_grid[p1_row, p1_column] = self.particle_grid[p2_row, p2_column]
        self.particle_grid[p2_row, p2_column] = temp
        self.updated_particles.append((p1_row, p1_column))
        self.updated_particles.append((p2_row, p2_column))
    def update_sand(self, sand_location):
        '''
        The update logic for sand particles

        Args:
            sand_location (int,int): A tuple containing the grid location of the sand particle
        '''
        row, column = sand_location

        # if the particle is at the bottom of the grid(or somehow past it)
        if row >= self.rows-1:
            # do nothing
            self.updated_particles.remove(sand_location)
            return

        # Identify the particle below our sand location
        particle_below = self.particle_grid[row+1][column][0]
        # Is particle_below AIR or WATER?
        if particle_below in {AIR, WATER}:
            # Swap the sand particle to that location
            # TODO: I want better logic for WATER particles
            #       Maybe instead of raw swapping, I could have the particle "push" other water particles upward to make room for the sand
            self.swap_particles(sand_location, (row+1, column))
            return
        # If the particle is not AIR or WATER

        # pick a random direction
        direction = choice([-1,0,1])
        # if that direction isn't in bounds or if direction is 0
        if not (0 <= column + direction < self.columns) or direction == 0:
            # do nothing
            return
        # else that direction is in bounds
        
        # Is the particle diagonally down in that direction AIR or WATER?
        particle_diagonal = self.particle_grid[row+1][column+direction][0]
        if particle_diagonal in {AIR, WATER}:
            # Swap the sand particle to that location
            # TODO: I want better logic for WATER particles
            self.swap_particles(sand_location, (row+1, column+direction))
            #return
        # if you've reached here, then do nothing
        self.updated_particles.remove(sand_location)
    def update_water(self, water_location):
        '''
        The update logic for water particles

        Args:
            water_location (int,int): A tuple containing the grid location of the water particle
        '''
        row, column = water_location

        # if the particle is at the bottom of the grid(or somehow past it)
        if row >= self.rows-1:
            # move in a random direction, if able
            print("WATER at bottom")
            self.updated_particles.remove(water_location)
            return
        # else that particle is not at the bottom of the grid

        # Identify the particle below our location
        # Is particle_below AIR?
        if self.particle_grid[row+1][column][0] == AIR:
            # Swap the water particle to that location
            self.swap_particles(water_location, (row+1, column))
            return
        # else the particle_below is not AIR

        # move in a random direction, if able
        # pick a random direction
        direction = choice([-1,1])
        # is that direction out of bounds or 0?
        if not (0 <= column+direction < self.columns):
            # do nothing
            return
        # else that direction is in bounds and not 0

        # Is the particle in the direction AIR?
        if self.particle_grid[row][column+direction][0] == AIR:
            # Swap the water particle to that location
            self.swap_particles(water_location, (row, column+direction))
            #return
        # if you've reached here, then do nothing
        print("WATER blocked on both sides")
        self.updated_particles.remove(water_location)
    def update_particles(self):
        '''
        The update logic for all particle types
        '''
        print("update particles")
        for column in range(self.columns):
            for row in range(self.rows-1, -1, -1):
                if (row, column) in self.updated_particles:
                    particle_type = self.particle_grid[row][column][0]
                    if particle_type == SAND:
                        self.update_sand((row, column))
                    elif particle_type == WATER:
                        self.update_water((row, column))
                    elif particle_type in {STONE, WOOD, AIR}:
                        continue
                    else:
                        print(f"Error: update_particles() - Invalid particle type: {particle_type}")       
    def place_particle(self):
        '''
        References the mouse location to place a particle in the corresponding grid location
        '''
        # is button1 on the mouse is not pressed?
        if not self.mouse_down:
            # do nothing
            return
        # else button1 is pressed down

        row, column = self.mouse_position
        # is the mouse within the bounds of the grid?
        if 0 <= row < self.rows and 0 <= column < self.columns:
        
        # TODO: decide if I want to let particles replace existing particles
        #    # is there a particle already in that grid location?
        #    if self.particle_grid[row][column][0] != AIR:
        #        # do nothing
        #        return
        #    # else the particle is not in that grid location
        #   else:
            # Define a dictionary mapping particle types to colors
            particle_colors = {
                SAND: self.vary_color(SAND_COLOR),
                WATER: self.vary_color(WATER_COLOR),
                STONE: STONE_COLOR,
                WOOD: self.vary_color(WOOD_COLOR),
                AIR: AIR_COLOR
            }

            # Get color based on current particle type
            particle_color = particle_colors.get(self.current_particle)

            # If somehow the self.current_particle does not correspond to an entry in the particle_colors dictionary
            if particle_color is None:
                print(f"Error: place_particles() -Invalid particle type: {self.current_particle}")
                return

            # Update particle grid and draw the new particle
            self.particle_grid[row][column] = (self.current_particle, particle_color)
            # mark the particle as updated and draw the initial particle
            self.updated_particles.append((row, column))
            self.draw_particle((row, column))

    # Canvas Methods
    def draw_particle(self, location):
        '''
        Draws the particle at the given location
        '''
        row, column = location
        particle_type, particle_color = self.particle_grid[row][column]

        canvas_x = column * self.cell_size
        canvas_y = row * self.cell_size

        # delete any rectangles that are at the specified location
        for rect in self.canvas.find_overlapping(canvas_x+1, canvas_y+1, canvas_x+2, canvas_y+2):
            self.canvas.delete(rect)
        
        # if the grid at that location is air
        if particle_type == AIR:
            # do nothing
            return
        # else the particle at that location isn't air

        # draw the new rectangle
        self.canvas.create_rectangle(canvas_x, canvas_y, canvas_x+self.cell_size, canvas_y+self.cell_size, fill=particle_color, outline="")
    def update_canvas(self):
        '''
        Each step update the particles that have changed between updates
        '''
        self.update_particles()

        # only update the particles that have been flagged as changed
        for row, column in self.updated_particles:
            self.draw_particle((row, column))
        #self.updated_particles.clear()

        root.after(5, self.update_canvas) # calls itself every second(1000ms)

    # Menu methods
    def particle_info_window(self):
        '''
        Creates the information window describing the different particles
        '''
        particle_info_window = tk.Toplevel(self.root)
        ParticleInfoWindow(particle_info_window)
    def reset_simulation(self):
        '''
        Resets the particle simulation by erasing the contents of the particle_grid and clearing the canvas
        '''
        self.particle_grid.fill((AIR,AIR_COLOR))
        self.canvas.delete("all")
    def set_particle(self, particle):
        '''
        Sets the current particle for the draw_particle method
        
        Args:
            particle (int): A integer value representing a specific type of particle
        '''
        self.current_particle = particle
    def build_menu(self):
        '''
        Builds the tkinter menu bar
        '''
        menu_bar = tk.Menu(self.root, tearoff=0)
        
        # File menu
        # Creates a dropdown menu that lets you reset, save, or load the simulation
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Scene (Ctrl + N)", command=self.reset_simulation)
        file_menu.add_command(label="Open Scene (Ctrl + O)", command=self.load_dialog)
        file_menu.add_command(label="Save Scene (Ctrl + S)", command=self.save_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Particle menu
        # Creates a dropdown menu that lets you select which particle you are drawing with
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
    application_title = "Python Sand Simulator"
    root = tk.Tk()
    app = FallingSand(root, application_title, window_width, window_height, cell_size)
    app.run()