  
1. Please choose one of following programing languages: C, C++， Java, Python;  
2. LFTP should use a client-server service model;  
3. LFTP must include a client side program and a server side program;  
- Client side program can not only send a large file to the server but also download a file from the server.  
    - Sending file should use the following format：LFTP lsend myserver mylargefile  
    - Getting file should use the following format：LFTP lget myserver mylargefile  
- The parameter myserver can be a url address or an IP address.  
4. LFTP should use UDP as the transport layer protocol.  
5. LFTP must realize 100% reliability as TCP;  
6. LFTP must implement flow control function similar as TCP;  
7. LFTP must implement congestion control function similar as TCP;  
8. LFTP server side must be able to support multiple clients at the same time;  
9. LFTP should provide meaningful debug information when programs are executed.  