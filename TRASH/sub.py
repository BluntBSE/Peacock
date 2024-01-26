import sys



# Execute the function with its arguments
if __name__ == '__main__':
  all_args = sys.argv
  #print(all_args)
  exec_args = all_args[1:]
  results = []
  print(exec_args)
  for execution in exec_args:
    peacock_output = {} #???namespace sorcery???
    exec(execution, peacock_output, peacock_output)
    result = peacock_output.get('_peacock_output')
    results.append(result)

  print(results)

  
