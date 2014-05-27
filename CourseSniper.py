import sys, time, mechanize, getpass, multiprocessing, os, urllib2, base64

# Program name - CourseSniper.py
# Written by - Mohammed Madhi Davoodi (mdavoodi@vt.edu)
# Date and version No:  24/04/2012 Ver 1.2

# CourseSniper is a script written using mechanize which automates the process of
# checking for and adding classes in HokieSpa. The user specifies a CRN and CourseSniper
# will check and see if the class is open. If the class is open it will add the class(
# Make sure you have ran Setup first to setup your login credential's!).

# Features:
# -  Adding classes by CRN.
# -  CourseSniper supports checking for multiple classes at once using multiprocessing.
# -  Will show current processes running in the jobs list.
# -  Logs the results of all operations in Logs.


# Clears the screen based on the OS. Does not work in Eclipse.
def cls():
    os.system('cls' if os.name=='nt' else 'clear') 

# Prints all the current tasks running.
def jobs():
    tasks = multiprocessing.active_children()
    if len(tasks) == 0:
        print "No jobs currently running"
    else: 
        for line in tasks:
            print line  
    raw_input("Press ENTER to continue...")
    
    
def dropAdd(crnToDrop, crnToAdd):
    global messages # Give us access to messages which stores the log.
    # Start browser.
    br = mechanize.Browser();
    # Allow access to site even if robots are disabled(may be unethical).
    br.set_handle_robots(False)
    br.set_handle_equiv(False) 
    # Allow redirects.
    br.set_handle_redirect(True)
    # Attempt to got to login page.
    try:
        br.open("https://banweb.banner.vt.edu/ssb/prod/twbkwbis.P_WWWLogin")
        br.follow_link(text="Login to HokieSpa >>>", nr = 0)
        br.select_form(nr = 0)
        br["username"] = username;
        # Decode the password.
        br["password"] = base64.standard_b64decode(password);
        # Submit the page(login).
        br.submit()
        # Open the registration page.
        br.open("https://banweb.banner.vt.edu/ssb/prod/hzskstat.P_DispRegStatPage");
        # If the login failed this code wont work.
    except:
        messages.append("Login failed.")
        dropAdd(crnToDrop, crnToAdd)

        # Look for the link called Drop/Add. Pick the 5th one(VT's sites are designed badly. No unique ID).
    br.follow_link(text="Drop/Add", nr = 0)
    br.select_form(nr = 1)
    index = 0;
    found = False
    for control in br.controls:
        if (control.value == crnToDrop):
            found = True
            break
        else:
            index = index + 1
    if (found == True):
        control = br.find_control(nr = index - 2)
        control.readonly = False
        control.value = ["DW"]       
        # Select control for adding class.
        control = br.find_control(id = "crn_id1")
        # Enable editing in the box.
        control.readonly = False;
        # Set the value of the box.
        control._value = crnToAdd
        response = br.submit()
        string = response.get_data()
        if "Registration Errors" in string:
            return False
        else:
            return True
    else:
        return False

    
    
    
def ReplaceClass(crnToDrop, crnToAdd):
    global messages
    campCRN(crnToAdd)
    result = dropAdd(crnToDrop, crnToAdd)
    if(result == False):
        result = addClass(crnToDrop)
        if(result == False):
            messages.append("Failed to substitute class " + crnToDrop + " for " + crnToAdd + " readd failed...")
        else:
            messages.append("Failed to substitute class " + crnToDrop + " for " + crnToAdd + " readd succeeded!")
    else:
        messages.append("Class substitute of " + crnToDrop + " for " + crnToAdd + " succeeded!")
        

# Adds the class specified by the crn field.
# @param crn: The crn of the class to add.
# @return: True if the class was added. False if there was an error. 
def addClass(crn):
    global messages # Give us access to messages which stores the log.
    # Start browser.
    br = mechanize.Browser();
    # Allow access to site even if robots are disabled(may be unethical).
    br.set_handle_robots(False)
    br.set_handle_equiv(False) 
    # Allow redirects.
    br.set_handle_redirect(True)
    # Attempt to got to login page.
    try:
        br.open("https://banweb.banner.vt.edu/ssb/prod/twbkwbis.P_WWWLogin")
        br.follow_link(text="Login to HokieSpa >>>", nr = 0)
        br.select_form(nr = 0)
        br["username"] = username;
        # Decode the password.
        br["password"] = base64.standard_b64decode(password);
        # Submit the page(login).
        br.submit()
        # Open the registration page.
        br.open("https://banweb.banner.vt.edu/ssb/prod/hzskstat.P_DispRegStatPage");
        # If the login failed this code wont work.
    except:
        messages.append("Login failed.")
        addClass(crn)
    try:
        # Look for the link called Drop/Add. Pick the Nth one(VT's sites are designed badly. No unique ID).
        br.follow_link(text="Drop/Add", nr = 0)
        br.select_form(nr = 1)
        control = br.find_control(id = "crn_id1")
        # Enable editing in the box.
        control.readonly = False;
        # Set the value of the box.
        control._value = crn
        response = br.submit()
        string = response.get_data()
        if "Registration Errors" in string:
            return False
        else:
            return True
    except:
	addClass(crn)
        return False
    
