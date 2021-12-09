#PYTHON STORAGE UTILITY - DUPLICATE FILE FINDER
#NOT FULLY VERIFIED FOR SYSTEMS OTHER THAN WINDOWS

import os
from sys import argv #used to find the current file - a more reliable method of __file__
import collections
import hashlib
import math
import shutil
import time
import re
import send2trash #a safer alternative to os.remove()


def deleteFiles(list): #deletes entries in supplied list
    if len(list) > 0:
        print("\nDeleting files.....")
        for i in list:
            print("deleting",i)
            try:
                #os.remove(i)
                send2trash(i) #if you want to use included modules only, remove this line and uncomment os.remove()
            except:
                print("Could not delete",i)
        time.sleep(1)
        print("Done deleting duplicate files")


def getFiles(): #alternate method to os.listdir() that doesn't include directories
    f = []
    for (dirpath, dirnames, filenames) in os.walk(os.getcwd()): #get filenames excluding subdirectories
        break
    return filenames


def progressBar(current,total,barLength=40): #makes a neat progress bar
    percent = float(current*100)/total
    arrow = "-" * int(percent/100*barLength-1) + '>' #makes the arrow
    spaces = ' ' * (barLength-len(arrow))
    print("Progress: [%s%s] %d%%" % (arrow, spaces, percent), end='\r')


def percentBar(current,total,barLength=40):
    percent = current*100/total
    bar = "=" * int(percent/100*barLength-1) + '|' #makes bar
    spaces = ' ' * (barLength-len(bar)) #makes the blank space
    return "[%s%s] %1.4g%%" %(bar,spaces,percent) 


def md5sum(filename,partial=False): 
    md5 = hashlib.md5()
    BUFFER_SIZE = 32768 #prevents the program from using up too much memory
    with open(filename, 'rb') as file: #open the target file in binary format
        buffer = file.read(BUFFER_SIZE) #loads a portion of the file into memory
        while len(buffer) > 0:
            md5.update(buffer) #add file data to the buffer
            buffer = file.read(BUFFER_SIZE)
            if partial: #if True, hashes only the first 32kb
                break
    return md5.hexdigest() #return the digested hash


def hashDuplicates(fileList=[],partial=True): #finds duplicate files based on hash. Tries to find the original one
    if partial:
        fileList = getFiles()
    fileList.sort(reverse=True) #make sure anything with parenthesis gets put after the original file in order
    
    hashList = []
    for targetFile in fileList:
        hashList.append(md5sum(targetFile,partial))
        progressBar(fileList.index(targetFile)+1,len(fileList)) #experimental feature

    hashListDupes = collections.Counter(hashList)

    duplicates = {}
    duplicatesList = []

    for key in hashListDupes: #getting the original file names
        if hashListDupes[key] > 1:
            itemIndex = hashList.index(key)
            duplicates[fileList[itemIndex]] = []
            duplicatesList.append(fileList[itemIndex])
            hashList[itemIndex] = "" #removes the entry from the list
            for i in range(hashListDupes[key]-1):
                itemIndex2 = hashList.index(key)
                duplicates[fileList[itemIndex]].append(fileList[itemIndex2]) #adds duplicate file names to the dictionary entry
                duplicatesList.append(fileList[itemIndex2])
                hashList[itemIndex2] = "" 
    if partial:
        return hashDuplicates(duplicatesList,partial=False) #recursive function
    return duplicates #return dictionary


