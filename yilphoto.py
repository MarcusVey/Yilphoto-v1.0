import os
import sys
import ftplib
import shutil
import json
import re
from datetime import datetime as dt
from time import sleep

def yilphotoMain():
    
    # Fetch dynamic variables from json configuration file

    with open("config.json", "r") as f:
        config = json.load(f)

    hosts = config[0]["hosts"]
    paths = config[1]["paths"]
    ports = config[2]["ports"]
    users = config[3]["users"]

    user = users["username"]
    pw = users["password"]
    port = ports["ftp"]
    localpath = paths["localpath"]
    remotepath = paths[r"remotepath"]

    ftpserver = ftplib.FTP()

    for host in hosts.values():
        yilphotoConnect(host, user, pw, port, ftpserver)
        yilphotoSync(localpath, remotepath, ftpserver)

    ftpserver.quit()

    # yilphotoAutosort(localpath)

def yilphotoConnect(host, user, pw, port, ftpserver):

    # Connect to the hosts, throw an exception of connection fails

    try:
        ftpserver.connect(host, port=port)
        ftpserver.login(user, pw)
        print("\n\nConnection succeeded to", host, "\n")
    except ftplib.all_errors as Err:
        print("Connection failed to", host, "due to", Err, "\n")
        quit()

def yilphotoSync(localpath, remotepath, ftpserver):
    
    # Create two empty lists, these will store remote and local images later
    # Build the local list of images (The list on the NAS)

    def getLocalList(localpath):

        print("Building local directory file list... \n")
        # create a list of file and sub directories 
        # names in the given directory
        listOfFile = os.listdir(localpath)
        list_local = list()
        # Iterate over all the entries
        for entry in listOfFile:
            # Create full path
            fullPath = os.path.join(localpath, entry)
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(fullPath):
                list_local = list_local + getLocalList(fullPath)
            else:
                head, tail = os.path.split(fullPath)
                list_local.append(tail)

        return list_local

    # Build the remote list of images (The list on the phone)

    def getRemoteList(remotepath, ftpserver):

        list_remote = list()
        ftpserver.cwd(remotepath)
        print("Building remote directory file list...")

        for rfile in ftpserver.nlst():
            if rfile.endswith('.jpg'):
                list_remote.append(rfile)

        return list_remote

        # Compare the contents of the two lists       

    list_difference = sorted(list(set(getRemoteList(remotepath, ftpserver)) - set(getLocalList(localpath))))

    if list_difference == []:
        print("All files are already synced\n")
    else:
        print("Found the following files in remote path:")
        print(list_difference, "\n")
        print("Syncing them now\n")

    # Download all the files that were missing from the remote list to the local path
    # i.e sync files so the two lists match

    for l in list_difference:
        with open(os.path.join(localpath, l), 'wb') as ftpfile:
            s = ftpserver.retrbinary('RETR ' + l, ftpfile.write, 204800)
            print("Processing" + ' ' + l)
            if str(s).startswith('226'):
                print("Success\n")
            else:
                print(s)

    # Close connection when finished and enter wait mode

def yilphotoAutosort(rootpath):

    year = dt.now().year
    year = str(year)
    folder_path = rootpath + '/' + year
    prere1 = re.compile(r"^[a-zA-Z]{5,8}")
    prere2 = re.compile(r"^[a-z]{5,8}\_[a-z]{5,8}")
    datere = re.compile(r"(\d{8}\_\d{6})")
    prefixre = re.compile(r"-IMG_")

    os.chdir(folder_path)

    def monthConversion(smonth):

        return {
                '01' : '1. JANUARI ' + year,
                '02' : '2. FEBRUARI ' + year,
                '03' : '3. MARS ' + year,
                '04' : '4. APRIL ' + year,
                '05' : '5. MAJ ' + year,
                '06' : '6. JUNI ' + year,
                '07' : '7. JULI ' + year,
                '08' : '8. AUGUSTI ' + year,
                '09' : '9. SEPTEMBER ' + year,
                '10' : '10. OKTOBER ' + year,
                '11' : '11. NOVEMBER ' + year,
                '12' : '12. DECEMBER ' + year
        } [smonth]

    for file in os.listdir(folder_path):

        if os.path.isfile(file) and file.endswith('.jpg'):
                
            prefix_split = prefixre.split(file, maxsplit=1)

            try:
                nmonth = prefix_split[1][4:6]
                day = prefix_split[1][6:8]
                prefix = prefix_split[0]
            except IndexError as Err:
                print(Err, '- IndexError, could not split out prefix from', file)
                
            if prefixre.search(file) != None and datere.search(file) != None and prere1.search(file) or prere2.search(file) != None:

                image_path = monthConversion(nmonth) + '/' + day + '/' + prefix

                try:
                    os.makedirs(folder_path + '/' + image_path)
                    print('\n' + folder_path + '/' + image_path, "does not exist, creating directory.")
                except:
                    pass

                try:
                    shutil.move(file, folder_path + '/' + image_path)
                    print("\nMoving", file, "to", folder_path + '/' + image_path)
                except:
                    pass

            elif datere.search(file) != None:

                r1 = datere.split(file)

                month = r1[1][4:6]
                day = r1[1][6:8]

                unsort_path = monthConversion(month) + '/' + day + '/Ej sorterbart/'

                try:
                    os.makedirs(folder_path + '/' + unsort_path)
                    print('\n' + folder_path + '/' + unsort_path, "does not exist, creating directory.")
                except:
                    pass

                try:
                    shutil.move(file, folder_path + '/' + unsort_path)
                    print("\nMoving", file, "to", folder_path + '/' + unsort_path)
                except:
                    pass

            else:
                pass

if __name__ == "__main__":
    yilphotoMain()