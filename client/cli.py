# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys
import os.path

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):

	# The buffer
	recvBuff = ""
	
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes)
		
		# The other side has closed the socket
		if not tmpBuff:
			break
		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
	
	return recvBuff



# ************************************************
# Receives the userInput command
# @param userInput - "get/put <filename>" or "ls" or "quit"
# @return - true or false if command is valid
# *************************************************
def validInputChecker(userInput):
	command_line = userInput.split()
	cmd = command_line[0]

	if cmd == 'get' or cmd == 'put': 
		if len(command_line) == 2:
			fileName = command_line[1]
			print cmd + ", " + fileName
			return True
		else: 
			print "-wrong amount of arguments for '" + cmd + "'"

	elif cmd == 'ls':
		if len(command_line) == 1:
			return True
		else: 
			print "-wrong amount of arguments for '" + cmd + "'"

	else:
		print "-Invalid Input. The command '" + userInput + "' not found"

	return False


def validFile(filename):
	if os.path.isfile(filename): 
		return True
	else:	
		print "file does not exist!!!!"
		return False



# Command line checks 
if len(sys.argv) < 3:
	print "USAGE python " + sys.argv[0] + "<Server IP> <port #>" 

# Server address
serverAddr = str(sys.argv[1])

# Server port
serverPort = int(sys.argv[2])

# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
connSock.connect((serverAddr, serverPort))
print "connected to server!"

command = ""
while command != "quit":
	command = raw_input("ftp> ")


	#=== Check if input information is valid =========
	validInput = validInputChecker(command)

	if len(command.split()) == 2:
		cmd, filename = command.split()
		if cmd == "put":
			# Check if filename does not exists
			if not validFile(filename):
				print "The file '",filename,"' does not exist"
				continue


	elif len(command.split()) == 1:
		cmd = command

	if not validInput:
		continue 

	# ==================================================



	#Send Command ---> Server via socket
	connSock.send(command)



	if cmd == "quit":
		connSock.close()
		sys.exit(1)

	elif cmd == "ls":
		#print "setting up the data connection to receive file listing..."
		#get the ephemeral port number over the control socket 

		ephemeral_port = int(connSock.recv(64))

		data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		data_sock.connect((serverAddr,ephemeral_port))
		#=========DATA CONNECTION ESTABLISHED==============
		# print "done! data_sock connected to the server on port", ephemeral_port

		message = data_sock.recv(64)
		message = message.split(';')
		for list in message:
			print list

		#========== Close data connection =================
		data_sock.close()

	elif cmd == "get":
		print "using get command"
		ephemeral_port = int(connSock.recv(64))

		data_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		data_sock.connect((serverAddr,ephemeral_port))
		#========= DATA CONNECTION ESTABLISHED ==========


		#Receive first 10 bytes indicating the size of the file
		fileSizeBuff = recvAll(data_sock,10)

		print "fileSizeBuff: ", fileSizeBuff
		#get the file size
		fileSize = int(fileSizeBuff)

		# Get the file data
		fileData = recvAll(data_sock,fileSize)


		newFile = open(filename,"wb")
		newFile.write(fileData)
		newFile.close()
		print "copying '", filename, "' from local directory <------ server"
		#========= Close data connection ================
		data_sock.close()


	elif cmd == "put":

		print "using put command"
		print "setting up the data connection to receive file listing..."
		#grab the ephemeral port number over the control socket 

		ephemeral_port = int(connSock.recv(64))
		data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		data_sock.connect((serverAddr,ephemeral_port))
		#=========DATA CONNECTION ESTABLISHED==============
		print "done! data_sock connected to the server on port", ephemeral_port

		# Open the file
		fileObj = open(filename, "r")

		# The number of bytes sent
		numSent = 0

		# The file data
		fileData = None

		# Keep sending until all is sent
		while True:
			
			# Read 65536 bytes of data
			fileData = fileObj.read(65536)
			
			# Make sure we did not hit EOF
			if fileData:
				
				print "original fileData: ",fileData,"\n\n"
				# Get the size of the data read
				# and convert it to string
				dataSizeStr = str(len(fileData))
				print "original dataSizeStr: ", dataSizeStr
				
				# Prepend 0's to the size string
				# until the size is 10 bytes
				while len(dataSizeStr) < 10:
					dataSizeStr = "0" + dataSizeStr
			
			
				# Prepend the size of the data to the
				# file data.
				fileData = dataSizeStr + fileData	
				
				# The number of bytes sent
				numSent = 0
				
				# Send the data!
				print "prepended 10 bytes len(filedata): ", len(fileData), '--------'
				while len(fileData) > numSent:
					# print "data sent fileData["+str(numSent)+"]: ", fileData[numSent:]
					numSent += data_sock.send(fileData[numSent:])
					# print "numSent: ", numSent, "\n"

			
			# The file has been read. We are done
			else:
				break


		print "Sent ", numSent, " bytes."
			
		# Close the socket and the file
		fileObj.close()
			
		#========== Close data connection =================
		data_sock.close()




