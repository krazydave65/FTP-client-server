# *****************************************************
# This file implements a server for receiving the file
# sent using sendfile(). The server receives a file and
# prints it's contents.
# *****************************************************

import socket
import commands
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


def validFile(filename):
	if os.path.isfile(filename): 
		return True
	else:	
		print "file does not exist!!!!"
		return False






if len(sys.argv) < 2:
	print "USAGE python " + sys.argv[0] + " <PORT NUMBER>" 


# The port on which to listen
listenPort = int(sys.argv[1])

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


	command = ""
	while command != "quit":
		print "\nwaiting for request..."
		command = control_socket.recv(64)



		if len(command.split()) == 2:
			command, filename = command.split()

			# if command == "get":
			# 	# Check if filename does not exists
			# 	if not validFile(filename):
			# 		print "[client] requested file '",filename,"' does not exist"
			# 		control_socket.send("FALURE: File '",filename,"' does not exist in server")
			# 		continue

		elif len(command.split()) == 1:
			pass



		# print "received something buffer..."

		#check for command
		if command == "get":
			welcome_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			welcome_sock.bind(('',0))
			welcome_sock.listen(1)

			ephemeral_port = str(welcome_sock.getsockname()[1])
			control_socket.send(ephemeral_port)

			#wait for client to connect
			data_sock, data_addr = welcome_sock.accept()
			#========= DATA CONNECTION ESTABLISHED ==========
			
			if not os.path.isfile(filename):
				message = "0000000039BAD: file '"+filename+"' does not exist!!!"
				print message
				data_sock.send(message)
			else:
				
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
						
						# print "original fileData: ",fileData,"\n\n"
						# Get the size of the data read
						# and convert it to string
						dataSizeStr = str(len(fileData))
						# print "original dataSizeStr: ", dataSizeStr
						
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
						# print "prepended 10 bytes len(filedata): ", len(fileData), '--------'
						while len(fileData) > numSent:
							# print "data sent fileData["+str(numSent)+"]: ", fileData[numSent:]
							numSent += data_sock.send(fileData[numSent:])
							# print "numSent: ", numSent, "\n"

					
					# The file has been read. We are done
					else:
						break



				print "Sending '" + filename + "' from client <----- server"
				print "["+str(numSent)+ "bytes transfered]"
				# Close the socket and the file
				fileObj.close()
	
			
			#========= Close data connection ================
			data_sock.close()

		elif command == "quit":
			pass
		elif command == "put":
			#set up the ephemeral data connection
			welcome_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			welcome_sock.bind(('',0))
			welcome_sock.listen(1)

			ephemeral_port = str(welcome_sock.getsockname()[1]) 
			control_socket.send(ephemeral_port)

			data_sock, data_addr = welcome_sock.accept()
			#========= DATA CONNECTION ESTABLISHED ==========

			# Receive the first 10 bytes indicating the
			# size of the file
			fileSizeBuff = recvAll(data_sock, 10)
				
			# Get the file size
			fileSize = int(fileSizeBuff)
						
			# Get the file data
			fileData = recvAll(data_sock, fileSize)
			newFile = open(filename, "wb");
			newFile.write(fileData)
			newFile.close()
			print "copying '", filename, "' from client --> local directory"
			print "["+str(fileSize)+" bytes received]"
			#========= Close data connection ================
			data_sock.close()


		elif command == "ls":
			print "[client] requesting 'ls command'"
			#set up the ephemeral data connection
			# print "setting up data connection..."
			welcome_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			welcome_sock.bind(('',0))
			welcome_sock.listen(1)

			ephemeral_port = str(welcome_sock.getsockname()[1]) 
			control_socket.send(ephemeral_port)

			# print "data_sock waiting on port",ephemeral_port
			data_sock, data_addr = welcome_sock.accept()
			#========= DATA CONNECTION ESTABLISHED ==========
			# print "data connection established!!! :)"
			
			message = ""
			for line in commands.getstatusoutput('ls')[1:]:
				message += line + ";"

			data_sock.send(message)
			print "[server] responding with 'ls command' results"

			#========= Close data connection ================
			data_sock.close()

		elif not command:
			print "unecpected interruption to", addr
			break
		else:
			print "error in message!"

	print "Disconnected from client", addr, "\n"
	control_socket.close()



