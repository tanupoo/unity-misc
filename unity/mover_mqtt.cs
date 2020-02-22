using System;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;

public class mover_mqtt : MonoBehaviour
{
    Rigidbody rb;

    UnityMQTTSubTest session;
    public string ServerName = "localhost";
    public string ClientID = "/object01";

    async void Start()
    {
        rb = this.GetComponent<Rigidbody>();
        session = new UnityMQTTSubTest();
        await session.start(ServerName, ClientID);
    }

    void Update()
    {
        string app_message = session.getMessage();
        if (app_message== null) { return; }
        Vector3 v = JsonUtility.FromJson<Vector3>(app_message);
        //Debug.Log($"Received: {app_message} converted into {v}");
        transform.Translate(v * Time.deltaTime);
    }

    private async void OnApplicationQuit()
    {
        await session.end();
    }
}
