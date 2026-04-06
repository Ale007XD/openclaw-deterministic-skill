import os


def run():
    base = os.path.dirname(__file__)
    for file in os.listdir(base):
        if file.endswith("_test.py"):
            print(f"Running {file}")
            __import__(f"tests.{file[:-3]}")


if __name__ == "__main__":
    run()
