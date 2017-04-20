Cell Matrix - Implementation of Conway's Game of Life Algorithm

Project site:
http://gatc.ca/projects/cell-matrix/


Dependencies:
Python 2.7+ (https://www.python.org/)
Pygame 1.9.1 (https://www.pygame.org/)

Usage:
Interphase module (http://gatc.ca/projects/interphase/)
>GUI interface module.
PyJ2D 0.27_dev (http://gatc.ca/projects/pyj2d/) / Jython 2.2.1+ (http://www.jython.org/)
>Optional to port Pygame app to Java environment of JVM 6.0+ (https://www.java.com).
Pyjsdl 0.21_dev (http://gatc.ca/projects/pyjsdl/) / Pyjs 0.8.1_dev (http://www.pyjs.org/)
>Optional to port Pygame app to JS environment of Web browser.


Instructions:
Cell Matrix runs with Python and the Pygame library. Input of Game of Life patterns can be done from the interface panel by the controls LOAD from a customized pattern.txt file and GET from the system clipboard. The app is run with the command 'python cell.py'. Alternatively, the app can run in the Java environment using Jython and the PyJ2D library with the command 'jython cell.py' or 'java -jar jython.jar cell.py'. The app can also run in the JavaScript environment using Pyjs compilation and the Pyjsdl library with the command '[pyjs_path]/bin/pyjsbuild -O cell.py --dynamic-link -o output' and copying data folder to pyjsbuild output.

Controls
Scroll up (UP/KP8)
Scroll down (DOWN/KP2)
Scroll left (LEFT/KP4)
Scroll right (RIGHT/KP6)
Reset (r)
Clear (c)
Pause/Edit toggle (Escape/e)
Edit cell (LMouse)
Panel toggle (p)
Pattern-panel/clipboard (LMouse/RMouse)


Released under the GPL3 license (http://www.gnu.org/licenses/gpl.html).

