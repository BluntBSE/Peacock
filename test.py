from peaco import peacock as pk
import time
from datetime import datetime


def wait_ten_seconds(x):
    time.sleep(10)
    return x + 2

print ("Note the current time")
# Start timer that ends at the end of the script. Format this time in full seconds.
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


print(current_time)

#THIS WOULD TAKE 50 SECONDS IN SERIAL
results = pk.fan_data(wait_ten_seconds, [1, 2, 3, 4, 5])
print(results)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("Notice that fewer than 50 seconds have elapsed")
print(current_time)
