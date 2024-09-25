import time
import os
from tqdm import tqdm

Black = "\033[30m"
Red = "\033[31m"
Green = "\033[32m"
Yellow = "\033[33m"
Blue = "\033[34m"
Magenta = "\033[35m"
Cyan = "\033[36m"
White = "\033[37m"
Reset = "\033[0m"

class Timer:
    def __init__(self):
        self.curr = time.time_ns()
    
    def end(self):
        old = self.curr
        self.curr = time.time_ns()
        return float((self.curr - old) // 1_000_000) / 1000


def benchmark(models):
    print("Initializing ultralytics...")
    timer = Timer()
    import cv2
    from ultralytics import YOLO
    print(f"Finished in {Green}{timer.end()}{Reset} seconds")
    resultframe = []
    for modelname in models:
        print(f"Benchmarking {modelname}...")
        timer.end()
        model = YOLO("models/" + modelname, verbose=False)
        times = []
        tot = 0
        for entry in os.listdir("assets"):
            if os.path.isfile(os.path.join("assets", entry)):
                cap = cv2.VideoCapture("assets/" + entry)
                if cap.isOpened():
                    tot += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
        progress = tqdm(total = tot)
        for entry in os.listdir("assets"):
            if os.path.isfile(os.path.join("assets", entry)):
                cap = cv2.VideoCapture("assets/" + entry)
                timeset = []
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    mytime = Timer()
                    results = model(frame, verbose=False)
                    timeset.append(mytime.end())
                    progress.update(1)
                cap.release()
                mint = timeset[0]
                for time in timeset:
                    if time < mint:
                        mint = time
                pruned = []
                for time in timeset:
                    if time < 10.0 * mint:
                        pruned.append(time)
                times += pruned
        progress.close()
        print(f"Finished benchmaking {modelname} in {Green}{timer.end()}{Reset} seconds")
        final = 0.0
        for time in times:
            final += time
        final /= len(times)
        resultframe.append([modelname, final])
    print("Results: \n")
    for result in resultframe:
        print(f"  Model Name: {result[0]}")
        print(f"    AET: {Green}{result[1]}{Reset} seconds")
        print(f"    Average FPS: {Green}{1.0 / result[1]}{Reset}")
        print("")
    print(f"({Yellow}AET{Reset} stands for {Yellow}A{Reset}verage {Yellow}E{Reset}xecution {Yellow}T{Reset}ime, refers to the time it takes to process a frame using the model)")