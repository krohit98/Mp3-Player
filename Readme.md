<b>This Readme doc contains:</b>

1)About the project  
2)Requirements to use the player  
3)Instructions to setup the mp3 player  
4)Instructions to play mp3 files  

<b><ins>ABOUT THE PROJECT</ins></b>

This is a simple mp3 player application built in python3 using the following python libraries:  
1)<b>tkinter</b> - Creates the GUI.  
2)<b>pygame</b> - Plays the audio files.  
3)<b>mutagen</b> - Extracts the metadata of the mp3 files.  
4)<b>stagger</b> - Extracts the metadata of the mp3 files.  
5)<b>PIL</b> - Extracts image data.  
It also uses an sqlite3 database to store the info about the mp3 files.  

<b><ins>REQUIREMENTS TO USE THE PLAYER</ins></b>

1)You must have python3 installed and running properly on your system (refer the internet if you dont have it).  
2)Install following python modules: pygame, mutagen, stagger, PIL (go to the python terminal and type "pip install module-name" but refer the internet if it doesnt work).  

<b><ins>INSTRUCTIONS TO SETUP THE MP3 PLAYER</ins></b>

1)Clone the repository to get a working copy on your machine.  
2)Extract the icons from the icons folder and put them in the same folder where the source code is.  
3)Go to your IDE or editor and run the program.  

<b><ins>INSTRUCTIONS TO PLAY MP3 FILES</ins></b>

1)In the application window, click on 'select a directory' button.  
2)Select the folder with your mp3 files or where you wish to put mp3 files. An SQLite3 database called 'Music Book.db" will be created inside the folder.  
3)Write the exact name of the mp3 file you wish to play in the search field and click on 'play' button to play the file.  
4)To add a new file to the folder, click on 'Add file' button.  
5)To delete a file from the folder, click on 'Delete file' button.  
6)To edit the info of any file in the folder, click on 'Update file info' button.  
7)Features such as pause,next,previous,rewind,mute and volume controls are supported and can be carried out by their respective buttons.  
