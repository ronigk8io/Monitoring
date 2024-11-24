#!/usr/bin/env python2.7
import sys
import commands
import os

num_of_retries = 3
currency = sys.argv[1]
diff_to_notify_on = int(sys.argv[2])

# ONLINE PUBLIC NODES
# Find the appropriate script based on file extension
script_base = "./" + currency + "OnlineGetBlock"
if os.path.exists(script_base + '.py'):
    cmd = "python3 " + script_base + ".py "
elif os.path.exists(script_base + '.sh'):
    cmd = "./" + script_base + ".sh "
else:
    print("No OnlineGetBlock valid script found for currency:", currency)

for i in range(num_of_retries):
    online_result = commands.getstatusoutput(cmd)[1]
    if online_result.isdigit() and int(online_result) > 0:
        break
    else:
        online_result = -10000

# OUR NODES
nodes = [{'node_owner': node.split("@")[0], 'node_ip': node.split("@")[1], 'affected_envs': node.split("@")[2]} for node in sys.argv[3:]]

for node in nodes:
    # Find the appropriate script based on file extension
    script_base = "./" + currency + "NodeGetBlock"
    if os.path.exists(script_base + '.py'):
        cmd = "python3 " + script_base + ".py " + node['node_ip']
    elif os.path.exists(script_base + '.sh'):
        cmd = "./" + script_base + ".sh " + node['node_ip']
    else:
        print("No NodeGetBlock valid script found for currency:", currency)
        continue

    node_result = -20000
    for i in range(num_of_retries):
        try:
            node_result = commands.getstatusoutput(cmd)[1]
            if node_result.isdigit() and int(node_result) > 0:
                break
        except Exception as e:
            if i == num_of_retries - 1:
                print("EXCEPTION_START" + str(e) + "EXCEPTION_END")
            continue

    if node_result.isdigit() and abs(int(online_result) - int(node_result)) >= diff_to_notify_on:
        print(currency + " | " + str(abs(int(node_result) - int(online_result))) + " | " + str(
            node_result) + " | " + str(online_result) + " | " + node['node_ip'] + " | " + node['node_owner'] + " | " +
              node['affected_envs'])
    elif not node_result.isdigit() and node_result == "False":
        print(currency + " | " + "?" + " | " + "0" + " | " + str(online_result) + " | " + node[
            'node_ip'] + " | " + node['node_owner'] + " | " + node['affected_envs'])
    elif not node_result.isdigit() and node_result != "True":
        print(currency + " | " + "?" + " | " + "-20000" + " | " + str(online_result) + " | " + node[
            'node_ip'] + " | " + node['node_owner'] + " | " + node['affected_envs'])
        print("EXCEPTION_START"+"Node returned unexpected value.<br>Command:<br>"+cmd+"<br>Returned value:<br>"+str(node_result)+"EXCEPTION_END")
