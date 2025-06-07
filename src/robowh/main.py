# my-python-project/src/main.py

from robowh.viewer import Viewer

if __name__ == "__main__":
    print("Welcome to the Robotic Warehouse Simulator!")

    viewer = Viewer()

    try:
        viewer.run()
    except KeyboardInterrupt:
        print('\nServer stopped by user')