def nameDuplicates(): #find duplicates based on name and find the most recent one
    extensions = [] #stores file extensions
    baseNames = [] #stores the base file name (without duplicate number and extension)

    files = getFiles()
    files.sort(key= lambda x: (os.path.getmtime,x),reverse=True) #order by date modified, then by name

    for i in files:
        filename, file_extension = os.path.splitext(i) #splits off the extension. Changed from using string.split() to deal with the dot in version numbers
        extensions.append(file_extension) #using os.path.splittext is easier than doing a regex match twice
        baseNames.append(re.sub("(?i)\s*?((\s*?-\s*?Copy)?\s?(\(\d*\))?)*\s*?$","",filename)+file_extension) #gets rid of "- Copy" and version numbers - extension is added back on for searching

    baseNameDupes = collections.Counter(baseNames) #count duplicates
    duplicates = {}

    for key in baseNameDupes: #getting the original file names
        if baseNameDupes[key] > 1:
            itemIndex = baseNames.index(key) #index of most recent file; dictionary key
            duplicates[files[itemIndex]] = []
            baseNames[itemIndex] = "" #removes the entry from the list
            for i in range(baseNameDupes[key]-1):
                itemIndex2 = baseNames.index(key)
                duplicates[files[itemIndex]].append(files[itemIndex2]) #adds duplicate file names to the dictionary entry
                baseNames[itemIndex2] = "" #removes the entry from the list
    return duplicates #return dictionary


def totalFileSize(dict):
    totalsize = 0 
    for key in dict: #iterates through the dictionary keys
        for i in dict[key]:
            totalsize += os.path.getsize(i) #adds up all the entries in the file name dictionary
    return(totalsize)


def convertBytes(size_input,decimals = 3): #makes bytes bite-sized (resizes units)
    if size_input == 0:
        return "0 B"
    size_types = ['B','KB','MB','GB','TB','PB','EB','ZB','YB'] #units
    power = math.floor(math.log(size_input,1024)) 
    size = round(size_input / math.pow(1024,power),decimals)
    return str(size)+" "+size_types[power] #ouputs a string


def nameGenerator(file_name):
    filename, file_extension = os.path.splitext(file_name)
    count = 0
    base_name = re.sub("\s*?\((\d*)\)\s*?","",filename) #gets rid of version numbers
    while(True):
        files = getFiles()
        new_name = base_name+" ("+str(count)+")"+file_extension #name of new file
        if new_name not in files: #makes sure new file has a unique name
            break
        count += 1
    return new_name
    
def fillStorage(copies): #creates self-duplicates for testing
    count = 1
    for i in range(copies): 
        self_name = os.path.basename(argv[0]) #get name of file
        new_name = nameGenerator(self_name) #name of new file
        print("Creating:",new_name)
        shutil.copy2(argv[0],new_name) #copy file with same metadata


def help(extra_options): #explains the available options
    print("\nname: find duplicates in the current directory according to name")
    print("    Faster and useful for finding older versions")
    print("hash: find duplicates in the current directory according to hash")
    print("    Slower but makes sure it is an exact copy so you don't lose any data")
    if "remove name-dupes" in extra_options: #unlockable options
        print("remove name-dupes: removes duplicate items according to file name")
    if "remove hash-dupes" in extra_options:
        print("remove hash-dupes: removes duplicate items according to file hash")
    print("test: creates duplicates in current directory of this file for testing purposes")
    print("quit: quits the program")
    if "export" in extra_options:
        print("export: exports a text file with a list of duplicates")

def help2():
    # options are ['confirm','cancel','select','remove','refresh','help']
    print("confirm: deletes the files displayed in the list above")
    print("cancel: return to the main menu")
    print("select: select one original file name to remove all duplicates of")
    print("remove: keep a file by removing it from the list to be deleted")
    print("refresh: resets the list to its original state")
    print("quit: quits the program")


