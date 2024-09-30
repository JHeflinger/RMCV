import time
import os
from tqdm import tqdm
import cv2
import shutil

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
    gwidth = 1600
    gheight = 1200
    timer = Timer()
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((gwidth, gheight))
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
        pygame.quit()
        return
    current_image_index = 0
    selected_boxes = []
    selecting = False
    start_pos = (0, 0)

    if not os.path.isfile(os.path.join(datadir, "dataset.yaml")):
        print("No dataset config found, implicitly creating one now...")
        with open(os.path.join(datadir, "dataset.yaml"), 'w') as file:
            imgpath = os.path.abspath(os.path.join(os.path.join(datadir, "images"), "train"))
            valpath = os.path.abspath(os.path.join(os.path.join(datadir, "images"), "val"))
            tpath = os.path.abspath(os.path.join(os.path.join(datadir, "images"), "test"))
            file.write(
                f"train: {imgpath}\n" + 
                f"val: {valpath}\n" + 
                f"test: {tpath}\n" + 
                "\n" + 
                "nc: 2\n" + 
                "names: ['Red', 'Blue']"
            )

    progress = tqdm(total = len(images))
    while True:        
        if os.path.isfile(os.path.join(srcdir, ".jignore")):
            with open(os.path.join(srcdir, ".jignore"), 'r') as file:
                for line in file.readlines():
                    if image_names[current_image_index] == line.strip():
                        current_image_index += 1
                        progress.update(1)
                        continue
        
        if (current_image_index >= len(images)):
            print("No more images to label! Shutting down now!")
            progress.close()
            pygame.quit()
            return

        img = pygame.image.load(images[current_image_index])
        img_rect = img.get_rect(center=(gwidth/2, gheight/2))
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
                progress.close()
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
                    progress.update(1)

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
                    os.makedirs(os.path.join(datadir, "labels/test"), exist_ok=True)
                    os.makedirs(os.path.join(datadir, "images/train"), exist_ok=True)
                    os.makedirs(os.path.join(datadir, "images/val"), exist_ok=True)
                    os.makedirs(os.path.join(datadir, "images/test"), exist_ok=True)
                    split_count += 1
                    txtname = image_names[current_image_index][0:len(image_names[current_image_index]) - len(image_names[current_image_index].split(".")[-1])] + "txt"
                    if split_count < 7:
                        with open(os.path.join(datadir, "labels/train/" + txtname), 'w') as f:
                            for box in selected_boxes:
                                x_center = ((box['rect'].x + box['rect'].width / 2) - ((gwidth / 2) - (img.get_width()/2))) / img.get_width()
                                y_center = ((box['rect'].y + box['rect'].height / 2) - ((gheight / 2) - (img.get_height()/2))) / img.get_height()
                                width = box['rect'].width / img.get_width()
                                height = box['rect'].height / img.get_height()
                                label = box['label']
                                f.write(f"{class_labels[label]} {x_center} {y_center} {width} {height}\n")
                        shutil.copy(images[current_image_index], os.path.join(datadir, "images/train/" + image_names[current_image_index]))
                    elif split_count < 9:
                        with open(os.path.join(datadir, "labels/val/" + txtname), 'w') as f:
                            for box in selected_boxes:
                                x_center = (box['rect'].x + box['rect'].width / 2) / img.get_width()
                                y_center = (box['rect'].y + box['rect'].height / 2) / img.get_height()
                                width = box['rect'].width / img.get_width()
                                height = box['rect'].height / img.get_height()
                                label = box['label']
                                f.write(f"{class_labels[label]} {x_center} {y_center} {width} {height}\n")
                        shutil.copy(images[current_image_index], os.path.join(datadir, "images/val/" + image_names[current_image_index]))
                    else:
                        with open(os.path.join(datadir, "labels/test/" + txtname), 'w') as f:
                            for box in selected_boxes:
                                x_center = (box['rect'].x + box['rect'].width / 2) / img.get_width()
                                y_center = (box['rect'].y + box['rect'].height / 2) / img.get_height()
                                width = box['rect'].width / img.get_width()
                                height = box['rect'].height / img.get_height()
                                label = box['label']
                                f.write(f"{class_labels[label]} {x_center} {y_center} {width} {height}\n")
                        shutil.copy(images[current_image_index], os.path.join(datadir, "images/test/" + image_names[current_image_index]))
                    current_image_index += 1
                    progress.update(1)
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

