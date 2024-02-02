import tkinter as tk
import random

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
# Base window Variables
window_width = 600
window_height = 500
window_title = "Python Falling Sand"

# Simulation variables

# Initialize the window
root = tk.Tk()
root.title(window_title)
root.geometry(f"{window_width}x{window_height}")
root.resizable(True, True)











if __name__ == '__main__':
    root.mainloop()