from collections import defaultdict

import boto3
import botocore.session
import boto.ec2
from boto.manage.cmdshell import sshclient_from_instance
import subprocess
import sys


running = {}
reserved = {}
on_demand = {}
od = {}

final = dict()


def get_running_instances(region):
    for ses in ['default', 'ci', 'dev', 'siva']:
        boto3.setup_default_session(profile_name=ses)
        ec2 = boto3.client('ec2', region)
        reservations = ec2.describe_instances()
        for reservation in reservations["Reservations"]:
            for instance in reservation["Instances"]:
                if instance["State"]["Name"] == "running":
                    if not instance.has_key('SpotInstanceRequestId'):
                        for tagname in instance["Tags"]:
                            if tagname["Key"] == "Name":
                                if instance["InstanceType"] in final:
                                    final[instance["InstanceType"]] = final[instance["InstanceType"]] + 1
                                else:
                                    final[instance["InstanceType"]] = 1
    for key, value in final.viewitems():
       # print region, ":", key, value
        running[region][key] = value


def get_reservations_all(region):
    boto3.setup_default_session(profile_name='default')
    ec2 = boto3.client('ec2', region)
    reg = dict()
    reservations = ec2.describe_reserved_instances()
    for reservation in reservations['ReservedInstances']:
        if reservation['State'] == 'active':
            count = reservation['InstanceCount']
            if reservation["InstanceType"] in reg:
                reg[reservation["InstanceType"]] = reg[reservation["InstanceType"]] + count
                # print region, reservation["InstanceType"]
            else:
                reg[reservation["InstanceType"]] = count

                # print reg.viewitems()
    for key, value in reg.viewitems():
        # print "reserved", region, key, value
        reserved[region][key] = value


#

def compare_reserved():
    for region in reserved:
        for instance in reserved[region]:
            running_region = running.get(region)
            if running_region is not None:
                running_instances = running_region.get(instance)
                if running_instances is None:
                    running_instances = 0
                on_demand_instances = reserved[region][instance] - running_instances
                on_demand[region][instance] = on_demand_instances
    for region in on_demand:
        for instance in on_demand[region]:
            if on_demand[region][instance] > 0:
                print "Reserved UnUsed : " + region + " : " + instance + " : " + str(on_demand[region][instance])


def compare_od():
    for region in running:
        for instance in running[region]:
            reserved_region = reserved.get(region)
            if reserved_region is not None:
                reserved_instances = reserved_region.get(instance)
                if reserved_instances is None:
                    reserved_instances = 0
                od_instances = running[region][instance] - reserved_instances
                od[region][instance] = od_instances
    for region in od:
        for instance in od[region]:

            if od[region][instance] > 0:
                print "Running OD : " + region + " : " + instance + " : " + str(od[region][instance])


def main():
    regions = ['us-east-1']
    for region in regions:
        running[region] = {}
        reserved[region] = {}
        on_demand[region] = {}
        od[region] = {}
        get_running_instances(region)
        get_reservations_all(region)
    compare_reserved()
    print " ============= "
    compare_od()


if __name__ == '__main__': main()
