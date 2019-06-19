class: CommandLineTool

cwlVersion: v1.0

baseCommand: [ "sort" ]

requirements:
  - class: DockerRequirement
    dockerPull: mgibio/samtools:1.9
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.bam_file)

inputs:
  bam_file:
    type: File
    inputBinding:
      position: 1

outputs:
  sorted_bam:
    type: stdout

stdout: aligned.sorted.bam
