class: CommandLineTool

cwlVersion: v1.0

baseCommand: [ "faidx" ]

hints:
  - class: DockerRequirement
    dockerPull: mgibio/samtools:1.9

  - class: SoftwareRequirement
    packages:
      samtools:
        version: [ "1.9" ]

  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.reference_file)

inputs:
  reference_file:
    type: File
    inputBinding:
      position: 1

outputs:
  fasta_index:
    type: File
    secondaryFiles: [.fai]
    outputBinding:
      glob: "*.fa"
