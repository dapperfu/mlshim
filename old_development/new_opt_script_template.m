function varargout={{ ml_script }}(opts)
% {{ ml_script }}(opts) - Is a script that ...
%
% Inputs:
% opts is a structure with the following available fields:
{% if opts is not none %}
    

{% endif %}
% for opt in opts:
%     model
%         Default: bdroot
%         Simulink model to build.
% endif
% endfor
% endif
%     model
%         Default: bdroot
%         Simulink model to build.
%     buildNum
%         Default: 99
%         Set the build number.
%     runInit
%         Default: true
%         Run init file. Required if the init file is not in the model 
%           PreLoadFcn callback. The init file must be named as follows
%           [Model]_Init.m
%     modelViewer
%         Default: true
%         Enable or disable the model viewer files.
%     profile
%         Default: false
%         Profile the build process.
%     commit
%         Default: false
%         Commit the build in git.
%         Recommended if flashfile is going to be used on engine.
%         Requires all changes to be commited before building and commits
%         the build after compiling.
%
%
% Author: You <@>

% Check number of in & out arguments
try
    nargoutchk(0,1);
    narginchk(0,1);
catch ME
    % Otherwise print the dtfBuild help and then rethrow error.
    fprintf('%s help:\n',mfilename);
    feval('help',mfilename);
    rethrow(ME);
end
%% Defaults
% for opt in opts:
defaults.buildSuffix=false;
% endfor

% If no inputs and only 1 output return the default options.
% Used to easily get a struct of what is available.
if nargin==0&&nargout==1
    varargout{1}=defaults;
    return;
end

%% IO Processing
% Process input
switch nargin
    case 0
        % If no input arguments are given, set the options to the default.
        opts=defaults;
    case 1
        % Otherwise get all of the fieldnames from the default settings.
        fields = fieldnames(defaults);
        % Determine all of the unset fields.
        unset_fields = fields(~isfield(opts,fields));
        % For each of the unset fields assign the default to opts struct.
        for i = 1:numel(unset_fields)
            field=unset_fields{i};
            opts.(field) = defaults.(field);
        end
end

%%%%%%
% BEGIN SCRIPT
% All 
%%%%%%