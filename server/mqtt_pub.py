import paho.mqtt.client as mqtt
import random
import time
import json
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
import ssl

connected = False

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    connected = True
    print("Connected with status:", client, userdata, flags, rc, properties)

def on_disconnect(client, userdata, rc, properties=None):
    global connected
    connected = False
    print("Disconnected:", client, userdata, rc, properties)

def on_message(client, userdata, message):
    # for subscriber.
    print("Received:", client, userdata, message)

def on_publish(client, userdata, mid):
    if opt.debug:
        print("Published:", client, userdata, mid)

ap = ArgumentParser(
        description="a MQTT publisher for UnityMQTTClientTest.",
        formatter_class=ArgumentDefaultsHelpFormatter)
ap.add_argument("client_id", help="specify the client id as a topic.")
ap.add_argument("-s", "--scale",
                action="store", dest="scale", type=float, default=1.,
                help="specify a scale of the vector.")
ap.add_argument("-t", "--interval",
                action="store", dest="interval", type=int, default=1,
                help="specify an interval to publish the data.")
ap.add_argument("--broker",
                action="store", dest="broker_name", default="localhost",
                help="specify the MQTT broker.")
ap.add_argument("--broker-port",
                action="store", dest="broker_port", type=int, default=1883,
                help="specify a port number for the MQTT broker.")
ap.add_argument("--ca-chain",
                action="store", dest="ca_chain",
                help="specify a file of the trusted CA chain.")
ap.add_argument("--client-cert",
                action="store", dest="client_cert",
                help="specify a file name of the client's cert.")
ap.add_argument("--priv-key",
                action="store", dest="priv_key",
                help="specify a file name of the client's private key.")
ap.add_argument("-d", action="store_true", dest="debug",
                help="enable debug mode.")
opt = ap.parse_args()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s" + logging.BASIC_FORMAT)

client = mqtt.Client()
if opt.ca_chain and opt.client_cert:
    if opt.priv_key is None:
        logger.error("client private key is required.")
        exit(1)
    client.tls_set(ca_certs=opt.ca_chain,
                   cert_reqs=ssl.CERT_REQUIRED,
                   certfile=opt.client_cert,
                   keyfile=opt.priv_key)
elif opt.ca_chain:
    client.tls_set(ca_certs=opt.ca_chain,
                   cert_reqs=ssl.CERT_REQUIRED)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

print("Connecting to the broker...")
client.connect(opt.broker_name, port=opt.broker_port, keepalive=60)
client.loop_start()

vecs = [-opt.scale,0,opt.scale]

while True:
    if connected:
        msg = json.dumps({
                "x":random.choice(vecs),
                "y":random.choice(vecs),
                "z":random.choice(vecs)
                })
        if opt.debug:
            print(msg)
        client.publish(opt.client_id, msg, qos=1)
        time.sleep(opt.interval)
    else:
        print("Waiting for connection...")
        time.sleep(5)

