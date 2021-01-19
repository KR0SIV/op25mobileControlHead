# OP25 Remote Server for the Mobile Control Head

## Server

This server should be run on the same system running OP25 where it will take in commands from the OP25 Mobile Control Head.
Binds to: '0.0.0.0' Binds Port: '10000'

## Client

The client is contained within the mobile control head itself. 
Currently the client is hard coded to port 10000 but will use the OP25 URI stored in the config.ini file.
