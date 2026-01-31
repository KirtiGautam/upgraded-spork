mod commands;
mod models;
mod rpc;

use serde_json::Value;
use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader};
use tokio::process::Command;

use crate::commands::process_command;
use crate::rpc::RpcResponse;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut child = Command::new("signal-cli")
        .arg("jsonRpc")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .expect("Failed to spawn signal-cli");

    println!("Signal Bot started. Waiting for messages...");

    let stdin = child.stdin.take().expect("Failed to open stdin");
    let stdout = child.stdout.take().expect("Failed to open stdout");

    // Create channel for communication between Reader and Writer
    let (tx, mut rx) = tokio::sync::mpsc::channel::<String>(32);

    // 1. Writer Task: Sends commands to signal-cli
    let writer_handle = tokio::spawn(async move {
        let mut stdin = stdin;
        while let Some(command_json) = rx.recv().await {
            let mut cmd = command_json;
            cmd.push('\n');
            if let Err(e) = stdin.write_all(cmd.as_bytes()).await {
                eprintln!("Failed to write to signal-cli: {}", e);
                break;
            }
            if let Err(e) = stdin.flush().await {
                eprintln!("Failed to flush stdin: {}", e);
            }
        }
    });

    // 2. Reader Loop: Listens for incoming messages
    let mut reader = BufReader::new(stdout).lines();

    while let Some(line) = reader.next_line().await? {
        if line.trim().is_empty() {
            continue;
        }

        match serde_json::from_str::<RpcResponse>(&line) {
            Ok(msg) => {
                if let Some(method) = msg.method {
                    if method == "receive" {
                        handle_incoming_message(msg.params, &tx).await;
                    }
                }
            }
            Err(e) => eprintln!("Skipping unparseable line: {}", e),
        }
    }

    let _ = writer_handle.await;
    child.kill().await?;
    Ok(())
}

async fn handle_incoming_message(params: Option<Value>, tx: &tokio::sync::mpsc::Sender<String>) {
    if let Some(p) = params {
        let envelope = &p["envelope"];
        let source = envelope["source"].as_str().unwrap_or("Unknown");
        // This 'account' is the phone number of the bot itself
        let account = p["account"].as_str().unwrap_or("");

        // Handle "Note to Self"
        if let Some(sync_msg) = envelope.get("syncMessage") {
            if let Some(sent_msg) = sync_msg.get("sentMessage") {
                let destination = sent_msg["destination"].as_str().unwrap_or("");
                // If destination == account, it's a Note to Self.
                if destination == account {
                    if let Some(text) = sent_msg["message"].as_str() {
                        // Pass 'account' as both owner AND recipient
                        process_command(tx, account, account, text).await;
                    }
                }
            }
            return;
        }

        // Handle Standard Messages
        if let Some(data_message) = envelope.get("dataMessage") {
            if let Some(text) = data_message["message"].as_str() {
                // Pass 'account' (owner) and 'source' (sender)
                process_command(tx, account, source, text).await;
            }
        }
    }
}