# Terminates all the running processes    
def terminate():
    for process in processes:
        if (process.is_alive()):
            process.terminate()
    sys.exit()
    
def addClassByCRN(crn, messages):
    campCRN(crn)
    # Class was found, add it.
    result = addClass(crn)
    if(result == True):
        messages.extend([crn +  " successfully added."])
    else:
        messages.extend([crn + " failed to add."])    
        
# Checks to see if the specified crn is open.
# @param crn: The crn of the course we are checking to see is open
# @param messages: the log file for the call.
def campCRN(crn):
    global messages
    br = mechanize.Browser();
    br.set_handle_robots(False);
    br.set_handle_equiv(False) 
    # Load the Timetable.
    try:
        br.open("https://banweb.banner.vt.edu/ssb/prod/HZSKVTSC.P_ProcRequest");
    except:
        campCRN(crn)
    found = False
    # Loop until the class is open.
    while(found != True):
        try:
	    br.select_form(nr = 0);
	    br["open_only"] = ["on"]
	    br["TERMYEAR"] = ["201401"]
	    br["crn"] = crn;
	    string = ""
	    # Try except to be used to try and catch all HTTP errors.
            response = br.submit()
            string = response.get_data()
        except urllib2.HTTPError, e:
            messages.extend([crn + " got HTTP " +str(e.code) + " error."])
            continue         
        if "NO SECTIONS FOUND FOR THIS INQUIRY." in string:
            found = False
            time.sleep(30)
        else:
            found = True
    
# Set's up account to be used to add the class.    
def setup():
    global username
    username = raw_input("Enter your PID: ")
    global password
    password = base64.standard_b64encode(getpass.getpass("Enter your password: "))
    confirm = base64.standard_b64encode(getpass.getpass("Confirm your password: "))
    if(password == confirm):
        print 'Setup Successful'
    else:
        print "Password did not match."
        setup()
    raw_input("Press ENTER to continue...")   

# Prints the log.
def log():
    global messages
    if len(messages) == 0:
        print "Nothing Added yet"
    else: 
        for line in messages:
            print line  
    raw_input("Press ENTER to continue...")  
    
    
# Brings up the main screen.
def main():
    global messages, processes
    print "Welcome to CourseSniper 1.2"
    print "What would you like to do?"
    print "1. Add class by CRN"
    print "2. Replace Class by CRN"
    print "3. Log"
    print "4. Jobs"
    print "5. Setup"
    print "6. Exit"
    var = raw_input("Input the command you want to do's number: ")
    if (var == "1"):
        cls()
        CRN = raw_input("Enter the CRN of the class you want to add: ")
        service = multiprocessing.Process(name='addClassByCRN_' + CRN, target=addClassByCRN, args=(CRN, messages))
        service.start()
        processes.append(service)
        print "CRN added to jobs list."
        raw_input("Press ENTER to continue...")
        cls()
        main()
        
    elif (var == "2"):
        cls()
        crnToDrop = raw_input("Enter the CRN of the class you want to drop: ")
        crnToAdd = raw_input("Enter the CRN of the class you want to add: ")
        service = multiprocessing.Process(name='ReplaceClassByCRN_' + crnToDrop + '_with_' + crnToAdd , 
                                          target=ReplaceClass, args=(crnToDrop, crnToAdd))
        service.start()
        processes.append(service)
        print "Replace added to jobs list."
        raw_input("Press ENTER to continue...")
        cls()
        main()
        
    elif (var == '3'):
        cls()
        log()
        cls()
        main()

    elif (var == '4') :
        cls()
        jobs()  
        cls()
        main()
           
    elif (var == "5"):
        cls()
        setup()
        cls()
        main()
        
    elif (var == "6"):
        terminate()
    
    else:
        print 'Invalid Input.'
        time.sleep(1)
        cls()
        main()
                
if __name__ == '__main__':
    # List of all processes ever ran.
    processes = []
    # Manager to use to manage all the process's
    manager = multiprocessing.Manager()
    # Default username
    username = ''
    # Default password
    password = ''
    # Set up a list using manager that all processes can have access too.
    messages = manager.list()
    main()



