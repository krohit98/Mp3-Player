#importing modules and libraries

import sys
import io
import os
import shutil
import sqlite3
import time
from tkinter import *
from tkinter import filedialog
from tkinter.filedialog import askdirectory

import pygame
import stagger
from mutagen.mp3 import MP3
from PIL import Image, ImageTk

dir_path = sys.path[0]
root=Tk()
root.title("MUSIC PLAYER")
root.iconbitmap(os.path.join(dir_path,"music.ico"))
root.configure(bg="gray8")
root.minsize(500,320)
      
# Creating methods:

#for clearing widgets inside a frame    
def clearFrame(f):
    for widget in f.winfo_children():
       widget.destroy() 

#for selecting or creating a song folder
def set_dir():
    global folder
    folder=filedialog.askdirectory()
    os.chdir(folder)
    filename=os.listdir(folder)
    files=root.tk.splitlist(filename)
    if os.path.isfile(os.path.join(folder,"Music_book.db"))==FALSE:
        conn=sqlite3.connect("Music_book.db")
        c=conn.cursor()
        c.execute("""CREATE TABLE metadata(
            id INTEGER PRIMARY KEY,
            location text,
            title text,
            album text,
            year text,
            genre text,
            artist text,
            minutes integer,
            seconds integer
            )""")
        conn.commit()
        conn.close()
        for file in files:
            realdir=os.path.realpath(file)
            audio=stagger.read_tag(realdir)
            audio1=MP3(realdir)
            length=int(audio1.info.length)
            minute=int(length/60)
            sec=int(length%60)
            conn=sqlite3.connect("Music_book.db")
            c=conn.cursor()
            c.execute("INSERT INTO metadata VALUES (NULL,:s_location,:s_title,:s_album,:s_year,:s_genre,:s_artist,:s_minutes,:s_seconds)",
                        {
                            "s_location":realdir,
                            "s_title":audio.title,
                            "s_album":audio.album,
                            "s_year":audio.date,
                            "s_genre":audio.genre,
                            "s_artist":audio.artist,
                            "s_minutes":minute,
                            "s_seconds":sec  
                        })
            conn.commit()
            conn.close()
    stop()
    clearFrame(frame1)
    clearFrame(frame2)
    clearFrame(frame3)


#for adding songs to the directory and database       
def add():
    root1=Tk()
    root1.title("Add a music file")
    root1.iconbitmap(os.path.join(dir_path,"music.ico"))
    root1.configure(bg="gray8")
    root1.minsize(350,100)
    
    select_entry=Entry(root1)
    select_entry.grid(row=0,column=1,padx=(5,0),ipadx=50)
    
    # to select the mp3 file to add
    def select():
        global files
        root1.filename=filedialog.askopenfilename(multiple=True,initialdir="/",
                                                  title="Select a File", 
                                                  filetypes=(("mp3 files","*.mp3"),("all files","*.*")))
        select_entry.insert(0,root1.filename)
        files=root.tk.splitlist(root1.filename)
        
    # adds songs to the directory and database
    def add_song():
        global folder
        for file in files:
            moved_file=shutil.move(file,folder)
            realdir=os.path.realpath(moved_file)
            audio=stagger.read_tag(realdir)
            audio1=MP3(realdir)
            length=int(audio1.info.length)
            minute=int(length/60)
            sec=int(length%60)
            conn=sqlite3.connect("Music_book.db")
            c=conn.cursor()
            c.execute("INSERT INTO metadata VALUES (NULL,:s_location,:s_title,:s_album,:s_year,:s_genre,:s_artist,:s_minutes,:s_seconds)",
                     {
                          "s_location":realdir,
                          "s_title":audio.title,
                          "s_album":audio.album,
                          "s_year":audio.date,
                          "s_genre":audio.genre,
                          "s_artist":audio.artist,
                          "s_minutes":minute,
                          "s_seconds":sec  
                     })
            conn.commit()
            conn.close()
            
        select_entry.delete(0,END)
        
    select_btn=Button(root1,text="Select File",command=select,width=10,bd=3,bg="gray",fg="black")
    select_btn.grid(row=0,column=0,padx=10,pady=(10,5))
    
    add_song_btn=Button(root1,text="Add File",command=add_song,width=10,bd=3,bg="gray",fg="black")
    add_song_btn.grid(row=1,column=0,padx=10)

