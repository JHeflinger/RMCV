# Jason's CV Tool

## How To Install

### Checklist!
- do you have python? (install if not)
- do you have opencv? (pip install if not)
- do you have tqdm? (pip install if not)
- do you have ultralytics? (pip install if not)

### Too lazy to manually do allat?

(Python must be installed manually, I'm not gonna do that for you unfortunately)

#### Windows
Run `./setup.bat` in your terminal

#### Linux
Run `./setup.sh` in your terminal

## How to use

### Windows
Run `./cli.bat` in your terminal

### Linux
Run `./cli.sh` in your terminal

### Need help?
run "help" for a list of commands and explanations

## Special Feature: .clirc

If your working directory has a `.clirc` file, the program will run each line of that file as an inputted command, effectively working as a macro for the tool!

### Example

If you want to run the `peel` command to get 100 frames from `assets/000.mp4` and store the images on `mytempfolder/images`, you can run the program and go through all the prompts individually. It will look something along the lines of:
```
./cli.bat
Welcome to the tool! What would you like to do?
>>> peel
What video do you want to peel from?
>>> assets/000.mp4
Where do you want to store your peeled images?
>>> mytempfolder/images
How many images do you want to peel?
>>> 100
Peeling images...
.
.
.
```

However, what if I'm lazy and want to do that multiple times without typing that all out? Then you can create a `.clirc` file with the following contents:
```
peel
assets/000.mp4
mytempfolder/images
100
```
Now, when you run the program, it will automatically open this file and simulate each line as an input automatically, effectively doing the same as if you were to input that string of lines manually:
```
./cli.bat
Peeling images...
.
.
.
```
Neato!