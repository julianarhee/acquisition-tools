% connect to the server
t = udp('localhost', 2002);
fopen(t);

% write a message
fwrite(t, 'This is a test message.');

% read the echo
bytes = fread(t, [t.BytesAvailable, 1], 'char');
temp = reshape(bytes, [8 6]);
z = [0,0,0,0,0,0]
for col = 1:6
        bytepack=uint64(0);
        for row = 1:8
                temp(9-row, col)
                bytepack = bitshift(temp(9 - row, col),8*(8-row));
                z(col) = bitor(bytepack,z(col));
                temp(row, col);
        end;
end;

% close the connection
fclose(t);