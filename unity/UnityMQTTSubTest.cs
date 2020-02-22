using System;
using System.Text;
using System.Threading.Tasks;
using MQTTnet;
using MQTTnet.Client;
using MQTTnet.Client.Connecting;
using MQTTnet.Client.Disconnecting;
using MQTTnet.Client.Options;
using MQTTnet.Client.Receiving;
using MQTTnet.Protocol;
using UnityEngine;

public class UnityMQTTSubTest
{
    private string app_message;
    private IMqttClient mqttClient;

    public async Task start(string server_name, string sub_topic)
    {
        try
        {
            var factory = new MqttFactory();
            mqttClient = factory.CreateMqttClient();
            var clientOptions = new MqttClientOptionsBuilder()
                .WithTcpServer(server_name, 1883)
                .WithClientId(Guid.NewGuid().ToString())
                //.WithWebSocketServer("broker.hivemq.com:8000/mqtt")
                //.WithCredentials("user", "pass")
                //.WithTls()
                .Build();

            mqttClient.ApplicationMessageReceivedHandler =
                new MqttApplicationMessageReceivedHandlerDelegate(e =>
            {
                /*
                Debug.Log("### RECEIVED APPLICATION MESSAGE ###");
                Debug.Log("Topic=" + e.ApplicationMessage.Topic
                        + " QoS="+e.ApplicationMessage.QualityOfServiceLevel
                        + " Retain="+e.ApplicationMessage.Retain);
                 */
                app_message = Encoding.UTF8.GetString(
                        e.ApplicationMessage.Payload);
            });

            mqttClient.ConnectedHandler =
                new MqttClientConnectedHandlerDelegate(async e =>
            {
                //Debug.Log("### CONNECTED WITH SERVER ###");
                await mqttClient.SubscribeAsync(new TopicFilterBuilder()
                        .WithTopic(sub_topic)
                        .Build());
                //Debug.Log("### SUBSCRIBED ###");
            });

            mqttClient.DisconnectedHandler =
                new MqttClientDisconnectedHandlerDelegate(async e => 
            {
                Debug.Log("### DISCONNECTED FROM SERVER ###");
                await Task.Delay(TimeSpan.FromSeconds(5));
                try
                {
                    await mqttClient.ConnectAsync(clientOptions);
                }
                catch
                {
                    Debug.Log("### RECONNECTING FAILED ###");
                }
            });

            /* ConnectAsync() must be placed at the end here. */
            try
            {
                await mqttClient.ConnectAsync(clientOptions);
            }
            catch (Exception exception)
            {
                Debug.Log("### CONNECTING FAILED:" + exception);
            }
            //Debug.Log("### WAITING FOR APPLICATION MESSAGES ###");
        }
        catch (Exception exception)
        {
            Debug.Log("### MQTT EXCEPTION:" + exception);
        }
    }

    public async Task end()
    {
        await mqttClient.DisconnectAsync();
    }

    public string getMessage()
    {
        return app_message;
    }
}
