class: CommandLineTool

cwlVersion: v1.0

baseCommand: [ "view" ]

hints:
  - class: DockerRequirement
    dockerPull: mgibio/samtools:1.9

  - class: SoftwareRequirement
    packages:
      samtools:
        version: [ "1.9" ]

arguments:
  - valueFrom: "-b"
    position: 1

inputs:
  sam_file:
    type: File
    inputBinding:
      position: 2

outputs:
  aligned_bam:
    type: stdout

stdout: aligned.bam
