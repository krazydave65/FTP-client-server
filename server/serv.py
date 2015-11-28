# *****************************************************
# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import commands
import sys

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







# The port on which to listen
listenPort = 2224

# Create a welcome socket. 
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
serverSocket.bind(('', listenPort))

# Start listening on the socket
serverSocket.listen(1)


# Accept connections forever
while True:
	
	print "Listening on port",serverSocket.getsockname()[1]
		
	# Accept connections
	control_socket, addr = serverSocket.accept()
	
	print "Accepted connection from client: ", addr
	print "\n"


	command = ""
	while command != "quit":
		print "waiting to recv()..."
		command = control_socket.recv(64)
		print "received something buffer..."

		if command == "get":
			print "received get command"
		elif command == "quit":
			pass
		elif command == "put":
			print "received put command"
		elif command == "ls":
			print "received ls command"
			#set up the ephemeral data connection
			print "setting up data connection..."
			welcome_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			welcome_sock.bind(('',0))
			welcome_sock.listen(1)

			ephemeral_port = str(welcome_sock.getsockname()[1]) 
			control_socket.send(ephemeral_port)

			print "data_sock waiting on port",ephemeral_port
			data_sock, data_addr = welcome_sock.accept()
			#========= DATA CONNECTION ESTABLISHED ==========
			print "data connection established!!! :)"

			message = ""
			for line in commands.getstatusoutput('ls')[1:]:
				print line
				message += line + ";"

			data_sock.send(message)



			#========= Close data connection ================
			data_sock.close()
			print "data_sock connection close!"

		elif not command:
			print "unecpected interruption to", addr
			break
		else:
			print "error in message!"

	print "Disconnected from client", addr, "\n"
	control_socket.close()






	# # The buffer to all data received from the
	# # the client.
	# fileData = ""
	
	# # The temporary buffer to store the received
	# # data.
	# recvBuff = ""
	
	# # The size of the incoming file
	# fileSize = 0	
	
	# # The buffer containing the file size
	# fileSizeBuff = ""
	
	# # Receive the first 10 bytes indicating the
	# # size of the file
	# fileSizeBuff = recvAll(clientSock, 10)
		
	# # Get the file size
	# fileSize = int(fileSizeBuff)
	
	# print "The file size is ", fileSize
	
	# # Get the file data
	# fileData = recvAll(clientSock, fileSize)
	
	# print "The file data is: "
	# print fileData
		
	# # Close our side
	# clientSock.close()
	
