%% Automatically Generated Run Script
{% for header, value in headers.items() %}
% {{ header }}: {{ value }}
{% endfor %}

try
    fprintf('########## Started ##########\n');
    restoredefaultpath;
{%- for lang, cfg in mex_cfg.items() %}
    mex('-setup:C:\Program Files\MATLAB\{{ matlab_version }}\bin\win64\mexopts\{{ cfg }}.xml','{{ lang }}');
{% endfor %}
{% if working_directory is not none %}
    cd('{{ obj.start_directory }}');
{% endif %}
{%- if profile -%}
    profile('on');
{% endif %}
    model = '{{ model }}';
    open_system(model);
    slbuild(model);
{%- if profile -%}
    profile('off');
    profileinfo = profile('info');
    profsave(profileinfo,'profile_results');
{% endif %}
    fprintf('########## Finished ##########\n');
    exit(0);
catch me
    fprintf('########## Failed ##########\n');
    fprintf('ERROR: %s (%s)\n\n',me.message, me.identifier)
    for i = numel(me.stack):-1:1
        fprintf('[Line %02d]: %s\n',me.stack(i).line,me.stack(i).file)
    end
    exit(1);
end
quit('force');
