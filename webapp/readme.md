#To run flash app. python3 app.py
# Visit https://127.0.0.1:8000

# Webapp runs with same functionality as the python cli version
# There are two version of the app.py file. There is app.py and app_auto_purge.py 

#app.py when an image is encoded a copy of the encoded imaged is saved in the uploads folder
#app_auto_purge.py the encoded imaged is purged from the uploads folder after each use. 


#app.py
#aes_key.txt is a rotating text file in the root folder. It gets overwritten each time a new aes_key is generated using the generate aes key button. So it will only save the most recent key that was generated. 

#app_auto_purge.py
#aes_key.txt is purged everytime its created and removed from root folder. Anything in the uploads folder is auto purged every 2 minutes or after a file is decoded. 




#To get started you must make sure you allow tcp traffic on port 8000.
#You can do this on linux with ufw (can be installed with apt install ufw)  or iptables.

#For ufw: 
#sudo ufw allow 8000/tcp 
#sudo ufw enable 
#sudo ufw status (To check that it took) 

#For iptables
#sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
#sudo service iptables save


#Windows 
#You can set to alllow new inbound rule in windows defender firewall. Add inbound TCP port 8000 and allow the connection. 

#MacOS
#Configure firewall options in systems preference window, click on "Security & Privacy" Allow Incoming Connections on macOS
#Step 1: Open System Preferences
#    Click on the Apple logo in the top left corner of your screen.
#    Select "System Preferences" from the dropdown menu.
#Step 2: Open Security & Privacy
#    In the System Preferences window, click on "Security & Privacy."
#Step 3: Go to the Firewall Tab
#    Click on the "Firewall" tab.
#Step 4: Unlock the Settings
#    Click on the lock icon in the bottom left corner of the window.
#    Enter your admin username and password when prompted.
#Step 5: Configure Firewall Options
#    Click on the "Firewall Options" button.
#Step 6: Add an Application
#    Click on the "+" button to add an application.
#    Navigate to your terminal application (typically found in /Applications/Utilities/Terminal.app).
#    Click "Add."
#Step 7: Allow Incoming Connections
#    Ensure that the newly added application (Terminal) is set to "Allow incoming connections."
#    Click "OK" to close the Firewall Options window.
#    Click the lock icon again to prevent further changes.
#Verify Firewall Settings
#  In the "Firewall" tab, ensure that the firewall is turned on and that Terminal is listed as allowed to accept incoming connections.


## TO START THE WEBAPP
## python3 start.py 
#This will guide you through the starting process to choose which version you want to use.
#The start up script will look for a key.pem & cert.pem file in the directory, if one does not exist, it will generate a self-signed cert


#You can now access the webapp at your host ip address: https://hostipaddress:8000
#You will get warning that it is not secure, this is because it is a self-signed certificate. The connection is still encrypted. 



#Additional info: The start.py is generating gunicorn instance for the appropriate app version. The app.py & app_auto_purge.py can be ran as standalone but it will run as flask in developmental webapp on port 5000 or whatever port you speicfy in the app.py or app_purge.py files.