# to delete an mp3 file from the directory and database
def delete():
    
    root2=Tk()
    root2.minsize(300,200)
    root2.title("Delete a Song")
    root2.iconbitmap(os.path.join(dir_path,"music.ico"))
    root2.configure(bg="gray8")
    listbox=Listbox(root2,width=30)
    listbox.pack()
    conn=sqlite3.connect("Music_book.db")
    c=conn.cursor()
    c.execute("SELECT id,title FROM metadata")
    records=c.fetchall()
    id_list=[]
    for record in records:
        id_list+=[str(record[0])+". "+record[1]]
    id_list.reverse()
    for item in id_list:
        listbox.insert(0,item)
    
    # deletes the mp3 file
    def delete_song():
        val=listbox.get(listbox.curselection())
        if val[1]==".":
            id_val=str(val[0])
        elif val[2]==".":
            id_val=str(val[0])+str(val[1])
        elif val[3]==".":
            id_val=str(val[0])+str(val[1])+str(val[2])
        conn=sqlite3.connect("Music_book.db")
        c=conn.cursor()
        c.execute("""SELECT location FROM metadata WHERE id="""+id_val)
        r=c.fetchone()
        os.remove(r[0])
        c.execute("""DELETE FROM metadata WHERE id="""+id_val)
        c.execute("""UPDATE metadata SET 
          id=id-1
          WHERE id>?""",(id_val,) )
        c.execute("SELECT id,title FROM metadata")
        records=c.fetchall()
        id_list=[]
        for record in records:
             id_list+=[str(record[0])+". "+record[1]]
        id_list.reverse()
        listbox.delete(0,END)
        for item in id_list:
             listbox.insert(0,item)
        conn.commit()
        conn.close()
    
    delete_song_btn=Button(root2,text="Delete File",command=delete_song,bd=3,bg="gray",fg="black")
    delete_song_btn.pack()
    conn.commit()
    conn.close()        
    
global var
global id_playing
global temp_time1
global temp_time2
var=0
temp_time1=1
temp_time2=1
id_playing=1

# returns the maximum song id from the database 
def get_max_id():
    conn=sqlite3.connect("Music_book.db")
    c=conn.cursor()
    c.execute("""SELECT MAX(id) FROM metadata""")
    r=c.fetchone()
    max_id=r[0]
    conn.commit()
    conn.close()
    return max_id

