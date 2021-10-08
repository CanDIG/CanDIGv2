from __future__ import absolute_import
from six.moves import xrange
from argparse import ArgumentParser
import os
import logging
import random

from toil.common import Toil
from toil.job import Job


def setup(job, input_file_id, n, down_checkpoints):
    """Sets up the sort.
    Returns the FileID of the sorted file
    """
    # Write the input file to the file store
    job.fileStore.logToMaster("Starting the merge sort")
    return job.addChildJobFn(down,
                             input_file_id, n,
                             down_checkpoints=down_checkpoints,
                             memory='600M').rv()


def down(job, input_file_id, n, down_checkpoints):
    """Input is a file and a range into that file to sort and an output location in which
    to write the sorted file.
    If the range is larger than a threshold N the range is divided recursively and
    a follow on job is then created which merges back the results. Otherwise,
    the file is sorted and placed in the output.
    """
    # Read the file
    input_file = job.fileStore.readGlobalFile(input_file_id, cache=False)
    length = os.path.getsize(input_file)
    if length > n:
        # We will subdivide the file
        job.fileStore.logToMaster("Splitting file: %s of size: %s"
                                  % (input_file_id, length), level=logging.CRITICAL)
        # Split the file into two copies
        mid_point = get_midpoint(input_file, 0, length)
        t1 = job.fileStore.getLocalTempFile()
        with open(t1, 'w') as fH:
            copy_subrange_of_file(input_file, 0, mid_point + 1, fH)
        t2 = job.fileStore.getLocalTempFile()
        with open(t2, 'w') as fH:
            copy_subrange_of_file(input_file, mid_point + 1, length, fH)

        # Call the down function recursively
        return job.addFollowOnJobFn(up, job.addChildJobFn(down, job.fileStore.writeGlobalFile(t1), n,
                                    down_checkpoints=down_checkpoints, memory='600M').rv(),
                                    job.addChildJobFn(down, job.fileStore.writeGlobalFile(t2), n,
                                                      down_checkpoints=down_checkpoints,
                                                      memory='600M').rv()).rv()
    else:
        # We can sort this bit of the file
        job.fileStore.logToMaster("Sorting file: %s of size: %s"
                                  % (input_file_id, length), level=logging.CRITICAL)
        # Sort the copy and write back to the fileStore
        output_file = job.fileStore.getLocalTempFile()
        sort(input_file, output_file)
        return job.fileStore.writeGlobalFile(output_file)


def up(job, input_file_id_1, input_file_id_2):
    """Merges the two files and places them in the output.
    """
    with job.fileStore.writeGlobalFileStream() as (fileHandle, output_id):
        with job.fileStore.readGlobalFileStream(input_file_id_1) as inputFileHandle1:
            with job.fileStore.readGlobalFileStream(input_file_id_2) as inputFileHandle2:
                job.fileStore.logToMaster("Merging %s and %s to %s"
                                          % (input_file_id_1, input_file_id_2, output_id))
                merge(inputFileHandle1, inputFileHandle2, fileHandle)

        # Cleanup up the input files - these deletes will occur after the completion is successful.
        job.fileStore.deleteGlobalFile(input_file_id_1)
        job.fileStore.deleteGlobalFile(input_file_id_2)
        return output_id


# convenience functions
def sort(in_file, out_file):
    """Sorts the given file.
    """
    filehandle = open(in_file, 'r')
    lines = filehandle.readlines()
    filehandle.close()
    lines.sort()
    filehandle = open(out_file, 'w')
    for line in lines:
        filehandle.write(line)
    filehandle.close()


def merge(filehandle_1, filehandle_2, output_filehandle):
    """Merges together two files maintaining sorted order.
    """
    line2 = filehandle_2.readline()
    for line1 in filehandle_1.readlines():
        while line2 != '' and line2 <= line1:
            output_filehandle.write(line2)
            line2 = filehandle_2.readline()
        output_filehandle.write(line1)
    while line2 != '':
        output_filehandle.write(line2)
        line2 = filehandle_2.readline()


def copy_subrange_of_file(input_file, file_start, file_end, output_filehandle):
    """Copies the range (in bytes) between fileStart and fileEnd to the given
    output file handle.
    """
    with open(input_file, 'r') as fileHandle:
        fileHandle.seek(file_start)
        data = fileHandle.read(file_end - file_start)
        assert len(data) == file_end - file_start
        output_filehandle.write(data)


def get_midpoint(file, file_start, file_end):
    """Finds the point in the file to split.
    Returns an int i such that fileStart <= i < fileEnd
    """
    filehandle = open(file, 'r')
    mid_point = (file_start + file_end) / 2
    assert mid_point >= file_start
    filehandle.seek(mid_point)
    line = filehandle.readline()
    assert len(line) >= 1
    if len(line) + mid_point < file_end:
        return mid_point + len(line) - 1
    filehandle.seek(file_start)
    line = filehandle.readline()
    assert len(line) >= 1
    assert len(line) + file_start <= file_end
    return len(line) + file_start - 1


def make_file_to_sort(file_name, lines, line_length):
    with open(file_name, 'w') as fileHandle:
        for _ in xrange(lines):
            line = "".join(random.choice('actgACTGNXYZ') for _ in xrange(line_length - 1)) + '\n'
            fileHandle.write(line)


def main():
    parser = ArgumentParser()
    Job.Runner.addToilOptions(parser)

    parser.add_argument('--num-lines', default=1000, help='Number of lines in file to sort.', type=int)
    parser.add_argument('--line-length', default=50, help='Length of lines in file to sort.', type=int)
    parser.add_argument("--N",
                        help="The threshold below which a serial sort function is used to sort file. "
                        "All lines must of length less than or equal to N or program will fail",
                        default=10000)

    options = parser.parse_args()

    if int(options.N) <= 0:
        raise RuntimeError("Invalid value of N: %s" % options.N)

    file_name = 'file_to_sort.txt'
    make_file_to_sort(file_name=file_name, lines=options.num_lines, line_length=options.line_length)

    with Toil(options) as toil:
        sort_file_url = 'file://' + os.path.abspath('file_to_sort.txt')
        if not toil.options.restart:
            sort_file_id = toil.importFile(sort_file_url)
            sorted_file_id = toil.start(Job.wrapJobFn(setup, sort_file_id, int(options.N), False, memory='600M'))
        else:
            sorted_file_id = toil.restart()
        toil.exportFile(sorted_file_id, sort_file_url)

if __name__ == '__main__':
    main()
