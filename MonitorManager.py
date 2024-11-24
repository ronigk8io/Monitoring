#!/bin/python
#run in python2.7 !!!
import os
import re
import subprocess
from datetime import datetime as dt
import requests
from Node import get_all_nodes
import commands


# Slack Channel - Choose one. (For two, add a line of notify_slack with channel id.)
#slack_channel = "C06V5E6PEFJ"   # channel: nodes-monitoring-tests
slack_channel = "C04LPKAGV6U"  # channel: healthcenter


def get_slack_token(file_path):
    try:
        with open(file_path, 'r') as file:
            slack_token = file.read().strip()
        return slack_token
    except IOError as e:
        print "Unable to read file at {}: {}".format(file_path, e)
        return None

slack_token_path = 'Tokens/slack_token_for_nodes_monitoring_app'
slack_token = get_slack_token(slack_token_path)


def notify_slack(channel, subject, text):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Authorization': 'Bearer {0}'.format(slack_token),
        'Content-Type': 'application/json'
    }
    payload = {
        'channel': channel,
        #'text': "Subject: {0}\nMessage: {1}".format(subject, text.replace('<br>', '\n'))
        'text': "{0} {1}".format(subject, text.replace('<br>', '\n'))
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if 'message' in response_data:
            print("Message sent: ", response_data['message']['text'])
        else:
            print("Response does not contain 'message': ", response_data)
    else:
        print("Failed to send message, status code: ", response.status_code, response.text)

def email(subject, text):
    print("email:")
    print(subject)
    print(text.replace("<br>", "\n"))
    os.system("bash sendEmailWithAmazonSes.sh \""+subject+"\" \""+text+"\"")
    print("Sending email with subject: {}\n{}".format(subject, text))

def handle_monitoring_error(currency, error_message):
    error_details = "Error monitoring {}: {}".format(currency, error_message)
    print(error_details)
    notify_slack('C06V5E6PEFJ', "Monitoring Error - {}".format(currency), error_details)

def format_slack_message(rows):
    if not rows:
        return "No data available."

    header = "Currency | Block Diff | Our Node Block | Real Block | Node IP | Node Owner | Affecting Node | Comments"
    table_data = [header]

    for row in rows:
        parts = row.split('|')
        if len(parts) < 7:
            print("Skipping malformed row:", row)  # Log unexpected format
            continue

        currency, block_diff, our_node_block, real_block, node_ip, node_owner, affecting_node = parts[:7]
        comments = ""
        if our_node_block.strip() == "-20000":
            comments = "Our node might be down.\n"
            #comments += "'Node returned unexpected value.'<'br'>'Command:'<'br>'python3 ./tronNodeGetBlock.py https://api.trongrid.io'<'br>'Returned value:'<'br>'{}'<'br'>''".format(real_block)
        elif our_node_block.strip() == "-10000":
            comments = "OnlineGetBlock failed."

        # Ensure we handle cases where there are more or fewer parts correctly
        formatted_row = " | ".join([
            currency.strip(),
            block_diff.strip() or '?',
            our_node_block.strip(),
            real_block.strip(),
            node_ip.strip(),
            node_owner.strip(),
            affecting_node.strip(),
            comments
        ])
        table_data.append(formatted_row)

    return "```" + "\n".join(table_data) + "```"

def format_email_html(text):
    errors = ""
    table_html = '''<table>
    <tr>
        <th>Currency</th><th>Block Diff</th><th>Our Node Block</th><th>Real Block</th><th>Node IP</th><th>Node Owner</th><th>Affecting Node</th><th>Comments</th>
    </tr>'''

    rows = text.replace("\n", "<br>").split("<br>")
    for row in rows:
        if "|" in row:
            details = row.split("|")
            if len(details) == 8:
                block_diff = details[2].strip()
                our_node_block = details[3].strip()
                real_block = details[4].strip()
                node_ip = details[5].strip()
                node_owner = details[6].strip()
                affecting_node = details[7].strip()

                if block_diff == "-20000":
                    comments = "Our node might be down. Error details below."
                elif block_diff == "-10000":
                    comments = "OnlineGetBlock failed."
                else:
                    comments = ""
                # Appending comments to the details
                details.append(comments)
                # Adding the row to the table
                table_html += "<tr>" + "".join("<td>{}</td>".format(detail.strip()) for detail in details) + "</tr>"

    table_html += '</table>'
    return table_html


# Initialize variables for notifications
email_subjects = []
email_bodies = []
slack_messages = []

# Retrieve nodes and currencies
nodes = get_all_nodes()
currencies = list(set([node.currency for node in nodes]))

tested_nodes = []
output = ""
affected_currencies = []
unsynced_nodes_regex = r".*\|.*\|.*\|.*\|.*\|.*\|.*"
currencies.sort()

for currency in currencies:
    currency_nodes = [node for node in nodes if node.currency == currency]
    currency_nodes.sort()

    if len(currency_nodes) == 0:
        continue

    print("Monitoring {} {}".format(currency, currency_nodes[0].max_block_diff))

    try:
        # Ensure the command is properly formatted as a list of arguments
        command_list = ["python2.7", "monitor_single_coin.py", currency, str(currency_nodes[0].max_block_diff)] + ["{}@{}@{}".format(node.owner, node.ip, node.used_by) for node in currency_nodes]
        result = subprocess.check_output(command_list, stderr=subprocess.STDOUT)
        print("Result of command execution for {}: {}".format(currency, result))
        print("---")
    except subprocess.CalledProcessError as e:
        print("Command failed with exit status {}: {}".format(e.returncode, e.output))
        handle_monitoring_error(currency, e.output)


    curr_output = str(result)

    if len(curr_output) != 0:
        output += curr_output + " <br> "
        if "EXCEPTION_START" in curr_output and currency not in affected_currencies and currency in currencies:
            affected_currencies.append(currency)



print(len(output))



if len(output) != 0:
    rows = output.split("\n")
    affected_envs = []
    for row in rows:
        if re.findall(unsynced_nodes_regex, row) == [row]:
            currency = row.split("|")[0].replace(" ", '')
            if currency not in affected_currencies and currency in currencies:
                affected_currencies.append(currency)
                current_envs = row.split("|")[6].split("[")[1].split("]")[0].split(",")
                affected_envs.extend([x for x in current_envs if x not in affected_envs])
    output += "<br>"
    affected_currencies = [x.replace(' ', '') for x in affected_currencies]
    affected_envs = [x.replace(' ', '') for x in affected_envs]
    affected_envs = ",".join(list(set(affected_envs))).upper()
    affected_currencies = ",".join(list(set(affected_currencies))).upper()

    # EMAIL
    #email_subject = ("Issue with " + affected_currencies + " nodes. Affecting nodes: " + affected_envs)[:70]
    email_subject = ("Issue with " + affected_currencies + " nodes")[:70]
    email(email_subject, format_email_html(output))

    # SLACK
    slack_subject = ("Issue with " + affected_currencies + " nodes")
    slack_message = format_slack_message(rows)
    print(slack_message)  # Print or log for debugging
    notify_slack(slack_channel, slack_subject, slack_message)

    # PHONE CALLER
    # if __name__ == '__main__':
    #       caller_python2.phone_call.make_calls_to_all_numbers()
    # for bash:
    #     email("Monitoring script: Some client nodes are not synced","client|currency|block_diff|our_node_block|real_block|our_node_ip\n" +output)
    #       phone call


# Update influx
with open("latest_check", 'w') as f:
    f.write(dt.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + str(tested_nodes) + "\n" + output)
commands.getstatusoutput("python3 nodes_health_to_influx.py")
