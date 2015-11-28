# *******************************************************************
# This file illustrates how to send a file using an
# application-level protocol where the first 10 bytes
# of the message from client to server contain the file
# size and the rest contain the file data.
# *******************************************************************
import socket
import os
import sys

# Command line checks 
# if len(sys.argv) < 2:
# 	print "USAGE python " + sys.argv[0] + " <port>" 

# Server address
serverAddr = "localhost"

# Server port
serverPort = 2224

# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
connSock.connect((serverAddr, serverPort))
print "connected to server!"

# # Open the file
# fileObj = open(fileName, "r")

# # The number of bytes sent
# numSent = 0

# # The file data
# fileData = None

command = ""
while command != "quit":
	command = raw_input("ftp> ")

	connSock.send(command)

	if command == "quit":
		connSock.close()
		sys.exit(1)

	elif command == "ls":
		print "using ls command"
		print "setting up the data connection to receive file listing..."
		#grab the ephemeral port number over the control socket 

		ephemeral_port = int(connSock.recv(64))
		data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		data_sock.connect((serverAddr,ephemeral_port))
		#=========DATA CONNECTION ESTABLISHED==============
		print "done! data_sock connected to the server on port", ephemeral_port

		message = data_sock.recv(64)
		message = message.split(';')
		for list in message:
			print list

		#========== Close data connection =================
		data_sock.close()

	elif command == "get":
		print "using get command"

	elif command == "put":
		print "using put command"







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
			print "data sent fileData["+str(numSent)+"]: ", fileData[numSent:]
			numSent += connSock.send(fileData[numSent:])
			print "numSent: ", numSent, "\n"

	
	# The file has been read. We are done
	else:
		break


print "Sent ", numSent, " bytes."
	
# Close the socket and the file
connSock.close()
fileObj.close()
	


