from Instragram import Instagram as f
import time

f.start_login_process("boskebarber", "125125bl")

start_time = time.clock()

while True:
    print("Start")
    print("deleting")


    print("Start")
    f.start_searching_by_hashtag("follow4follow")
    time.sleep(1000)

    for i in range(4):
        f.delete_following()
        print("deleted")
        time.sleep(500)









    #start_following_accounts_of_another_account()

