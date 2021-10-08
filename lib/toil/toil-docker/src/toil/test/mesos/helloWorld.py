# Copyright (C) 2015-2021 Regents of the University of California
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
A simple user script for Toil
"""

import argparse

from toil.common import Toil
from toil.job import Job

childMessage = "The child job is now running!"
parentMessage = "The parent job is now running!"

def hello_world(job):

    job.fileStore.logToMaster(parentMessage)
    with open('foo_bam.txt', 'w') as handle:
        handle.write('\nThis is a triumph...\n')

    # Assign FileStoreID to a given file
    foo_bam = job.fileStore.writeGlobalFile('foo_bam.txt')


    # Spawn child
    job.addChildJobFn(hello_world_child, foo_bam, memory=100, cores=0.5, disk="3G")


def hello_world_child(job, hw):

    path = job.fileStore.readGlobalFile(hw)
    job.fileStore.logToMaster(childMessage)
    # NOTE: path and the udpated file are stored to /tmp
    # If we want to SAVE our changes to this tmp file, we must write it out.
    with open(path, 'r') as r:
        with open('bar_bam.txt', 'w') as handle:
            for line in r.readlines():
                handle.write(line)

    # Assign FileStoreID to a given file
    # can also use:  job.updateGlobalFile() given the FileStoreID instantiation.
    job.fileStore.writeGlobalFile('bar_bam.txt')


def main():
    # Boilerplate -- startToil requires options

    parser = argparse.ArgumentParser()
    Job.Runner.addToilOptions(parser)
    options = parser.parse_args()

    # Create object that contains our FileStoreIDs

    # Launch first toil Job
    i = Job.wrapJobFn(hello_world, memory=100, cores=0.5, disk="3G")
    with Toil(options) as toil:
        toil.start(i)


if __name__ == '__main__':
    main()
