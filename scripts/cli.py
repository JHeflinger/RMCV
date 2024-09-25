import os
from lib import benchmark, label, trainmodel, Black, Red, Green, Yellow, Blue, Magenta, Cyan, White, Reset

prettylogger = True
state = 0
gdir = ""
pset = 0
epochs = 0
batch = 0

def pprint(mystr):
    global prettylogger
    if prettylogger:
        print(mystr)

def run_command(cmd):
    global state
    global gdir
    global pset
    global epochs
    global batch
    if cmd == "quit":
        return False
    if cmd == "help":
        print(f"With {Red}Jason's {Yellow}Super {Green}Insane {Cyan}Computer {Blue}Vision {Magenta}Environment{Reset}, you can do the following commands!")
        print(f"\thelp       | The command that 😍{Red}YOU{Reset}💖 are running right now silly!")
        print(f"\tbenchmark  | {Green}Tests{Reset} one or more models thouroughly to compare speed and accuracy! 👌")
        print(f"\tdemo       | Shows off our {Yellow}AWESOME{Reset} performance! 💪🥸")
        print(f"\tlabel      | Labels your {Magenta}🪨ROCKIN'🪨{Reset} data!")
        print(f"\ttrain      | Trains a new {Yellow}⭐STELLAR⭐{Reset} model")
        return True
    if state == 0:
        if cmd == "benchmark":
            pprint(f"I'm so happy you chose to {Green}BEN{Yellow}CHM{Red}ARK{Reset} 😁!!")
            pprint(f"Which 😍{Red}LOVELY{Reset}💖 model would you like to benchmark? (Enter the # of the selection you want)")
            ind = 2
            pprint("1. All of the below!")
            for entry in os.listdir("models"):
                if os.path.isfile(os.path.join("models", entry)):
                    pprint(f"{ind}. {entry}")
                ind += 1
            state = 1
            return True
        if cmd == "demo":
            print("not implemented yet buster...")
            exit()
            state = 2
            return True
        if cmd == "label":
            pprint(f"WHOS READY FOR SOME (boring) {Yellow}💪💪LABELING???💪💪{Reset}")
            pprint(f"What {Red}R{Yellow}A{Green}D{Cyan}I{Blue}C{Magenta}A{Red}L{Reset} directory are you labeling from?")
            state = 3
            return True
        if cmd == "train":
            pprint(f"WHOS READY FOR SOME (friggin' awesome) {Yellow}💪💪TRAINING???💪💪{Reset}")
            pprint(f"What {Red}R{Yellow}A{Green}D{Cyan}I{Blue}C{Magenta}A{Red}L{Reset} directory is your dataset in?")
            state = 6
            return True
    if state == 1:
        ind = 2
        testing = []
        for entry in os.listdir("models"):
            if os.path.isfile(os.path.join("models", entry)):
                if cmd == "1":
                    testing.append(entry)
                if cmd == str(ind):
                    testing.append(entry)
                    break
            ind += 1
        mystr = ""
        if len(testing) == 1:
            mystr = testing[0]
        elif len(testing) > 1:
            for test in testing[:-1]:
                mystr += test + ", "
            mystr = mystr[:-2] + " and " + testing[-1]
        if mystr != "":
            print(f"Benchmarking {mystr}...")
            benchmark(testing)
            state = 0
            return True
    if state == 3:
        if os.path.isdir(cmd):
            gdir = cmd
            state = 5
            pprint(f"{Yellow}⭐STELLAR⭐{Reset}!! Where do you want your labeled data to be stored?")
        else:
            pprint(f"That directory does {Red}NOT{Reset} exist!!")
        return True
    if state == 5:
        if os.path.isdir(cmd):
            state = 0
            print(f"Starting labeling program...")
            label(gdir, cmd)
        else:
            pprint(f"That directory does {Red}NOT{Reset} exist!!")
        return True
    if state == 6:
        if os.path.isfile(os.path.join(cmd, 'dataset.yaml')):
            gdir = os.path.join(cmd, 'dataset.yaml')
            pprint(f"{Yellow}⭐SICK⭐{Reset}!! What preset would you like to use?!")
            pprint("1. YOLOv8 Nano")
            pprint("2. YOLOv8 Small")
            pprint("3. YOLOv8 Medium")
            pprint("4. YOLOv10 Nano")
            pprint("5. YOLOv10 Small")
            pprint("6. YOLOv10 Medium")
            state = 7
        else:
            pprint(f"This is {Red}NOT{Reset} a directory with valid training data!!")
        return True
    if state == 7:
        if cmd.isdigit() and int(cmd) > 0 and int(cmd) < 6:
            pset = int(cmd)
            pprint(f"How many {Green}quivering{Reset} epochs will you train on?!")
            state = 8
        else:
            pprint(f"That was {Red}NOT{Reset} a valid option!")
        return True
    if state == 8:
        if cmd.isdigit() and int(cmd) > 0:
            epochs = int(cmd)
            pprint(f"How {Cyan}LARGE{Reset} will your batch size be?!")
            state = 9
        else:
            pprint(f"That was {Red}NOT{Reset} a valid option!")
        return True
    if state == 9:
        if cmd.isdigit() and int(cmd) > 0:
            batch = int(cmd)
            pprint(f"What do you want to call this {Red}R{Yellow}A{Green}D{Cyan}I{Blue}C{Magenta}A{Red}L{Reset} model?!")
            state = 10
        else:
            pprint(f"That was {Red}NOT{Reset} a valid option!")
        return True
    if state == 10:
        if cmd != "":
            mpset = ""
            if pset == 1:
                mpset = "yolov8n.pt"
            elif pset == 2:
                mpset = "yolov8s.pt"
            elif pset == 3:
                mpset = "yolov8m.pt"
            elif pset == 4:
                mpset = "yolov10n.pt"
            elif pset == 5:
                mpset = "yolov10s.pt"
            elif pset == 6:
                mpset = "yolov10m.pt"
            print(f"Starting training suite using \"{mpset}\" as a preset and training {epochs} epochs with a batch size of {batch}")
            trainmodel(cmd, gdir, mpset, epochs, batch)
            state = 0
        else:
            pprint(f"That was {Red}NOT{Reset} a valid option!")
        return True
    print(f"OHHHH NO 😢! That's an {Red}invalid{Reset} input 😱!")
    return True

def shell():
    print(f"Welcome to {Red}Jason's {Yellow}Super {Green}Insane {Cyan}Computer {Blue}Vision {Magenta}Environment{Reset}!")
    print(f"For a list of {Cyan}cool commands{Reset}, enter \"help\"!")
    print(f"To {Red}quit{Reset} 😢, enter \"quit\"")
    while (True):
        cmd = input(">>> ")
        if run_command(cmd) == False:
            return

if os.path.exists(".clirc"):
    prettylogger = False
    with open(".clirc", 'r') as file:
        lines = file.readlines()
        for line in lines:
            run_command(line.strip())
else:
    shell()