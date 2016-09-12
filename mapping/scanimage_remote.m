classdef scanimage_remote < handle
    properties
        sbudp=[];
        remote_port=7000;
        local_port=9090;
        cur_coord=[];
        mmfile=[];
        
        grab_running=0;
        grab_aborted=0;
        
        rotation_mode=0; %1;
        objective_rotation=0;
        focal_point_distance=12.5;
        AP_correction_angle=0;
        % add FOV tilt correction angle => may depend on objective rotation
    end
    
    methods
        function self=scanimage_remote(varargin)
            disp('<<<Custom class to streamline communication with scanimage over UDP>>>')            
            
            % link into memmapped file
            self.mmfile = memmapfile('rscanimage.mmap','Writable',true, 'Format', { 'int16' [1 16] 'header' } , 'Repeat', 1);
        end
        
        %%% MemMap commands
        function is_done=check_grabDone(self)
             status=self.mmfile.Data.header(1);
             if status==-2
                 is_done=1;
                 self.grab_running=0;
             else
                 is_done=0;
             end
        end
        
        %%% UDP commands
        function connect(self,varargin)
            try
                delete(instrfindall)
                handles.cur_coord=[];
                self.sbudp = udp('localhost',self.remote_port,'LocalPort',self.local_port,'BytesAvailableFcn',@self.trajectory_cb,'UserData',handles);
                fopen(self.sbudp);
            catch
                error('Unable to open connection')
            end
            disp('Opened UDP connection to scanimage...')
        end
        
        function send_cmd(self,varargin)
            if strcmpi(self.sbudp.status,'open')
                msg=varargin{1};
                if ~isempty(msg)
                    fprintf(self.sbudp,msg);
                end
            else
                disp('Open connection first...')
            end
        end
        
        function set_folder(self,folder_name)
            self.send_cmd(['A' folder_name])
            self.send_cmd('E000') % reset counter
        end
        
        function set_msg(self,message)
            self.send_cmd(['M' message])
        end
        
        function clear_msg(self,varargin)
            self.send_cmd('C')
        end
        
        function set_AP_correction_angle(self,varargin)
            if nargin==1
                disp('Please provide an input argument...')
            else
                self.AP_correction_angle=varargin{1};
            end
        end
        
        function get_coord(self,varargin)
            self.send_cmd('XR') % self.cur_coord will be updated when reply comes in
            pause(.1)
        end                
        
        function set_coord(self,varargin)             
                          
             if self.rotation_mode
                 
             else
                 
             end
        end
        
        function move_relative(self,varargin)
             move_vector=varargin{1};
             self.get_coord();
             %self.cur_coord
                          
             %for X
             x_step_req=move_vector(1);
             if self.rotation_mode                 
                 alpha=self.objective_rotation/180*pi;
                 x_step=cos(alpha)*x_step_req;
                 z_step_x=sin(alpha)*x_step;
             else
                 x_step=x_step_req;
                 z_step_x=0;
             end                          

             
             %for Y
             y_step_req=move_vector(2);
             if self.rotation_mode
                 alpha=self.AP_correction_angle/180*pi;
                 y_step=cos(alpha)*y_step_req;
                 z_step_y=sin(alpha)*y_step;
             else
                 y_step=y_step_req;
                 z_step_y=0;
             end       
             
             % correct tilt of FOV
             alpha=self.objective_rotation/180*pi;
             x_step_rot=cos(alpha)*x_step+sin(alpha)*y_step;
             y_step_rot=cos(pi-alpha)*y_step+sin(pi-alpha)*x_step;
             x_step=x_step_rot;
             y_step=y_step_rot;
             
             
             %for Z
             z_step_req=move_vector(3);
             if z_step_req~=0
                 if self.rotation_mode
                     alpha=self.objective_rotation/180*pi;
                     z_step_ML=cos(alpha)*z_step_req;
                     x_step_ML=sin(alpha)*z_step_req;
                     
                     z_step=z_step_ML+z_step_x+z_step_y;
                     
                     % adjust steps in X and Y if nec
                     x_step=x_step+x_step_ML;
                 else
                     z_step=z_step_req;
                 end       
             else
                 z_step=z_step_x+z_step_y;
             end
             
             %%% perform moves
             if x_step~=0
                 cmd=sprintf('Px%d',x_step);
                 self.send_cmd(cmd)
             end
             if y_step~=0
                 cmd=sprintf('Py%d',y_step);
                 self.send_cmd(cmd)
             end
             if z_step~=0
                 cmd=sprintf('Pz%d',z_step);
                 self.send_cmd(cmd)
             end
        end
        
        
        function start_grab(self,varargin)
            self.send_cmd('G')
            self.grab_running=1;
            self.grab_aborted=0;
        end
            
        function abort_grab(self,varargin)
            self.send_cmd('S')
            self.grab_running=0;
            self.grab_aborted=1;
        end
        
        
        
        
        
        %%% helper functions
        function trajectory_cb(self,varargin)
            obj=varargin{1};
            E=varargin{2};
            if strcmpi(E.Type,'BytesAvailable')
                s = fgetl(obj);
                if strfind(s,'coord')
                    eval(s);
                    self.cur_coord=coord;
                    self.objective_rotation=coord(4);
                    %elseif
                else
                    fprintf('UDP response "%s" cannot be parsed...',s)
                end
            else
                fprintf('UDP event "%s" cannot be parsed...',E.Type)
            end
        end
    end
end