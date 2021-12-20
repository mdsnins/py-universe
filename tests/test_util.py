def success(test_name):
    print("[+] Test passed: {}".format(test_name))
    
def fail(test_name, code, msg, extra, halt = True):
    print("[*] Test failed [{}]: {} {}".format(code, test_name, msg))
    print("  [-] Extra information: {}".format(extra))
    if halt:
        exit()