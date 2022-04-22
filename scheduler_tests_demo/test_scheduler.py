#!/usr/bin/env python3

import os
import sys
import yaml
from uwtools.nameddict import NamedDict
from uwtools.scheduler import Scheduler

input_file = sys.argv[1]

with open(input_file, "r") as fh:
    try:
        cfg = NamedDict(yaml.load(fh, Loader=yaml.FullLoader))
    except yaml.YAMLError as exc:
        print(exc)

factory = Scheduler.scheduler_factory
sched = factory.create(cfg.scheduler, cfg)
batch_card = sched.get_batch_card

job_card = []

if cfg.scheduler in ['Slurm']:
    job_card.append('#!/bin/bash')

job_card.append(batch_card+'')

cmd = f"echo 'Hello World!'"
job_card.append(cmd)

# Create jobcard
with open(f"{cfg.jobname}.sh", 'w') as fh:
    fh.write('\n'.join(job_card))


# Submit to job to scheduler
os.system(f"{cfg.submit_cmd} {cfg.jobname}.sh")
