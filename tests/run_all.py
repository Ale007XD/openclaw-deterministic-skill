import os
import sys
import runpy


def run():
    base = os.path.dirname(__file__)
    root = os.path.dirname(base)

    # 🔥 КРИТИЧНО: добавить ДО всего
    sys.path.insert(0, root)

    print("SYS.PATH =", sys.path[0])

    for file in os.listdir(base):
        if file.endswith("_test.py"):
            path = os.path.join(base, file)
            print(f"Running {file}")
            runpy.run_path(path, run_name="__main__")  # ✅ важно


if __name__ == "__main__":
    run()
