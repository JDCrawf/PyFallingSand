# PyFallingSand

<!-- TODO: Create an animated gif of the project running -->
![Falling Sand Demo](img)

## Overview

This is a simple simulation application built with Python and the NumPy and Tkinter libraries that allows users to interactively create and observe the behavior of falling sand particles within a 2D grid.

This project is an educational practice with Cellular Automata to experiement with particle simulations

## Features

- Draw sand particles by clicking and dragging the left mouse button.
- Simulate the falling of sand particles under the influence of gravity.
- Sand particles slide down to the side of a slope if the grid location down one and one to the left or right is empty.

	### Planned Features

	- Adding mroe particle types that behave differently
	- The ability to change which particle you are drawing with
	- Particle interactions
		- Sand sinks in water
		- Water douses fire
		- Fire burns plants
		- etc...

## Requirements

Make sure you have the following dependencies installed before running the application:
- Python 3.X
- tkinter 8.X (install using `pip install tk`)
- numpy 1.26.X (install using `pip install numpy`)

## Usage

1. Clone the repository:

	```bash
	git clone https://github.com/JDCrawf/PyFallingSand.git
	```

2. Navigate to the project directory:

	```bash
	cd PyFallingSand
	```

3. Launch the PyFallingSand application

    ```bash
    py falling-sand.py
    ```

4. Click and drag the left mouse button to draw sand particles and watch as the particles fall and interact with each other.

## Configuration

Adjust the following parameters in the `if __name__ == '__main__:` section at the bottom of the falling-sand.py file to customize the simulation:

<!-- TODO: Add more details about the configuration options and more configuration options -->
    window_width, window_height = 600,500
    cell_size = 50
	target_fps = 30
    

## Contributing

If you would like to contribute to this project, feel free to fork the repository and submit a pull request. Any contributions are welcome and accepted push requests will get your name added to this list!

Jacob Crawford - [@JDCrawf](https://github.com/JDCrawf)

## License

- This project is licensed under the [MIT License](LICENSE).
- Tkinter: Python Software Foundation License (included with Python installations).
- Numpy: Modified BSD License.  See [NumPy License](https://github.com/numpy/numpy/blob/main/LICENSE.txt) for details

## Acknowledgments

- Thanks to the Tkinter communities for providing excellent libraries and resources.
