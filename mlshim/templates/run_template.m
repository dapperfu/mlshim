%% Automatically Generated Run Script
{% for header, value in obj.headers.items() %}
% {{ header }}: {{ value }}
{% endfor %}

failed=0
try
    fprintf('########## Started ##########\n');
{% if cwd is not none %}
    cd('{{ obj.working_directory }}');
{% endif %}

{%- for script in scripts %}
    {{ script }}
{% endfor %}
catch me
    fprintf('########## Failed ##########\n');
    fprintf('ERROR: %s (%s)\n\n',me.message, me.identifier)
    for i = numel(me.stack):-1:1
        fprintf('[Line %02d]: %s\n',me.stack(i).line,me.stack(i).file)
    end
    failed=1
end
fprintf('########## Finished ##########\n');
exit(failed);
