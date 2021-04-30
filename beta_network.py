import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3 as sq
from tkinter.constants import END, FALSE
from paramiko import client
from tkinter.scrolledtext import ScrolledText
import paramiko
from tkinter import filedialog
from paramiko.client import AutoAddPolicy
import os
from tkinter import simpledialog
import socket
window = tk.Tk()
window.sourceFile = '' 
window.title("Network manager")
window.geometry("1000x480+500+300")
conn = sq.connect('ips.db')
current = conn.cursor()
current.execute('create table if not exists tasks (IP_Adresses)')
ip_addresses = []
#Functions1

def checkIP():
    ip = get_ip.get()
    if len(ip) == 0:
        messagebox.showinfo('Empty Entry', 'Enter an IP address')
    else:
        try :
            socket.inet_pton(socket.AF_INET, ip)
        except AttributeError:
            try:
                socket.inet_aton(ip)
            except socket.error:
                return False
            return ip.count('.') == 3
        except socket.error:
            return False
        return True
        
def addIP():
    ip = get_ip.get()
    if checkIP():
        if ip not in ip_addresses:
            ip_addresses.append(ip)
            current.execute('insert into tasks values (?)', (ip,))
            listUpdate()
            get_ip.delete(0,'end')
        else:
            messagebox.showinfo('Error', 'You entered this IP before')
    else:
        if len(ip) != 0:
            messagebox.showinfo('Error', 'Enter a valid IP address')

def listUpdate():
    clearList()
    for i in ip_addresses:
        t.insert('end', i)

def clearList():
    t.delete(0, 'end')

def delOne():
    try:
        val = t.get(t.curselection())
        if val in ip_addresses:
            ip_addresses.remove(val)
            listUpdate()
            current.execute('delete from tasks where IP_Adresses = ?', (val,))
    except:
        messagebox.showinfo('Cannot Delete', 'No IP Address Selected')
def deleteAll():
    sure = messagebox.askyesno('Delete all', 'Are you sure?')
    if sure == True:
        while(len(ip_addresses) != 0):
            ip_addresses.pop()
        current.execute('delete from tasks')
        listUpdate()
def bye():
    window.destroy()

def retrieveDB():
    while(len(ip_addresses)!=0):
        ip_addresses.pop()
    for row in current.execute('select IP_Adresses from tasks'):
        ip_addresses.append(row[0])

def sshConnect():
    port = 22
    succes = 0
    username = get_username.get()
    password = get_password.get()
    not_succes = 0
    count = 0
    not_suc_list = []
    other_port = get_ssh.get()
    script = get_script.get('1.0', END)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    for i in ip_addresses:
        if os.system(f'ping -c1 -w3 {i} > /dev/null 2>&1') == 0:
            output.insert('end', f'{i} online, try to connect')
            outputUpdate()
            try :
                client.connect(i, port, username, password)
                if client.get_transport().is_active():
                    output.insert('end', f'{i}: ssh connection succesfull on port 22')
                    outputUpdate()
                    client.exec_command(script)
                    output.insert('end', f'Script successfully uploaded to the server')
                    outputUpdate()
                    succes +=1
                    client.close()
            except paramiko.ssh_exception.AuthenticationException:
                output.insert('end', 'Bad username or password')
                outputUpdate()
                not_suc_list.append(i)
                not_succes +=1
            except paramiko.ssh_exception.NoValidConnectionsError:
                #not_succes += 1
                #not_suc_list.append(i)
                try:
                    if len(get_ssh.get()) != 0:
                        output.insert('end', f'{i}: ssh connect faild on port 22, try on {other_port}')
                        outputUpdate()
                        client.connect(i, other_port, username, password)
                        if client.get_transport().is_active():
                            output.insert('end', f'{i}: ssh connect succesfull on port {other_port}')
                            outputUpdate()
                            client.exec_command(script)
                            output.insert('end', f'Script successfully uploaded to the {i} host ')
                            outputUpdate()
                            succes += 1
                            client.close()
                except paramiko.ssh_exception.AuthenticationException:
                    output.insert('end', 'Bad username or password')
                    outputUpdate()
                    not_succes +=1
                    not_suc_list.append(i)
                except paramiko.ssh_exception.NoValidConnectionsError:
                    output.insert('end', 'Could not connect to ssh server')
                    outputUpdate()
                    not_succes +=1
                    not_suc_list.append(i)
        else:
            output.insert('end', f'{i} Host is down')
            outputUpdate()
            not_suc_list.append(i)
            not_succes +=1
        count +=1
    output.insert('end', f'Could not connect: {not_succes} hosts, {not_suc_list}')
    outputUpdate()
    output.insert('end', f'Succes: {succes} host of {count}')
    outputUpdate()
    

