class: CommandLineTool

cwlVersion: v1.0

baseCommand: [ "gunzip" ]

arguments: [ "-c" ]

hints:
  - class: DockerRequirement
    dockerPull: ubuntu:xenial

  - class: SoftwareRequirement
    packages:
      package: "gunzip"

inputs:
  reference_file:
    type: File
      inputBinding:
        position: 1

outputs:
  unzipped_fasta:
    type: stdout

stdout: reference.fa