# to plays the mp3 file
def play():
    global var
    global id_playing
    global prev_btn
    global next_btn
    global song_scale
    global pos
    global f_len
    global max_id
    max_id=get_max_id()
    clearFrame(frame2)
    clearFrame(frame1)
    conn=sqlite3.connect("Music_book.db")
    c=conn.cursor()
    if search.get()=="":
        c.execute("""SELECT * FROM metadata WHERE id="""+str(id_playing))
    else:
        c.execute("""SELECT * FROM metadata WHERE title=?""",(search.get(),))
    records=c.fetchall()
    for record in records:
        file=stagger.read_tag(record[1])
        a=file[stagger.id3.APIC][0].data
        im=io.BytesIO(a)
        image_file=Image.open(im)
        new_img=image_file.resize((144,174), Image.ANTIALIAS)
        photo=ImageTk.PhotoImage(new_img)
        art=Label(frame1,image=photo)
        art.image=photo
        art.place(x=0,y=0)
        title=Label(frame2,text="Title: "+record[2],bg="dark slate gray",fg="white")
        title.place(x=10,y=10)
        album=Label(frame2,text="Album: "+record[3],bg="dark slate gray",fg="white")
        album.place(x=10,y=30) 
        year=Label(frame2,text="Year: "+record[4],bg="dark slate gray",fg="white")
        year.place(x=10,y=50)
        genre=Label(frame2,text="Genre: "+record[5],bg="dark slate gray",fg="white")
        genre.place(x=10,y=70) 
        artist=Label(frame2,text="Artist: "+record[6],bg="dark slate gray",fg="white")
        artist.place(x=10,y=90)
        if record[8]<10:
                duration=Label(frame3,text=str(record[7])+":0"+str(record[8]),bg="dark slate gray",fg="white")
        else:
                duration=Label(frame3,text=str(record[7])+":"+str(record[8]),bg="dark slate gray",fg="white")
        duration.place(x=268,y=10)
        song_scale=Scale(frame3,from_=0,orient=HORIZONTAL,width=5,resolution=1,length=290,bd=2,troughcolor="gray8",highlightbackground="dark slate gray",bg="dark slate gray",sliderlength=10,showvalue=0)
        song_scale.set(0)
        song_scale.place(x=0,y=30)
        pos=record[1]
        id_playing=record[0]
    conn.commit()
    conn.close()
    
    if search.get=="":
        var=0    
           
    audio=MP3(pos)
    f_len=int(audio.info.length) 

   
    if var == 1:  # to play paused song
        pygame.mixer.init()
        pygame.mixer.music.unpause()
        def call_set_time():
            s_pos=pygame.mixer.music.get_pos()
            set_time(s_pos)
            go_to_next(s_pos)
            root.after(1000,call_set_time)
        call_set_time()
    elif var == 0: # to play songs from start
        pygame.mixer.quit()
        pygame.mixer.pre_init(frequency=audio.info.sample_rate)
        pygame.mixer.init()
        pygame.mixer.music.load(pos)
        pygame.mixer.music.play()
        def call_set_time():
            s_pos=pygame.mixer.music.get_pos()
            set_time(s_pos)
            go_to_next(s_pos)
            root.after(1000,call_set_time)
        call_set_time()
        
    pause_btn=Button(root,text="Pause Song",command=pause,width=10,bd=3,bg="gray",fg="black")
    pause_btn.grid(row=7,column=0,padx=(5,0),pady=(10,0))
    
    if id_playing==1:
        prev_btn=Button(root,text="<<",state=DISABLED,width=10,bd=3,bg="gray",fg="black")        
    else:
        prev_btn=Button(root,text="<<",command=prev,width=10,bd=3,bg="gray",fg="black")
    prev_btn.grid(row=7,column=2,pady=(10,0)) 

    if id_playing==max_id:
        next_btn=Button(root,text=">>",state=DISABLED,width=10,bd=3,bg="gray",fg="black")
    else:
        next_btn=Button(root,text=">>",command=next_song,width=10,bd=3,bg="gray",fg="black")
    next_btn.grid(row=7,column=3,pady=(10,0))     
            
    search.delete(0,END)  
    
# sets the tile slider scale according to song position    
def set_time(val):
    global temp_time1 
    global song_scale     
    song_scale.config(to=f_len)
    time=int(val/1000)
    if time==temp_time1:
        return
    song_scale.set(time)
    mins=int(time/60)
    secs=time%60
    
    if secs<10:
        time_running=Label(frame3,text=str(mins)+":0"+str(secs),bg="dark slate gray",fg="white")
    else:
        time_running=Label(frame3,text=str(mins)+":"+str(secs),bg="dark slate gray",fg="white")  
    time_running.place(x=0,y=10)        
    if time==f_len:
        return
    temp_time1=int(val/1000)

# counts up to the end of a song to play the next one after it is finished
def go_to_next(val):
    global temp_time2
    time=int(val/1000) 
    if time==temp_time2:
        return
    s_len=f_len-time
    temp_time2=int(val/1000)    
    if s_len == 0:
        next_song()
        return
   

# to pause a song    
def pause():
    global var
    var=1
    c_pos=pygame.mixer.music.get_pos()
    pygame.mixer.music.pause()
    set_time(c_pos)
    go_to_next(c_pos)
    play_btn=Button(root,text="Play Song",command=play,width=10,bd=3,bg="gray",fg="black")
    play_btn.grid(row=7,column=0,padx=(5,0),pady=(10,0))
    
# to stop a song    
def stop():
    global var
    var=0
    pygame.mixer.init()
    pygame.mixer.music.stop()
    set_time(0)
    go_to_next(0)
    play_btn=Button(root,text="Play Song",command=play,width=10,bd=3,bg="gray",fg="black")
    play_btn.grid(row=7,column=0,padx=(5,0),pady=(10,0))

# to rewind a song
def rewind():
    global var
    var=0
    play()
    
# to go to the next song    
def next_song():
    global id_playing
    global max_id
    global var
    var=0
    id_playing=id_playing+1
    if id_playing > max_id:
        stop()
        clearFrame(frame1)
        clearFrame(frame2)
        id_playing=1
    else:
        play()
    

# to go to the previous song    
def prev():
    global id_playing
    global var
    var=0
    id_playing=id_playing-1
    play()

       
