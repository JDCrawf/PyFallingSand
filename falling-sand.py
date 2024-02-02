import tkinter as tk
from random import choice, random

'''
    Here is basic idea
    Cellular automata
    Create a 2d grid in a tkinter window
    each grid location holds a value if there is a sand located there or not(0 or 1)
    each step, check if the spot below a sand is empty,
        if so move the sand to that empty spot
    else if the spot is not empty, check the down1/left1 or down1/right1 locations to see if either of them is empty,
        if so then move the sand to that spot
    make sure to constrain checking to within the grid
    and have the sand stop moving when it reaches an edge of the grid
    
    after the basic foundation is made we can work on extra features
        maybe add different rules for interactions
            i.e. sand/water fall, stone/wood stays in place, fire burns wood then fades, water dowses fire, etc...44
'''
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
        self.rows = height // cell_size
        self.columns = width // cell_size
        self.grid =  [[0 for _ in range(self.columns)] for _ in range(self.rows)] 
        
        # Canvas Variables
        self.canvas_width = width
        self.canvas_height = height
        self.cell_size = cell_size
    
    def build_menu(self):
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
    cell_size = 50
    applicaiton_title = "Python Sand Simulator"
    root = tk.Tk()
    app = FallingSand(root, applicaiton_title, window_width, window_height, cell_size)
    app.run()