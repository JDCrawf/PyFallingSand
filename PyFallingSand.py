import tkinter as tk              # Creates tkinter windows
from tkinter import filedialog    # Save/load tkinter interfaces
import pickle                     # allows saving and loading of files
import os                         # for checking and creating save directory
import numpy as np                # easy array interface
from random import choice, random # for choosing random directions/chances
import time                       # used for debugging and capping FPS

AIR    = 0 # Empty tile
STONE  = 1 # stationary and indestructible
SAND   = 2 # falls down and piles up, heavier than water
WATER  = 3 # falls down and spreads out
WOOD   = 4 # stationary but flammable
FIRE   = 5 # spreads onto flammable particles, produces smoke
SMOKE  = 6 # floats upward drifting to the sides before disappearing
OIL    = 7 # flammable liquid that is lighter than water

# constants for search_adjacent
UP   = -1
DOWN = 1

# Defining the cardinal directions in relation to grid coordinates
NORTH = ( 0, -1)
EAST  = ( 1,  0)
SOUTH = ( 0,  1)
WEST  = (-1,  0)

# particle colors
# https://www.plus2net.com/python/tkinter-colors.php
particle_colors = {
    AIR  : "#FAEBD7", # antiquewhite
    STONE: "#808A87", # coldgray
    WOOD : "#8B4513", # chocolate
    SAND : "#F4A460", # saddlebrown
    WATER: "#7FFFD4", # aquamarine1
    FIRE : "#FF6103", # cadmiumorange
    SMOKE: "#A9A9A9", # darkgray
}

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

        # Set up directory for saving files
        self.save_directory = "./bin/saves"
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
        
        # Debug settings
        self.debug_log = "DEBUG LOG\n\n"
        self.debug_time = time.time()

        # Particle settings
        self.current_particle = SAND
        
        # Simulation Variables
        self.cell_size = cell_size
        self.canvas_width   = width
        self.canvas_height  = height
        self.columns   = width // cell_size  # x
        self.rows      = height // cell_size # y
        # Creates a grid of size [rows][columns] filled with tuples that contain (int, 7 character string).  The string is 7characters since it should only be a hex value starting with '#'
        self.particle_grid = np.zeros((self.rows, self.columns), dtype=[('particle_type', int),('particle_color','U7')])
        # Fill the grid with default value of AIR. AIR_COLOR is probably not needed
        self.particle_grid.fill((AIR,None))
        self.next_grid = np.zeros((self.rows, self.columns), dtype=[('particle_type', int),('particle_color','U7')])
        self.next_grid.fill((AIR,None))
        self.updated_particles = []
        # SIMULATION - Particle traits
        self.flammable_particles = [WOOD]
        self.grain_particles     = [SAND]
        self.liquid_particles    = [WATER, OIL]
        self.gaseous_particles   = [AIR, SMOKE]
        self.stationary_particles= [STONE, WOOD]
        self.special_particles   = [FIRE]
        self.particle_weights   = { # Only need weights for movable particles
            AIR  : 0,
            SAND : 5,
            WATER: 4,
            OIL  : 3,
            SMOKE: -1
        }
        # SIMULATION - Fire variable
        self.fire_consumption_rate = 0.1 # this can be modified depending on the flammable material type(i.e. oil burns faster than water)
        self.smoke_production_rate = 0.1
        
        self.particle_actions = {
            SAND: self.update_sand,
            WATER: self.update_water,
            FIRE: self.update_fire,
            SMOKE: self.update_smoke
        }
        
        # Mouse Variables
        self.mouse_down     = False
        self.mouse_position = (0,0)
        
        #self.root.protocol("WM_DELETE_WINDOW", self.debug_on_closing)
        
        # Create the canvas to display the simulation
        self.canvas = tk.Canvas(root, width=width, height=height, bg=particle_colors.get(AIR))
        self.canvas.pack(fill="both", expand=True)
        
        # Binding mouse events for drawing control
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down) # start drawing sand when mouse is pressed down
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up) # stop drawing sand when mouse is released
        self.canvas.bind("<Motion>", self.track_mouse) # update the current mouse position in relation to the canvas

        # Start the animation loop
        self.root.after_idle(self.update_canvas)

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
        self.mouse_position = (event.y // self.cell_size - 1, event.x // self.cell_size)

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
        filename = filedialog.asksaveasfilename(initialdir=self.save_directory, initialfile="scene", defaultextension=".sand")
        if filename:
            self.save_scene(filename)
    def load_dialog(self):
        '''
        Creates a load dialog window
        Opens a file dialog to retrieve the path to a scene to be loaded from
        '''
        filename = filedialog.askopenfilename(initialdir=self.save_directory, filetypes=[("PyFallingSand Scenes", "*.sand")])
        if filename:
            self.load_scene(filename)
        
        # redraw the entire canvas
        for row in range(self.rows):
            for column in range(self.columns):
                self.updated_particles.append((row,column))

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
    def find_adjacent(self, location, target_list, direction=0, distance=1):
        '''
        Search the tiles adjacent to the given location for target particle types

        Args:
            location (int,int): A tuple containing the grid location of the calling particle
            target_list (list): A list of particles to be searching for
            direction    (int): The direction this should look in(-1 is at level and above, 1 is at level and below, 0 is all around). Defaults to 0
            distance     (int): The distance away from the particle to check.  Defaults to 1
        '''
        row, column = location
        results_list = []
        # parse through the grid locations adjacent to the given location
        row_range = range(-distance, distance) if direction == 0 else range(0, distance) if direction == DOWN else range(-distance, 0)
        for adjacent_row in row_range:
            for adjacent_column in [-distance,0,distance]:
                # skip yourself
                if adjacent_row == adjacent_column == 0:
                    continue

                check_row, check_column = row + adjacent_row, column + adjacent_column
                # is check_row and check_column out of bounds?
                if not (0 <= check_row < self.rows and 0 <= check_column < self.columns):
                    # do nothing
                    continue
                # else check_row and check_column are in bounds

                # what particle is there?
                particle_type = self.particle_grid[check_row][check_column][0]
                # is the particle one of the flammable particle types?
                if particle_type in target_list:
                    results_list.append((row,column))
                # else its not the target particle so check the next location
        
        return results_list

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
        temp = tuple(self.particle_grid[p1_row][p1_column])
        self.particle_grid[p1_row][p1_column] = self.particle_grid[p2_row][p2_column]
        self.particle_grid[p2_row][p2_column] = temp

        # Add the particles to the updated_particles array if they're not already there
        if (p1_row, p1_column) not in self.updated_particles:
            self.updated_particles.append((p1_row, p1_column))
        if (p2_row, p2_column) not in self.updated_particles:
            self.updated_particles.append((p2_row, p2_column))
    def update_fire(self, fire_location):
        '''
        Update the logic for fire particles

        Args:
            fire_location (int,int): A tuple containing the grid location of the fire particle
        '''
        row, column = fire_location
        
        # If there is not both flammable particles and AIR adjacent to the fire_location
        adjacent_flammable = self.find_any_adjacent(fire_location, self.flammable_particles)
        adjacent_air       = self.find_any_adjacent(fire_location, [AIR])
        if not (adjacent_flammable != False and adjacent_air != False):
            # kill the FIRE particle and return
            self.particle_grid[row][column] = (AIR,particle_colors[AIR])
            self.updated_particles.append((row,column))
            return
        # else there is a flammable particle particle and AIR adjacent to the location

        # does the FIRE consume the flammable particle(spread) this step?
        particle_consumed = random() < self.fire_consumption_rate
        # if random chance decided the particle is consumed
        if particle_consumed:
            # turn the particle into a FIRE particle
            consumed_row, consumed_column = adjacent_flammable
            self.particle_grid[consumed_row][consumed_column] = (FIRE, particle_colors[FIRE])
            self.updated_particles.append(adjacent_flammable)
        # else the particle was not consumed this step

        # does the FIRE produce SMOKE this step?
        smoke_produced = random() < self.smoke_production_rate
        smoke_produced = False
        # if random chance decided the particle is produced
        if smoke_produced:
            # turn the particle into a SMOKE particle
            produced_row, produced_column = adjacent_air
            self.particle_grid[produced_row][produced_column] = (SMOKE, self.vary_color(particle_colors[SMOKE]))
        # else smoke wasn't produced this step
        
        # if you've reached here, then do nothing
    def update_gaseous(self, location):
        '''
        Update the logic for gaseous particles

        Args:
            location (int,int): A tuple containing the grid location of the particle
        '''
        row, column = location

        # pick a random direction NSEW
        direction = choice([NORTH, EAST, SOUTH, WEST])
        target_row = row + direction[0]
        target_column = column + direction[1]

        # is the direction out of bounds?
        if not (0 <= target_row < self.rows and 0 <= target_column < self.columns):
            # do nothing
            return
        # else that direction is in bounds

        # is the particle in that direction NOT gaseous(gas won't swap with solid or liquids)
        if self.particle_grid[target_row][target_column][0] not in self.gaseous_particles:
            # do nothing
            return
        # else the particle is gaseous

        # is the particle moving up
        if direction == NORTH:
            # if north, swap if the particle is lighter than the target particle

            pass
        # else the particle is moving down
        elif direction == SOUTH:
            # if south, swap if the particle is heavier than the target particle
            pass
        # else the particle is moving left/right
        else:
            # if left/right, swap if the particle is not the same type of particle
            pass
    def update_liquid(self, location):
        '''
        Update the logic for liquid particles

        Args:
            location (int,int): A tuple containing the grid location of the particle
        '''
        row, column = location

        # is it the bottom of the grid
            # do nothing
        # else its not at the bottom of the grid

        # is the particle below lighter?
            # swap
        # else the particle is heavier

        # pick a random direction EW
        direction = choice([EAST, WEST])
        target_row, target_column = row + direction[0], column + direction[1]
        # is the particle in that direction lighter?
            # swap
        # else the particle is heavier

        # if you reached here do nothing

    def update_grain(self, location):
        '''
        Update the logic for grain particles

        Args:
            location (int,int): A tuple containing the grid location of the particle
        '''
        row, column = location

        # is it at the bottom of the grid?
            # do nothing
        # else we are not at the bottom

        # is there free space below it?
            # move down
        # else there is something below it

        # pick a random direction
        direction = choice([EAST, WEST])
        target_row, target_column = row + direction[0], column + direction[1]
        # is there free space in the direction and the diagonal direction?
            # move down
        pass

    def update_particles(self):
        '''
        The update logic for all particle types
        '''
        # TODO: change this to use the next_grid
        # each time the updates happen, apply them to the next_grid instead
        # after parsing through the entire grid, if it's different than the old grid, overwrite the old with the next one, then redraw
        for column in range(self.columns):
            for row in range(self.rows-1, -1, -1):
                particle_type = self.particle_grid[row][column][0]
                if particle_type in self.particle_actions:
                    self.particle_actions[particle_type]((row, column))
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
        # is the mouse is out of bounds of the grid?
        if not (0 <= row < self.rows and 0 <= column < self.columns):
            # do nothing
            pass
        else:
            # Get color based on current particle type
            particle_color = particle_colors.get(self.current_particle)

            # If somehow the self.current_particle does not correspond to an entry in the particle_colors dictionary
            if particle_color is None:
                print(f"Error: place_particle() -Invalid particle type: {self.current_particle}")
                return

            # Update particle grid and draw the new particle
            self.particle_grid[row][column] = (self.current_particle, particle_color)
            # mark the particle as updated and draw the initial particle
            if (row, column) not in self.updated_particles:
                self.updated_particles.append((row, column))
            #self.draw_particle((row, column))
        self.root.after(1, self.place_particle)

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
        #self.updated_particles.remove(location)
    def update_canvas(self):
        '''
        Each step update the particles that have changed between updates
        '''
        self.update_particles()
        #self.canvas.delete("all")
        # only update the particles that have been flagged as changed
        for row, column in self.updated_particles:
            self.draw_particle((row, column))
        self.updated_particles.clear()

        root.after(5, self.update_canvas) # calls itself every X milliseconds(1000ms = 1s)

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
        particle_menu.add_radiobutton(label="Fire", command=lambda: self.set_particle(FIRE))
        particle_menu.add_radiobutton(label="Erase", command=lambda: self.set_particle(AIR))
        menu_bar.add_cascade(label="Particles", menu=particle_menu)
        
        info_menu = tk.Menu(menu_bar, tearoff=0)
        info_menu.add_command(label="Particle Info", command=self.particle_info_window)
        info_menu.add_command(label="About...")
        menu_bar.add_cascade(label="Help", menu=info_menu)
        
        self.root.config(menu=menu_bar)

    def run(self):
        # Create the menu bar at the top of the window
        self.build_menu()
        self.root.mainloop()

if __name__ == '__main__':
    window_width, window_height = 800,600
    cell_size = 10
    application_title = "Python Sand Simulator"
    root = tk.Tk()
    app = FallingSand(root, application_title, window_width, window_height, cell_size)
    app.run()