def deleteMenu(dict): #input a dictionary, outputs a list
    delete_list = [] #converts the dictionary to a list
    for key in dict:
        for i in dict[key]:
            delete_list.append(i)
    while True:
        print("\nDuplicate files that will be removed:")
        for i in delete_list:
            print(i)
        while True: #my standard options menu loop
            print("\nProceed, or select a file to delete the duplicates for, or remove a particular file from the deletion list")
            list_options = ['confirm','cancel','select','remove','refresh','help']
            print("Your options are:", list_options)
            selection = input()
            if selection.lower() == "quit": #another hidden quit option
                quit()
            if selection.lower() in list_options:
                break
            else:
                print("Your selection could not be recognized. Please try again.")
        
        if selection.lower() == "confirm": #selection tree
            break
        elif selection.lower() == "cancel":
            return []
        elif selection.lower() == "select": #selects a key in the file dictionary to delete all files for
            while True:
                print("\nSelect an original file name to remove the duplicates for")
                print("Type in the file name or type cancel to cancel")
                target_name = input()
                if target_name in dict:
                    delete_list = []
                    for i in dict[target_name]:
                        delete_list.append(i)
                    break
                elif target_name.lower() == "cancel":
                    break
                else:
                    print("Could not find the file in list of originals with duplicates")
        elif selection.lower() == "remove": #allows user to type in the name of a file and remove it from the list
            selecting = True
            while selecting:
                while True:
                    print("\nType the name of the file that you don't want deleted. Type back to go back")
                    list_remove = input()
                    if list_remove in delete_list:
                        break
                    elif list_remove.lower() == "back":
                        selecting = False
                        break
                    else:
                        print("File name not recognized. Try again")
                if selecting:
                    delete_list.remove(list_remove)
                    print("\nDuplicate files that will be removed:")
                    for i in delete_list:
                        print(i)
        elif selection.lower() == "refresh": #reloads the list and gets rid of any changes the user makes
            delete_list = [] #converts the dictionary to a list
            for key in dict:
                for i in dict[key]:
                    delete_list.append(i)
        elif selection.lower() == "help": #help menu nuber 2
            help2()
        else:
            print("You somehow found an option that I forgot to code.") #shouldn't ever be activated
            print("Good job but pick something else")

    return delete_list
    

#excecuting code starts here
#========================================================================================================
#-----------------------get directory stats--------------------------
print("\n==================================================================================================") #startup message
print("===============================PYTHON DUPLICATE FILE FINDER=======================================")
print("==================================================================================================\n")
time.sleep(0.5)

while True:
    if "Downloads" not in os.getcwd(): #directory selection menu appears if you don't run in downloads
        print("You appear to not be running in Downloads")
        print("1. Would you like to use the current directory:",os.getcwd()) #the current working directory
        downloads_path = os.path.expanduser('~')+"\\Downloads" #Fixed to be cross-compatible
        print("2. Would you like to switch to %s" % downloads_path)
        print("3. Or would you like to switch to a custom directory")
        print("Options:",['1','2','3'])
        while True: #loops while the user decides
            dir_choice = input()
            if dir_choice.lower() == "quit": #hidden quit option
                quit()
            if dir_choice in ['1','2','3']: 
                break
            else:
                print("Selection not recognized. Please select from",['1','2','3']) #user error handling
        if int(dir_choice) == 3:
            path=input("Please input a custom path:\n") #custom path input
        elif int(dir_choice) == 2:
            path = downloads_path
        else:
            path = os.getcwd() #changes the working directory
        try: #makes sure the directory is valid
            os.chdir(path)
            break
        except:
            print("Directory could not be opened. Please try again.\n")

    else:
        break

print("\n==============================================STATS===============================================")
dirsize = 0
for i in getFiles(): #counts total size of working directory
    dirsize += os.path.getsize(i)
print("\nThe total size of items in %s is %s" % (os.getcwd(),convertBytes(dirsize)))
total,used,free = shutil.disk_usage(os.getcwd())
print("The files in this directory take up %.4g%% of your total storage, and make up %.4g%% of your total storage usage" % (round(100*dirsize/total,5),round(100*dirsize/used,5)))

files = getFiles()
files.sort(key = os.path.getsize,reverse=True) #finds the biggest file in the directory
print("\nThe largest file in %s is %s at %s" % (os.getcwd(),files[0],convertBytes(os.path.getsize(files[0]))))

print("\nAltogether, your %s of storage is %1.4g%% full" % (convertBytes(total),100*used/total))
print("Used:",percentBar(used,total))