def scriptUpload():
    if (get_script.compare("end-1c", "==", "1.0")):
        messagebox.showinfo('Empty', 'You did not entered any script to upload')
    elif (len(get_username.get()) == 0 ):
        messagebox.showinfo('Empty', 'You did not entered username')
    elif (len(get_password.get()) == 0 ):
        messagebox.showinfo('Empty', 'You did not entered password')
    else:
        sshConnect()

    
def clearOutput():
    output.delete('0', END)
def clearBox():
    get_script.delete('1.0', END)
def Help():

    messagebox.showinfo('Help', 'Simple network manager for multi addresses. If you want upload the same config to multiple device via ssh, just enter theire IP Addresses, your credentials and the script.\n If you are using other port to ssh, you can use it, but not neccesarry! \n You have to use the same login credentials on the devecies is you want update them at the same time')

def outputUpdate():
    output.update()

def backupScript():
    ftp = simpledialog.askstring("Input", "FTP szerver IP címe:", parent=window)
    username = simpledialog.askstring("Input", "FTP szerver username:", parent=window)
    password = simpledialog.askstring("Input", "FTP szerver password:", parent=window)

    script = f'/system scheduler add interval=1w name=hetimentes on-event=backup policy=ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon start-time=startup'
    script1 = f'/system script add dont-require-permissions=no name=backup owner={username} policy=ftp,reboot,read,write,policy,test,password,sniff,sensitive,romon source=":global backupname (\\\"BACKUP\\".\\"-\\".[/system identity get name].\\".rsc\\");\\nexport compact file=\\$backupname\\n/tool fetch address={ftp} mode=ftp user={username} password={password} src-path=\\$backupname dst-path=\\"mentesek/\\$backupname\\" upload=yes"'
    script2 = f'/system script run backup'
    get_script.insert(tk.INSERT, script, tk.INSERT, "\n",  tk.INSERT, script1, tk.INSERT, "\n", tk.INSERT, script2)
#def chooseFile():
    #window.sourceFile = filedialog.askopenfilename(parent=window, initialdir= "/home/fuszi", title='Please select a directory')
    #f = open (window.sourceFile, 'r')
    #script = f.read()
    #get_script.insert(tk.INSERT, script)

#Functions2
l1 = ttk.Label(window, text = 'Network Manager version 1.0')
l2 = ttk.Label(window, text = 'Enter IP Addresses')
get_ip = ttk.Entry(window, width = 21)
t = tk.Listbox(window, height=10, selectmode='SINGLE')
output = tk.Listbox(window, height = 19, width = 45, selectmode='SINGLE')
button1 = ttk.Button(window, text='Add IP', width=20, command=addIP)
button2 = ttk.Button(window, text='Delete', width=20, command=delOne)
button3 = ttk.Button(window, text='Delete All', width=20, command=deleteAll)
button4 = ttk.Button(window, text='Exit', width=20, command=bye)
button5 = ttk.Button(window, text='Script upload', width=20, command=scriptUpload)
button6 = ttk.Button(window, text='Clear script input box', width=20, command=clearBox)
button7 = ttk.Button(window, text='Clear output box', width=20, command=clearOutput)
button8 = ttk.Button(window, text='Help', width=20, command=Help)
button9 = ttk.Button(window, text='Backup to FTP', width=15, command=backupScript)
button10 = ttk.Button(window, text='ADD MAC to ARP')
get_script = ScrolledText(window, width=40, height=5)
l3 = ttk.Label(window, text='Username: ', width=13)
l4 = ttk.Label(window, text='Password: ', width=13)
l5 = ttk.Label(window, text='Other ssh Port: ', width=13)
l6 = ttk.Label(window, text='Enter your script to upload or select one from the list')
l7 = ttk.Label(window, text='IPs:')
get_username = ttk.Entry(window, width=15)
get_password = ttk.Entry(window, width=15)
get_ssh = ttk.Entry(window, width=15)
retrieveDB()
listUpdate()

#place things
get_username.place(x=155, y=260)
get_password.place(x=155, y=280)
get_ssh.place(x=155, y=300)
get_ip.place(x=45, y=80)
get_script.place(x=45, y=350)
t.place(x=220, y = 58)
l7.place(x=222, y=40)
l6.place(x=45, y=330)
l5.place(x=45, y=300)
l4.place(x=45, y=280)
l3.place(x=45, y=260)
l2.place(x=45, y=50)
l1.place(x=45, y=10)
button1.place(x=45, y=110)
button2.place(x=45, y=140)
button3.place(x=45, y=170)
button4.place(x=45, y =200)
button5.place(x=45, y = 230)
button6.place(x=130, y=450)
button7.place(x=720, y=450)
button8.place(x=820, y=20)
button9.place(x=450, y=70)
button10.place(x=455, y=110)
output.place(x=620, y = 58)

if __name__ == "__main__":
    window.mainloop()
    conn.commit()
    current.close()