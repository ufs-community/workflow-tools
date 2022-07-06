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

horizontal_resolution: c768
vertical_resolution: '{{ 62 + 2 }}'

executable: '{{ env["UFSEXEC"] }}'

filetype: gfs
datapath: '{{ cfg.experiment_dir }}/{{ cycle.current_cycle }}'
filename_core: 'fv_core.res.nc'

updated_datapath: '{{ cfg.experiment_dir }}/{{ cycle.my_current_cycle }}'

updatethis: 'testpassed'
testupdate: '{{ cfg.updatethis }}'

'''



os.environ['UFSEXEC'] = '/Users/christina.holt/Work/ufs-srweather-app/bin/ufs_weather_model'

yaml_dict = yaml.load(input_str, Loader=yaml.SafeLoader)
print(yaml_dict)

print('*'*80)
print('*'*80)
for k, v in yaml_dict.items():
    if '{{' in v:
        # Find each individual double curly brace template in the string
        templates = re.findall(r'{{[^}]*}}|\S', v)

        print(f'Templates: {templates}')
        yaml_namespace = Namespace(**yaml_dict)

        data = []
        for template in templates:
            j_tmpl = jinja2.Environment(loader=jinja2.BaseLoader).from_string(template)
            try:
                template = j_tmpl.render(cfg=yaml_namespace, 
                            env=os.environ)
                print(f'Filled template: {k}: {template}')
            except jinja2.exceptions.UndefinedError as e:
                print(f'Error: {e}')
                print(f'Preserved template: {k}: {template}')

            data.append(template)

        yaml_dict[k] = ''.join(data)

print('*'*80)
print('*'*80)

for k, v in yaml_dict.items():
    print(f'{k}: {v}')



