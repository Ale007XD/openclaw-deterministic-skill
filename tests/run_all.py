import os
import sys
import runpy


def run():
    base = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(base)

    sys.path.insert(0, root)

    files = sorted(f for f in os.listdir(base) if f.endswith("_test.py"))
    passed = 0
    failed = []

    for file in files:
        path = os.path.join(base, file)
        try:
            runpy.run_path(path, run_name="__main__")
            print(f"  PASS  {file}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {file}: {e}")
            failed.append(file)

    print()
    print(f"Results: {passed} passed, {len(failed)} failed")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    run()
