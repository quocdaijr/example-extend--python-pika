import sys

from jobs import ExampleJob

if __name__ == '__main__':
    _type = sys.argv[1] if len(sys.argv) >= 2 else None
    if _type == "send":
        job = ExampleJob()
        job.pub({
            "data": "some text"
        })
        print("Send success. Run command receive to see result")
    elif _type == "receive":
        job = ExampleJob()
        job.sub()
    else:
        print("Not valid")
