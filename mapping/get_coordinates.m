% makes grids around a specific coordinate
% relies on you defining an ETL stack in scanbox
% setting laser power and number of planes and frames
% will move to new position and hit grab for you
% will wait until stack is collected and move to next position
% enjoy!

clear all
clc

sir = scanimage_remote();
sir.connect()

%%
sir.get_coord;
sir

%%
sir.set_AP_correction_angle(0) % no correction angle

%%
radius_X = 2; % number of tile rings
radius_Y = 2; % number of tile rings

FOV_size = [100 100]; %[760 714];
percentage_overlap = 30;
step_size_x = round(FOV_size(1)*(100-percentage_overlap)/100);
step_size_y = round(FOV_size(2)*(100-percentage_overlap)/100);

if 0
    %%
    sir.move_relative([step_size_y step_size_y*0 0])
end

[X,Y] = meshgrid(-radius_X*step_size_x:step_size_x:radius_X*step_size_x, -radius_Y*step_size_y:step_size_y:radius_Y*step_size_y);
even=2:2:size(Y,1);
Y(:,even)=flipud(Y(:,even)); % make snake
tile_coordinate=[Y(:) X(:) X(:)*0];
tile_coordinate=[0 0 0 ; 0 0 0 ; tile_coordinate ; 0 0 0]; % start and stop at current coordinate

% This assumes starting movement traj at END of desired grid (?)
% Then, goes back to START of grid.
move_matrix=diff(tile_coordinate) 
nTiles=size(move_matrix,1);
%%
sir.clear_msg()

dry_run=0; % test first all moves
for iTile=1:nTiles
    % doing tile xxx
    sir.set_folder(sprintf('Tile_%03d',iTile))
    pause(.5)
    
    % move to new position
    relative_move=move_matrix(iTile,:);
    sir.move_relative(relative_move)
    pause(2)
    
    % wait until we arrived
    % depending on velocity and step size, we should be able to calculate
    % duration
    pause(1)
    sir.get_coord;
    pause(.5)
    
    fprintf('Collecting ETL stack %03d of %03d... \n',[iTile nTiles])
    
    if dry_run
        sir.set_msg(sprintf('coord=[%.2f;%.2f;%.2f;%.2f]',sir.cur_coord))
        pause(.2)
    else
        % start grab
        sir.start_grab()
        pause(3)
        
        sir.set_msg(sprintf('coord=[%.2f;%.2f;%.2f;%.2f]',sir.cur_coord))   
        pause(.5)
        
        % listen for grab to stop
        fprintf('Waiting for grab to finish...')
        nWaits=0;
        while sir.check_grabDone==0
            nWaits=nWaits+1;
            %iFrame=sbx.mmfile.Data.header(1)
            %sbx.mmfile.Data.header(1) = -1;
            pause(.2)
            %if nWaits>1000
            %    fprintf(' did not complete!!! \n')
            %    break
            %end
        end
        fprintf(' done! \n')
        pause(1)
    end
    
    %move to next position
    
end

disp('Grid stack completed!!!')