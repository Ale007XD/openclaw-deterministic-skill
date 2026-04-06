import os
import runpy


def run():
    base = os.path.dirname(__file__)

    for file in os.listdir(base):
        if file.endswith("_test.py"):
            path = os.path.join(base, file)
            print(f"Running {file}")
            runpy.run_path(path, run_name="__main__")


if __name__ == "__main__":
    run()