# to update any metadata info about a song in the database
def update_info():
    root3=Tk()
    root3.title("Edit Info")
    root3.iconbitmap(os.path.join(dir_path,"music.ico"))
    root3.configure(bg="gray8")
    root3.geometry("400x400")
    # opens up a window to update info
    def s_update():
            val=l_box.get(l_box.curselection())
            if val[2]==".":
                id_val=str(val[1])
            elif val[3]==".":
                id_val=str(val[1])+str(val[2])
            elif val[4]==".":
                id_val=str(val[1])+str(val[2])+str(val[3])
            conn=sqlite3.connect("Music_book.db")
            c=conn.cursor()
            c.execute("SELECT * FROM metadata WHERE id="+id_val)
            rec=c.fetchall()
            for r in rec:
                 title=Label(root3,text="Title :",bg="gray8",fg="white")
                 album=Label(root3,text="Album :",bg="gray8",fg="white")
                 year=Label(root3,text="Year :",bg="gray8",fg="white")
                 genre=Label(root3,text="Genre :",bg="gray8",fg="white")
                 artist=Label(root3,text="Artist :",bg="gray8",fg="white")
                 
                 title_edit=Entry(root3,width=50,bd=3)
                 album_edit=Entry(root3,width=50,bd=3)
                 year_edit=Entry(root3,width=50,bd=3)
                 genre_edit=Entry(root3,width=50,bd=3)
                 artist_edit=Entry(root3,width=50,bd=3)
                 
                 title_edit.insert(0,r[2])
                 album_edit.insert(0,r[3])
                 year_edit.insert(0,r[4])
                 genre_edit.insert(0,r[5])
                 artist_edit.insert(0,r[6])
                 
                 title.place(x=10,y=220)
                 album.place(x=10,y=245)
                 year.place(x=10,y=270)
                 genre.place(x=10,y=295)
                 artist.place(x=10,y=320)
                 
                 title_edit.place(x=70,y=220)
                 album_edit.place(x=70,y=245)
                 year_edit.place(x=70,y=270)
                 genre_edit.place(x=70,y=295)
                 artist_edit.place(x=70,y=320)
                 
                 # saves changes to info update
                 def save():
                     conn=sqlite3.connect("Music_book.db")
                     c=conn.cursor()
                     c.execute("""UPDATE metadata SET              
                               title = :title_s,
                               album = :album_s,
                               year = :year_s,
                               genre = :genre_s,
                               artist = :artist_s
                               
                               WHERE id ="""+id_val,
                               {
                                   "title_s": title_edit.get(),
                                   "album_s": album_edit.get(),
                                   "year_s": year_edit.get(),
                                   "genre_s": genre_edit.get(),
                                   "artist_s": artist_edit.get()                      
                               })
                     c.execute("SELECT id,title FROM metadata")
                     records=c.fetchall()
                     id_list=[]
                     for record in records:
                         id_list+=[" "+str(record[0])+". "+record[1]]
                     id_list.reverse()
                     l_box.delete(0,END)
                     for item in id_list:
                        l_box.insert(0,item)
                     conn.commit()
                     conn.close()
                     
                     title_edit.delete(0,END)
                     album_edit.delete(0,END)
                     year_edit.delete(0,END)
                     genre_edit.delete(0,END)
                     artist_edit.delete(0,END)
                
                 save_btn=Button(root3,text="Save Changes",command=save,bd=3,bg="gray",fg="black")
                 save_btn.place(x=70,y=350)
                    
            conn.commit()
            conn.close()
        
    select_song=Label(root3,text="Select a song to edit :",bg="gray8",fg="white")
    select_song.place(x=10,y=10)
    l_box=Listbox(root3,width=40,height=10,bd=3)
    l_box.place(x=130,y=10)
    conn=sqlite3.connect("Music_book.db")
    c=conn.cursor()
    c.execute("SELECT id,title FROM metadata")
    records=c.fetchall()
    id_list=[]
    for record in records:
        id_list+=[" "+str(record[0])+". "+record[1]]
    id_list.reverse()
    for item in id_list:
        l_box.insert(0,item)
    
    select_btn=Button(root3,text="Select Song",command=s_update,bd=3,bg="gray",fg="black")
    select_btn.place(x=215,y=180)
    conn.commit()
    conn.close()

# sets the volume of the player        
def set_vol(val):
    value=int(val)/100
    pygame.mixer.init()
    pygame.mixer.music.set_volume(value)
    
