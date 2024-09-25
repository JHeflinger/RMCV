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

def label(srcdir, datadir):
    print("Initializing pygame...")
    timer = Timer()
    import pygame
    import shutil
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("LMB: Red | RMB: Blue | ENTR: Submit | C: Clear | ESC: Reject")
    print(f"Finished in {Green}{timer.end()}{Reset} seconds")
    class_labels = {'Red': 0, 'Blue': 1}
    images = []
    image_names = []
    split_count = 0
    for filename in os.listdir(srcdir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(srcdir, filename)
            images.append(img_path)
            image_names.append(filename)
    if not images:
        print("No images found to label in source directory...")
        return
    current_image_index = 0
    selected_boxes = []
    selecting = False
    start_pos = (0, 0)

    if not os.path.isfile(os.path.join(datadir, "dataset.yaml")):
        print("No dataset config found, implicitly creating one now...")
        with open(os.path.join(datadir, "dataset.yaml"), 'w') as file:
            imgpath = os.path.join(os.path.join(datadir, "images"), "train")
            valpath = os.path.join(os.path.join(datadir, "images"), "val")
            file.write(
                "path: .\n" + 
                f"train: {imgpath}\n" + 
                f"val: {valpath}\n" + 
                "\n" + 
                "nc: 2\n" + 
                "names: ['Red', 'Blue']"
            )

    while True:
        if (current_image_index >= len(images)):
            print("No more images to label! Shutting down now!")
            pygame.quit()
            return
        
        if os.path.isfile(os.path.join(srcdir, ".jignore")):
            with open(os.path.join(srcdir, ".jignore"), 'r') as file:
                for line in file.readlines():
                    if image_names[current_image_index] == line.strip():
                        current_image_index += 1
                        continue

        img = pygame.image.load(images[current_image_index])
        img_rect = img.get_rect(center=(400, 300))
        screen.fill((255, 255, 255))
        screen.blit(img, img_rect)

        for box in selected_boxes:
            color = (255, 0, 0) if box['label'] == 'Red' else (0, 0, 255)
            pygame.draw.rect(screen, color, box['rect'], 2)
        
        if selecting:
            end_pos = pygame.mouse.get_pos()
            rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
            pygame.draw.rect(screen, (0, 255, 0), rect, 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    selected_boxes.clear()

                if event.key == pygame.K_ESCAPE:
                    if not os.path.isfile(os.path.join(srcdir, ".jignore")):
                        print("ignore file was not detected... implicitly creating one now...")
                        with open(os.path.join(srcdir, ".jignore"), "w") as file:
                            file.write(image_names[current_image_index] + "\n")
                    else:
                        with open(os.path.join(srcdir, ".jignore"), "a") as file:
                            file.write(image_names[current_image_index] + "\n")
                    selecting = False
                    current_image_index += 1

                if event.key == pygame.K_RETURN:
                    if not os.path.isfile(os.path.join(srcdir, ".jignore")):
                        print("ignore file was not detected... implicitly creating one now...")
                        with open(os.path.join(srcdir, ".jignore"), "w") as file:
                            file.write(image_names[current_image_index] + "\n")
                    else:
                        with open(os.path.join(srcdir, ".jignore"), "a") as file:
                            file.write(image_names[current_image_index] + "\n")
                    selecting = False
                    os.makedirs(os.path.join(datadir, "labels/train"), exist_ok=True)
                    os.makedirs(os.path.join(datadir, "labels/val"), exist_ok=True)
                    os.makedirs(os.path.join(datadir, "images/train"), exist_ok=True)
                    os.makedirs(os.path.join(datadir, "images/val"), exist_ok=True)
                    split_count += 1
                    if split_count < 9:
                        with open(os.path.join(datadir, "labels/train/" + image_names[current_image_index].split(".")[0] + ".txt"), 'w') as f:
                            for box in selected_boxes:
                                x_center = (box['rect'].x + box['rect'].width / 2) / img.get_width()
                                y_center = (box['rect'].y + box['rect'].height / 2) / img.get_height()
                                width = box['rect'].width / img.get_width()
                                height = box['rect'].height / img.get_height()
                                label = box['label']
                                f.write(f"{class_labels[label]} {x_center} {y_center} {width} {height}\n")
                        shutil.copy(images[current_image_index], os.path.join(datadir, "images/train/" + image_names[current_image_index]))
                    else:
                        with open(os.path.join(datadir, "labels/val/" + image_names[current_image_index].split(".")[0] + ".txt"), 'w') as f:
                            for box in selected_boxes:
                                x_center = (box['rect'].x + box['rect'].width / 2) / img.get_width()
                                y_center = (box['rect'].y + box['rect'].height / 2) / img.get_height()
                                width = box['rect'].width / img.get_width()
                                height = box['rect'].height / img.get_height()
                                label = box['label']
                                f.write(f"{class_labels[label]} {x_center} {y_center} {width} {height}\n")
                        shutil.copy(images[current_image_index], os.path.join(datadir, "images/val/" + image_names[current_image_index]))
                    current_image_index += 1
                    selected_boxes.clear()
                    if split_count >= 10:
                        split_count = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                start_pos = event.pos
                selecting = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and selecting:
                    end_pos = event.pos
                    rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                    selected_boxes.append({'rect': rect, 'label': 'Red'})
                    selecting = False
                elif event.button == 3 and selecting:
                    end_pos = event.pos
                    rect = pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]))
                    selected_boxes.append({'rect': rect, 'label': 'Blue'})
                    selecting = False