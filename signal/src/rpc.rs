use serde::{Deserialize, Serialize};
use serde_json::Value;
use tokio::sync::mpsc::Sender;

#[derive(Serialize)]
pub struct RpcRequest {
    pub jsonrpc: &'static str,
    pub method: &'static str,
    pub params: Value,
    pub id: i64,
}

#[derive(Deserialize, Debug)]
pub struct RpcResponse {
    #[allow(dead_code)]
    pub jsonrpc: String,
    pub method: Option<String>,
    pub params: Option<Value>,
    #[allow(dead_code)]
    pub result: Option<Value>,
    #[allow(dead_code)]
    pub id: Option<i64>,
}

pub async fn send_message(tx: &Sender<String>, recipient: &str, message: &str) {
    let req = RpcRequest {
        jsonrpc: "2.0",
        method: "send",
        params: serde_json::json!({
            "recipient": [recipient],
            "message": message
        }),
        id: 1,
    };

    if let Ok(json_str) = serde_json::to_string(&req) {
        if let Err(e) = tx.send(json_str).await {
            eprintln!("Error sending command to channel: {}", e);
        }
    }
}