def trainmodel(name, datayaml, mpset, nepochs, nbatch):
    print("Initializing ultralytics...")
    timer = Timer()
    from ultralytics import YOLO
    print(f"Finished in {Green}{timer.end()}{Reset} seconds")
    print("Initializing preset...")
    timer.end()
    model = YOLO(mpset)
    print(f"Finished initializing preset in {Green}{timer.end()}{Reset} seconds")
    print("Starting training process...")
    timer.end()
    result = model.train(data=datayaml, epochs=nepochs, batch=nbatch)
    shutil.copy(os.path.join(os.path.join(result.save_dir, "weights"), "best.pt"), f"models/{name}.pt")
    print(f"Finished training process in {Green}{timer.end()}{Reset} seconds")
    print(f"Final model saved under \"{Green}models/{name}.pt{Reset}\"")

def applymodel(model, frame, history):
    return model(frame, verbose=False)

def modeldemo(assetpath, modelpath):
    print("Initializing ultralytics...")
    timer = Timer()
    from ultralytics import YOLO
    print(f"Finished in {Green}{timer.end()}{Reset} seconds")
    print(f"Starting video processing...")
    timer.end()
    model = YOLO(modelpath, verbose=False)
    tot = 0
    cap = cv2.VideoCapture(assetpath)
    if cap.isOpened():
        tot += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    progress = tqdm(total = tot)
    cap = cv2.VideoCapture(assetpath)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    output_path = 'cache.mp4'
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
    history = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        history.append(applymodel(model, frame, history))
        out.write(history[-1][0].plot())
        progress.update(1)
    cap.release()
    out.release()
    progress.close()
    print(f"Finished video processing in {Green}{timer.end()}{Reset} seconds")
    cap = cv2.VideoCapture(output_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        cv2.imshow('Demo Video', frame)
        if cv2.waitKey(25) & 0xFF == ord('q') or not cv2.getWindowProperty('Demo Video', cv2.WND_PROP_VISIBLE):
            break
    cap.release()
    cv2.destroyAllWindows()

def splitdir(dir, savedir, numways):
    for i in range(numways):
        os.makedirs(os.path.join(savedir, f"shard_{i}"), exist_ok=True)
    file_count = 0
    for root, dirs, files in os.walk(dir):
        file_count += len(files)
    print("Distributing files...")
    progress = tqdm(total = file_count)
    distcount = 0
    timer = Timer()
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            shutil.copy(file_path, os.path.join(savedir, f"shard_{distcount}/{file}"))
            distcount += 1
            if distcount >= numways:
                distcount = 0
            progress.update(1)
    progress.close()
    print(f"Finished distributing files in {Green}{timer.end()}{Reset} seconds!")
    
def peelvid(vidpath, storepath, numimages):
    tot = 0
    cap = cv2.VideoCapture(vidpath)
    if cap.isOpened():
        tot += int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if numimages > tot:
        print("Not enough frames to peel from! Please try and peel less or choose a longer video.")
        cap.release()
        return
    print("Peeling frames...")
    timer = Timer()
    progress = tqdm(total = numimages)
    interval = int(tot/numimages)
    curr_frame = 0
    for i in range(numimages):
        cap.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        ret, frame = cap.read()
        if not ret:
            cap.release()
            progress.close()
            print("Error occured while reading frame...")
            return
        cv2.imwrite(f"{storepath}/frame_{curr_frame}.png", frame)
        curr_frame += interval
        progress.update(1)
    cap.release()
    progress.close()
    print(f"Finished peeling frames in {Green}{timer.end()}{Reset} seconds!")