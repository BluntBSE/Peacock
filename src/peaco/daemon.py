import sys
import multiprocessing


def process_fan_data(exec_string):
    peacock_output = {}  # ???namespace sorcery???
    exec(exec_string, peacock_output, peacock_output)
    result = peacock_output.get("_peacock_output")
    return result


# Execute the function with its arguments
if __name__ == "__main__":
    # If you passsed arguments to the daemon, they will be in this array.
    all_args = sys.argv
    # The first few arguments are the python executable and the daemon script, so this makes an array of arguments that excludes those.
    operation_args = all_args[1:]
    pool = multiprocessing.Pool()
    # Switch the callback from demo_Logic to long_logic to see the speed gains on an operation that should take 30 minutes.
    # The more time the operation takes, the more speed gains you will see.
    results = pool.map(process_fan_data, operation_args)
    pool.close()
    pool.join()
    print(results)

