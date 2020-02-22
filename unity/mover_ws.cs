using System;
using System.Threading.Tasks;
using UnityEngine;

public class mover_ws : MonoBehaviour
{
    Rigidbody rb;

    UnityWSClientTest session;
    public string ServerName = "ws://localhost:8080/ws";
    public string ClientID = "object01";

    async void Start()
    {
        session = new UnityWSClientTest();
        await session.start(ServerName, ClientID);
    }

    void Update()
    {
        string app_message = session.getMessage();
        if (app_message == null) { return; }
        if (app_message == "HELLO") {
            Task ignoredAwaitableResult = session.sendMessage(ClientID);
            return;
        }
        Vector3 v = JsonUtility.FromJson<Vector3>(app_message);
        //Debug.Log($"Received: {app_message} converted into {v}");
        transform.Translate(v * Time.deltaTime);
    }

    private async void OnApplicationQuit()
    {
        await session.end();
    }
}