# to toggle between mute and unmute options        
muted=FALSE

def set_mute():
    global muted
    
    if muted:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)    
        mute_btn.config(image=mute_icon)
        vol_scale.set(50)
        muted=FALSE
    
    else:
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0)    
        mute_btn.config(image=unmute_icon)
        vol_scale.set(0)
        muted=TRUE

# stops the music player when window is closed        
def on_close():
    pygame.mixer.init()
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    root.destroy()

# Creating root widgets:

frame=LabelFrame(root,height=190,width=480,relief=SUNKEN,bd=7,bg="dim gray")
frame.grid(row=2,column=0,columnspan=7,padx=10,pady=(10,0))

frame1=LabelFrame(frame,height=180,width=150,bd=1,bg="dark slate gray")
frame1.grid(row=0,column=0,rowspan=3,padx=10,pady=10)

frame2=LabelFrame(frame,height=120,width=300,bd=1,bg="dark slate gray")
frame2.grid(row=0,column=1,padx=(0,10),pady=10)

frame3=LabelFrame(frame,height=50,width=300,bd=1,bg="dark slate gray")
frame3.grid(row=1,column=1,padx=(0,10),pady=(0,10))
    
search=Entry(root,bd=3,width=70)
search.grid(row=0,column=1,columnspan=8,pady=(10,0))

Search=Label(root,text="Search Song: ",bg="gray8",fg="white")
Search.grid(row=0,column=0,pady=(10,0))

add_btn=Button(root,text="Add Song",command=add,bd=3,width=10,bg="gray",fg="black")
add_btn.grid(row=1,column=0,padx=(5,0),pady=(10,0))   

delete_btn=Button(root,text="Delete Song",command=delete,bd=3,width=10,bg="gray",fg="black")
delete_btn.grid(row=1,column=1,padx=(4,0),pady=(10,0)) 

play_btn=Button(root,text="Play Song",command=play,width=10,bd=3,bg="gray",fg="black")    
play_btn.grid(row=7,column=0,padx=(5,0),pady=(10,0))

stop_btn=Button(root,text="Stop Song",command=stop,width=10,bd=3,bg="gray",fg="black")
stop_btn.grid(row=7,column=1,pady=(10,0))

next_btn=Button(root,text=">>",command=next_song,width=10,bd=3,bg="gray",fg="black")
next_btn.grid(row=7,column=3,pady=(10,0))

prev_btn=Button(root,text="<<",command=prev,width=10,bd=3,bg="gray",fg="black")
prev_btn.grid(row=7,column=2,pady=(10,0))

update_song=Button(root,text="Edit Song Info",command=update_info,width=20,bd=3,bg="gray",fg="black")
update_song.grid(row=1,column=2,columnspan=2,padx=(5,0),pady=(10,0))

set_dir_btn=Button(root, text="Select/Create Folder", command=set_dir, width=25,bd=3,bg="gray",fg="black")
set_dir_btn.grid(row=1,column=4,columnspan=3,pady=(10,0))

icon3=Image.open(os.path.join(dir_path,"replay.png"))
new_icon3=icon3.resize((20,20), Image.ANTIALIAS)
rew_icon=ImageTk.PhotoImage(new_icon3)
rew_btn=Button(root,width=30,bd=3,command=rewind,bg="gray")
rew_btn.grid(row=7,column=4,pady=(10,0))
rew_btn.config(image=rew_icon)

icon1=Image.open(os.path.join(dir_path,"vol_on1.png"))
new_icon1=icon1.resize((20,20), Image.ANTIALIAS)
mute_icon=ImageTk.PhotoImage(new_icon1)
mute_btn=Button(root,width=30,bd=3,command=set_mute,bg="gray")
mute_btn.grid(row=7,column=5,pady=(10,0))
mute_btn.config(image=mute_icon)

icon2=Image.open(os.path.join(dir_path,"vol_off1.png"))
new_icon2=icon2.resize((20,20), Image.ANTIALIAS)
unmute_icon=ImageTk.PhotoImage(new_icon2)


vol_scale=Scale(root,from_=0,to=100,orient=HORIZONTAL,width=10,length=110,bd=2,highlightbackground="gray8",fg="white",bg="gray8",command=set_vol)
vol_scale.set(50)
vol_scale.grid(row=7,column=6)


root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
