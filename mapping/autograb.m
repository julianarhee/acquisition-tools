function autograb(varargin)

    % example for using the ScanImage API to set up a grab
    hSI = evalin('base','hSI');                         % get hSI from the base workspace
    assert(strcmpi(hSI.acqState,'idle'));               % make sure scanimage is in an idle state
    
    % Set defaults for auto-grab series:
    %hSI.hScan2D.logFilePath = 'C:\';                   % set the folder for logging Tiff files
    hSI.hScan2D.logFileStem = 'autograb'                % set the base file name for the Tiff file
    hSI.hScan2D.logFileCounter = 1;                     % set the current Tiff file number
    hSI.hChannels.loggingEnable = true;                 % enable logging
           
    %hSI.hRoiManager.scanZoomFactor = 2;     % define the zoom factor
    %hSI.hRoiManager.framesPerSlice = 100;   % set number of frames to capture in one Grab
  
    switch nargin %isempty(varagin)
        case 0
            hSI.hMotors.motorPosition = [0 0 0];    	% move stage to origin Note: depending on motor this value is a 1x3 OR 1x4 matrix
        case 1
            hSI.hMotors.motorPosition = varargin{1};    % move to given coord
        case 2
            hSI.hMotors.motorPosition = varargin{1};    % target pos
            hSI.hScan2D.logFileStem = varargin{2};      % file save basename
            hSI.hScan2D.logFileCounter = varargin{3};   % file save #

    hSI.startGrab();                        % start the grab
end