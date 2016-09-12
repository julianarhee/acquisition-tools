%% Example of UDP connection:
% from:
% https://machinelearning1.wordpress.com/2012/05/21/how-to-sendreceive-data-in-a-2-way-udp-connection-using-matlab/

delete(instrfindall)
clear all

% 1.  Define the ip and port for both PCs:

% UDP data buffer
data=zeros(2,1);
Ress=zeros(1);
flag=[];
% Define computer-specific variables
ipA = '140.247.178.213';
portA = 9090; % Modify these values to be those of your first computer.
ipB = '140.247.178.213';
portB = 9095; % Modify these values to be those of your

% 2.  Open the session:

udpA = udp(ipB,portB,'LocalPort',portA);      % Define UDP
fopen(udpA);      % Open the ports

%%
% 3. Make some loops to receive, calculate and send data inside:

fprintf(udpA,'%f','Test - are you there. B?');
data=fscanf(udpA, '%f');     % listen to port

%%
while isempty(flag)==1      % loop until receiving Terminator code
    
    while get(udpA,'BytesAvailable')==0      % loop untile receive something
        data=fscanf(udpA, '%f');     % listen to port
    end
    disp(['Data Received - ' , '[',num2str(data(1,1)) , ' ', num2str(data(2,1)),']']);
    %Ress=evalfis(data',FIS);      % use received data to make result
    Ress = data;
    disp('Calculation Done. Sending result...');
    %Ress = input('send msg:');
    
    while get(udpA,'ValuesSent') == 0      % loop until the result is sent
        fprintf(udpA,'%f',Ress);      % sending on port
    end
    disp(['data sent - ' , num2str(Ress)]);
    
    %set(udpA,'BytesAvailable',0);      % initialize the receiving loop
    data=zeros(2,1);      % initialize buffer
    
    if data(1,1)==999 && data(2,1)==999      % check for Terminate Code
        flag=0;      % if YES make the termination flag on
        disp(['Terminate Request received from ',ipB]);
    end
    
end

% 4.  Close port and delete obj from memory:

fclose(udpA);       % Close the session</span>
delete(udpA);      % delete the object from memory</span>
clear ipA portA ipB portB udpA

