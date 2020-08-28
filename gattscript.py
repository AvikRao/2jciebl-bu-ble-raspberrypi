import pexpect
import time

print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

DEVICE = "E2:D8:9D:FF:72:A2"

scan = pexpect.spawn("sudo hcitool lescan")
time.sleep(5)
print(scan.terminate())

child = pexpect.spawn("sudo gatttool -i hci0 -b E2:D8:9D:FF:72:A2 -I -t random")
child.sendline("connect")

child.expect("Connection successful", timeout=7)
print("connected!")


child.sendline("disconnect")
child.sendline("quit")

child.sendline("sudo hciconfig hci0 down")
child.sendline("sudo hciconfig hci0 up")

print("done!")
