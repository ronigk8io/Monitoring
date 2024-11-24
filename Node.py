import re
from envs_and_clients import envs_and_clients

max_block_diff_name= "max_block_diff"
clients_and_max_block_diff= {
    max_block_diff_name: {
        "btc": "3", "bch": "3", "eth": "20", "xlm": "50", "xrp": "50", "xtz": "50", 
        "hbar": "100", "atom": "500", "celo": "100", "dot": "100", "matic": "100", 
        "near": "150", "op": "20", "ada": "20", "tron": "100", "arb": "150000", 
        "base": "100", "avax": "100", "iota": "100", "smr": "100"
    }
    ##MoreNodesCanBeAddedHere
    ##"CLIENT":{"btc":"1","bch":"2","eth":"3","xlm":"127.0.0.1","xrp":"5"}
}

class Node:
    def __init__(self, ip, currency, used_by):
        self.ip = ip
        self.currency = currency
        self.used_by = used_by
        self.max_block_diff = clients_and_max_block_diff[max_block_diff_name][currency] if currency in clients_and_max_block_diff[max_block_diff_name].keys() else ''
        if "127.0.0.1" in ip:
            self.owner = "Public_Service_with_Our_Nginx"
        elif "gk8.network" in ip:
            self.owner = "GK8_DNS"
        elif "https" in ip and "gk8.network" not in ip:
            self.owner = "Public_Service"
        elif ip.replace(".", "").isdigit():
            self.owner = "Our_Node_IP"
        else:
            self.owner = "Unknown"

def get_node(ip, nodes_list):
    for node in nodes_list:
        if node.ip==ip:
            return node

def get_all_nodes():
    file_name = "nodes.txt"
    nodes_str_list = open(file_name, "r").read().split("\n")
    nodes_str_list = [x.split("|") for x in nodes_str_list]
    nodes_obj_list = []
    for x in nodes_str_list:
        if len(x)>=3:
            ip = x[0]
            if re.match(r"[0-9:\.]{4,100}", ip):
                ip = ip.split(":")[0]
            currency = x[1]
            used_by = (x[2].strip("][")).replace("\'", '').split(', ')
            nodes_obj_list.append(Node(ip, currency, used_by))
    node_ips = [node.ip for node in nodes_obj_list]
    clients = [client for client in clients_and_max_block_diff.keys() if client!=max_block_diff_name]
    for client in clients:
        for currency in clients_and_max_block_diff[client].keys():
            print(currency)
            ip = clients_and_max_block_diff[client][currency].split(":")[0] #removing port
            if ip in node_ips:
                add_env(ip, client, currency, nodes_obj_list)
            else:
                new_node = Node(ip, currency, [client])
                nodes_obj_list.append(new_node)
                node_ips.append(ip)
    for node in nodes_obj_list:
        new_list = []
        for env in node.used_by:
            if env in envs_and_clients and envs_and_clients[env] not in new_list:
                new_list.append(envs_and_clients[env])
            elif env not in new_list:
                new_list.append(env)
        node.used_by = list(set(new_list))
    return nodes_obj_list

def add_env(ip, env, currency, nodes_list):
    node = Node('','',[])
    for x in nodes_list:
        if x.ip==ip:
            node=x
            break
    if node.ip=='':
        print("Error adding node " )
        return
    if env not in node.used_by:
        node.used_by.append(env)