#------------------------options tree---------------------------------
time.sleep(0.7)
options = ["name","hash","test","help","quit"] #main menu options
while(True):
    print("\n------------------------------------------MENU----------------------------------------------------")
    while(True):
        if ("remove name-dupes" in options) and ("remove hash-dupes" in options): #adds and remove the export item
            if "export" not in options:
                options.insert(6,"export")
        else:
            if "export" in options:
                options.remove("export")

        print("\nYour options are:",options)
        user_input = input()

        if user_input.lower() in options: #make sure that the user chooses something from the menu
            break
        else:
            print("Your choice wasn't recognized. Try again")
    #----------------------------options-----------------------------------
    if user_input.lower() == "quit": #quits the program
        print("\nQuitting program....\n")
        time.sleep(0.2)
        quit()
    #---------------------find duplicates by name--------------------------
    elif user_input.lower() == "name":
        print("\n=================================FINDING NAME DUPLICATES==========================================")
        namedupes = nameDuplicates()
        count = 0

        for key in namedupes: #prints out the duplicate files for the user to see
            print("\n%s is the most recent copy of:" % key)
            for i in namedupes[key]:
                print(i)
                count += 1

        print("\nTotal space wasted by",count,"name duplicate files:",convertBytes(totalFileSize(namedupes)))

        options.insert(2,"remove name-dupes")

    elif user_input.lower() == "remove name-dupes": #delete name duplicate files
        deleteFiles(deleteMenu(namedupes))
        options.remove("remove name-dupes") #duplicate files are gone so remove option from menu
        if "remove hash-dupes" in options:
            options.remove("remove hash-dupes")

    #--------------------find duplicates by hash---------------------------
    elif user_input.lower() == "hash":
        print("\n=================================FINDING HASH DUPLICATES==========================================")
        print("\nHashing.... ")
        hashdupes = hashDuplicates()
        count = 0

        for key in hashdupes: #prints out the duplicate files for the user to see
            print("\n%s has %d exact hash duplicates:" % (key,len(hashdupes[key])))
            for i in hashdupes[key]:
                print(i)
                count += 1

        print("\nTotal space wasted by",count,"hash duplicate files:",convertBytes(totalFileSize(hashdupes)))

        if len(hashdupes) > 0:
            options.insert(2,"remove hash-dupes")
    
    elif user_input.lower() == "remove hash-dupes": #delete hash duplicate files
        deleteFiles(deleteMenu(hashdupes))
        options.remove("remove hash-dupes") #duplicate files are gone so remove option from menu
        if "remove name-dupes" in options:
            options.remove("remove name-dupes")
    
    #-------------------------extra options for fun and testing---------------------------
    elif user_input.lower() == "test":
        while True:
            copies = input("\nHow many copies would you like to create?\n")
            if copies.isnumeric(): #make sure the user enters a number
                break
            else:
                print("\nPlease enter a number")
        print("\nCreating duplicates....")
        fillStorage(int(copies))

    elif user_input.lower() == "help": #displays help menu
        help(options)

    elif user_input.lower() == "export": #logs to a .txt file
        fileName = nameGenerator("list_of_duplicates.txt")
        with open(fileName,"w+") as file:
            file.write("Results from %s:\n" % os.getcwd())
            
            file.write("\nHash duplicates:")
            count = 0
            for key in hashdupes: 
                file.write("\n\n%s has %d exact hash duplicates:" % (key,len(hashdupes[key])))
                for i in hashdupes[key]:
                    file.write("\n"+i)
                    count += 1
            file.write("\n\nTotal space wasted by "+ str(count) +" hash duplicate files: "+ convertBytes(totalFileSize(hashdupes)))

            file.write("\n\nName duplicates:")
            count = 0
            for key in namedupes:
                file.write("\n\n%s is the most recent copy of:" % key)
                for i in namedupes[key]:
                    file.write("\n"+i)
                    count += 1
            file.write("\n\nTotal space wasted by"+ str(count) +"name duplicate files: "+ convertBytes(totalFileSize(namedupes)))
            print("\nExported to:",fileName)