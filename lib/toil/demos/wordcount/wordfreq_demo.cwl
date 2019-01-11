cwlVersion: v1.0
class: CommandLineTool
baseCommand: python
inputs:
  file:
    type: string
    inputBinding:
      position: 1
outputs:
  output:
      type: stdout
