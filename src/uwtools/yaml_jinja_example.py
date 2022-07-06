'''

A Proof of Concept for an algorithm that could be used to template
fields in a YAML config file. The steps are as such:

    1. Read in the YAML file with pyyaml. We need a dictionary of key,
    value pairs to reference inside the templated fields.
    2. Loop through each dictionary items from the YAML and assess the
    existence of a Jinja template field -- double curly braces.
    3. If a {{ }} exists, have Jinja fill it in with any available
    configuration settings. Leave it untouched if variables are not
    definied to fill it in.

    Note: Each Jinja field is treated separately because of the Jinja
    behavior that disallows filling any field if even a single one is
    not defined.

Here are the requirements this algorithm meets:

  * It provides a python method for filling in templates that are very
  consistent with basic Jinja.
  * It provides an option to hold off filling in certain variables until
  they are defined (cycle wasn’t provided, so it wasn’t filled in) 
  * It provides mechanisms for referencing other key/values available in
  the YAML
  * It provides the SAME mechanism for referencing environment variables
  * It requires only the use of a single double curly bracket
  * It allows for easy math as a no-cost additional feature.


'''
from argparse import Namespace
import os
import re

import yaml
import jinja2

orig = '''
model: gfs
target: ufs-weather-model

horizontal_resolution: c768
vertical_resolution: 64

executable: ${UFSEXEC}

filetype: gfs
datapath: '$(experiment_dir)/{{current_cycle}}'
filename_core: 'fv_core.res.nc'

updated_datapath: '$(experiment_dir)/{{my_current_cycle}}'

updatethis: 'testpassed'
testupdate: $(updatethis)
'''

input_str = '''

model: gfs
target: ufs-weather-model

experiment_dir: /home/myexpid

fcst:
  length: 72
  bndy_freq: 12

boundary_hours: '{% for h in range(fcst.bndy_freq, fcst.length, fcst.bndy_freq) %}{{ " %03d" % h }}{% endfor %}'

horizontal_resolution: c768
vertical_resolution: '{{ 62 + 2 }}'

executable: '{{ env.UFSEXEC }}'

post_length: '{{ fcst.length }}'

filetype: gfs
datapath: '{{ experiment_dir }}/{{ cycle.current_cycle }}'
filename_core: 'fv_core.res.nc'

updated_datapath: '{{ experiment_dir }}/{{ cycle.my_current_cycle }}'

updatethis: 'testpassed'
testupdate: '{{ updatethis }}'


'''

# Set the env variables needed for the template above.
os.environ['UFSEXEC'] = '/Users/christina.holt/Work/ufs-srweather-app/bin/ufs_weather_model'


# Load the yaml string as a dict
# This is needed as the first step so that we have access to all the
# key, value pairs stored for reference.
yaml_dict = yaml.load(input_str, Loader=yaml.SafeLoader)
print(yaml_dict)

print('*'*80)
print('*'*80)

for k, v in yaml_dict.items():

    # Save a bit of compute and only do this part for strings that
    # contain the jinja double brackets.
    is_a_template = any((ele for ele in ['{{', '{%'] if ele in v))
    if is_a_template:

        # Find expressions first, and process them as a single template
        # if they exist
        # Find individual double curly brace template in the string
        # otherwise. We need one substitution template at a time so that
        # we can opt to leave some un-filled when they are not yet set.
        # For example, we can save cycle-dependent templates to fill in
        # at run time.
        print(f'Value: {v}')
        if '{%' in v:
            templates = [v]
        else:
            templates = re.findall(r'{{[^}]*}}|\S', v)
        print(f'Templates: {templates}')

        data = []
        for template in templates:
            j_tmpl = jinja2.Environment(loader=jinja2.BaseLoader).from_string(template)
            try:
                # Fill in a template that has the appropriate variables
                # set.
                template = j_tmpl.render(env=os.environ, **yaml_dict)
                print(f'Filled template: {k}: {template}')
            except jinja2.exceptions.UndefinedError as e:
                # Leave a templated field as-is in the resulting dict
                print(f'Error: {e}')
                print(f'Preserved template: {k}: {template}')

            data.append(template)

        # Put the full template line back together as it was, filled or
        # not
        yaml_dict[k] = ''.join(data)


print('*'*80)
print('*'*80)


for k, v in yaml_dict.items():
    print(f'{k}: {v}')


with open('test_example.yaml', 'w') as fn:
    yaml.dump(yaml_dict, fn)


expected_printed_output = '''
model: gfs
target: ufs-weather-model
experiment_dir: /home/myexpid
fcst: {'length': 72, 'bndy_freq': 12}
boundary_hours:  012 024 036 048 060
horizontal_resolution: c768
vertical_resolution: 64
executable: /Users/christina.holt/Work/ufs-srweather-app/bin/ufs_weather_model
post_length: 72
filetype: gfs
datapath: /home/myexpid/{{ cycle.current_cycle }}
filename_core: fv_core.res.nc
updated_datapath: /home/myexpid/{{ cycle.my_current_cycle }}
updatethis: testpassed
testupdate: testpassed
'''
