import os

import boto3
from flask import Flask, render_template_string

app = Flask(__name__)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION = "us-east-1"

session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION,
)
ec2_client = session.client("ec2")
elb_client = session.client("elbv2")

HTML_TEMPLATE = """
<html>
<head><title>AWS Resources</title></head>
<body>
<h1>Running EC2 Instances</h1>
<table border='1'>
<tr><th>ID</th><th>State</th><th>Type</th><th>Public IP</th></tr>
{% for instance in instance_data %}
<tr><td>{{ instance['ID'] }}</td><td>{{ instance['State'] }}</td><td>{{ instance['Type'] }}</td><td>{{ instance['Public IP'] }}</td></tr>
{% endfor %}
</table>
<h1>VPCs</h1>
<table border='1'>
<tr><th>VPC ID</th><th>CIDR</th></tr>
{% for vpc in vpc_data %}
<tr><td>{{ vpc['VPC ID'] }}</td><td>{{ vpc['CIDR'] }}</td></tr>
{% endfor %}
</table>
<h1>Load Balancers</h1>
<table border='1'>
<tr><th>LB Name</th><th>DNS Name</th></tr>
{% for lb in lb_data %}
<tr><td>{{ lb['LB Name'] }}</td><td>{{ lb['DNS Name'] }}</td></tr>
{% endfor %}
</table>
<h1>Available AMIs</h1>
<table border='1'>
<tr><th>AMI ID</th><th>Name</th></tr>
{% for ami in ami_data %}
<tr><td>{{ ami['AMI ID'] }}</td><td>{{ ami['Name'] }}</td></tr>
{% endfor %}
</table>
</body>
</html>
"""


@app.route("/")
def home():
    instances = ec2_client.describe_instances()
    instance_data = []
    for reservation in instances["Reservations"]:
        for instance in reservation["Instances"]:
            instance_data.append(
                {
                    "ID": instance["InstanceId"],
                    "State": instance["State"]["Name"],
                    "Type": instance["InstanceType"],
                    "Public IP": instance.get("PublicIpAddress", "N/A"),
                }
            )

    vpcs = ec2_client.describe_vpcs()
    vpc_data = [
        {"VPC ID": vpc["VpcId"], "CIDR": vpc["CidrBlock"]} for vpc in vpcs["Vpcs"]
    ]

    lbs = elb_client.describe_load_balancers()
    lb_data = [
        {"LB Name": lb["LoadBalancerName"], "DNS Name": lb["DNSName"]}
        for lb in lbs["LoadBalancers"]
    ]

    amis = ec2_client.describe_images(Owners=["self"])
    ami_data = [
        {"AMI ID": ami["ImageId"], "Name": ami.get("Name", "N/A")}
        for ami in amis["Images"]
    ]

    return render_template_string(
        HTML_TEMPLATE,
        instance_data=instance_data,
        vpc_data=vpc_data,
        lb_data=lb_data,
        ami_data=ami_data,
    )


@app.get("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
