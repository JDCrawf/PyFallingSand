import tkinter as tk
from random import choice, random

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
        
        # Canvas Variables
        self.canvas_width   = width
        self.canvas_height  = height
        self.cell_size      = cell_size
        
        self.canvas = tk.Canvas(root, width=width, height=height, bg="white")
        self.canvas.pack()
        
        # Draw and update the sand particles
        self.canvas.bind("<Button-1>", self.draw_sand) # draw a sand particle when the "Button-1" event happens with the self.draw_sand function
        self.canvas.bind("<B1-Motion>", self.draw_sand)
        
    def draw_sand(self, event):
        # draw the sand particle when the event is triggered
        row     = event.y // self.cell_size
        column  = event.x // self.cell_size
        
        # Checks to see if in the bounds of the canvas
        if 0 <= row < self.rows and 0 <= column <= self.columns:
            self.grid[row][column] = 1
            self.update_canvas()
    
    def update_canvas(self):
        self.canvas.delete("all")
        for row in range(self.rows):
            for column in range(self.columns):
                if self.grid[row][column] == 1:
                    x = column * self.cell_size
                    y = row * self.cell_size
                    self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill="black", outline="")
    
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
    cell_size = 10
    applicaiton_title = "Python Sand Simulator"
    root = tk.Tk()
    app = FallingSand(root, applicaiton_title, window_width, window_height, cell_size)
    app.run()