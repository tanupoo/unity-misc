using System;
using System.Threading.Tasks;
using NativeWebSocket;
using UnityEngine;

public class UnityWSClientTest
{
    private string app_message;
    WebSocket websocket;

    public async Task start(string server_name, string client_id)
    {
        try
        {
            websocket = new WebSocket(server_name);

            websocket.OnOpen += () =>
            {
                //Debug.Log("### WebSocket Connection open ###");
            };

            websocket.OnError += (e) =>
            {
                //Debug.Log("### WebSocket Error ###" + e);
            };

            websocket.OnClose += (e) =>
            {
                //Debug.Log("### WebSocket Connection closed ###" + e);
            };

            websocket.OnMessage += (bytes) =>
            {
                app_message = System.Text.Encoding.UTF8.GetString(bytes);
                //Debug.Log("### OnMessage:" + app_message);
            };

            await websocket.Connect();
        }
        catch (Exception exception)
        {
            Debug.Log("### WebSocket Exception ###");
            Debug.Log(exception);
        }
    }

    public async Task end()
    {
        await websocket.Close();
    }

    public async Task sendMessage(string message)
    {
        await websocket.SendText(message);
    }

    public async Task reconnect()
    {
        await Task.Delay(TimeSpan.FromSeconds(5));
        await websocket.Connect();
    }

    public string getMessage()
    {
        if (websocket.State == WebSocketState.Closed) {
            Task ignoredAwaitableResult = reconnect();
            // getting message is passed to the next chance.
            return null;
        }
        if (websocket.State != WebSocketState.Open) {
            Debug.Log($"WS state is not Open: {websocket.State}");
            return null;
        }
        return app_message;
    }
}
