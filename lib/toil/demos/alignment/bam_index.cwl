class: CommandLineTool

cwlVersion: v1.0

baseCommand: [ "index" ]

hints:
  - class: DockerRequirement
    dockerPull: mgibio/samtools:1.9

  - class: SoftwareRequirement
    packages:
      package: "samtools"
      version: "1.9"

  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.bam_file)

inputs:
  bam_file:
    type: File
    inputBinding:
      position: 1

outputs:
  bam_index:
    type: File
    secondaryFiles: [.bai]
    outputBinding:
      glob: "*.bam"
