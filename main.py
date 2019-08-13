#encoding=utf-8
import psycopg2
from openpyxl import Workbook
import json
from openstack import connection

def get_config():
    conn = psycopg2.connect(database="huaweiyun",user="postgres",host="127.0.0.1",port="5432")
    cur=conn.cursor()
    cur.execute("select projectID,cloud,region,AK,SK from config")
    rows = cur.fetchall()
    return rows

def server_ips(server_id):
    server_ips = conn.compute.server_ips(server_id)
    for ip in server_ips:
        return(ip.address)

def calCost(size_list):
    if size_list[0] == "s3.2xlarge.4":
            cost = 862.4
    elif size_list[0] == "s3.large.2":
            cost = 152.2
    elif size_list[0] == "s3.xlarge.4":
            cost = 431.2
    elif size_list[0] == "s3.large.4":
            cost = 215.6
    elif size_list[0] == "s3.xlarge.2":
            cost = 304.3
    elif size_list[0] =="s3.small.1":
            cost = 32.2
    else:
            cost = "new_size"
    return cost

def openpyxl(lines):
    wb = Workbook()
    line1 = ["序号","ID","名称","内网IP","外网IP","规格","月费用","标签"]
    ecs = wb.active
    ecs.append(line1)
    for line in lines:
        ecs.append(line)
    wb.save("ecs.xlsx")

def tags(name_list):
    if "k8s" in name_list[0]:
        tag = "k8s"
    elif "songshuhui" in name_list[0]:
        tag = "songshuhui"
    else:
        tag = "guokr"
    return tag

def get_cost(ecs_num,ecs_k8s_cost,ecs_k8s_num):
    allcost = float(input("总费用："))
    ecs = float(input("ECS费用："))
    shujuhu = float(input("数据湖探索："))
    shipin = float(input("视频点播："))
    biaoge = float(input("表格存储服务："))
    tuijian = float(input("推荐服务："))
    pod_fantuan = float(input("饭团pod数量:"))
    pod_zhiniu = float(input("吱扭pod数量:"))
    pingjun = (allcost - ecs - shujuhu - shipin - biaoge - tuijian) / ecs_num
    songshuhui = 150 + pingjun
    guokr = (ecs - 150 - ecs_k8s_cost) + (ecs_num - ecs_k8s_num -1) * pingjun
    k8s = ecs_k8s_num * pingjun + ecs_k8s_cost
    fantuan = pod_fantuan / (pod_fantuan + pod_zhiniu) * k8s
    zhiniu = pod_zhiniu / (pod_fantuan + pod_zhiniu) * k8s + shujuhu + shipin + biaoge + tuijian
    print("果壳主站费用是","{:.2f}".format(guokr))
    print("松鼠会费用是","{:.2f}".format(songshuhui))
    print("饭团费用是","{:.2f}".format(fantuan))
    print("吱扭费用是","{:.2f}".format(zhiniu))
    print(guokr+songshuhui+zhiniu+fantuan)

def set_pg(lines):
    conn = psycopg2.connect(database="huaweiyun", user="postgres", host="127.0.0.1", port="5432")
    cur = conn.cursor()
    cur.execute("SELECT ID  from ecs")
    pg_id = cur.fetchall()
    all_id_list=[]
    for id_list in pg_id:
        id_list1 = id_list[0]
        all_id_list.append(id_list1)
    for line in lines:
        ecs_id = str(line[1])
        if ecs_id not in all_id_list:
            str_line = 'INSERT INTO ecs (num,id,name,ip_in,ip_ex,size,cost,tag) VALUES('
            str_line += str(line[0])+','+"'"+str(line[1])+"'"+','+"'"+str(line[2])+"'"+','+"'"+str(line[3])+"'"+','
            str_line += "'"+str(line[4])+"'"+','+"'"+str(line[5])+"'"+','+str(line[6])+','+"'"+str(line[7])+"'"+')'
            cur.execute(str_line)
        else:
            continue
    conn.commit()
    conn.close()

rows  = get_config()
projectId = str(rows[0][0])
cloud = str(rows[0][1])
region = str(rows[0][2])
AK = str(rows[0][3])
SK = str(rows[0][4])
conn = connection.Connection(
              project_id=projectId,
              cloud=cloud,
              region=region,
              ak = AK,
              sk = SK)
servers = conn.compute.servers(limit=1)
all_lines = []
ecs_num = 0
ecs_k8s_cost = 0
ecs_k8s_num = 0
num = 1
for server in servers:
    name = server.name
    ecs_id = server.id.split('\n')
    name_list = name.split('\n')
    ip_in = server_ips(server.id)
    ip_out = server.addresses['*******************'][1]['addr']
    ip_out_list = ip_out.split('\n')
    size = server.flavor['id']
    size_list = size.split('\n')
    cost = calCost(size_list)
    tag = tags(name_list)
    if tag == "k8s":
        ecs_k8s_cost = ecs_k8s_cost + cost
        ecs_k8s_num = ecs_k8s_num + 1
    lines = [num,str(ecs_id[0]),name_list[0],ip_in,ip_out_list[0],size_list[0],str(cost),tag]
    all_lines.append(lines)
    ecs_num = ecs_num + 1
    num = num + 1
#openpyxl(all_lines)
#get_cost(ecs_num,ecs_k8s_cost,ecs_k8s_num)
set_pg(all_lines)
