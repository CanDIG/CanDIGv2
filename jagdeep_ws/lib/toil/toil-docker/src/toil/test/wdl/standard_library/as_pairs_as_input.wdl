version development

workflow asPairsWorkflow {
  input {
    Map[String, Int] in_map
  }

  call copy_output {input: in_pairs=as_pairs(in_map)}
}

task copy_output {
  input {
    Array[Pair[String, Int]] in_pairs
  }

  command {
    cp ~{write_json(in_pairs)} output.txt
  }

  output {
    File the_output = 'output.txt'
  }
}
