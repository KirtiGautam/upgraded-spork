use crate::models::Torrent;
use crate::rpc::send_message;
use tokio::process::Command;
use tokio::sync::mpsc::Sender;

// UPDATED: Now accepts 'account' to perform security checks
pub async fn process_command(tx: &Sender<String>, account: &str, recipient: &str, text: &str) {
    let text = text.trim();

    if let Some(query) = text.strip_prefix("Links for ") {
        handle_links_command(tx, recipient, query.trim()).await;
        return;
    }

    if let Some(item) = text.strip_prefix("download ") {
        handle_download_command(tx, recipient, item.trim()).await;
        return;
    }

    if text.eq_ignore_ascii_case("status") {
        // SECURITY CHECK: Pass both the requestor (recipient/source) and the owner (account)
        handle_status_command(tx, recipient, account).await;
        return;
    }

    if text.eq_ignore_ascii_case("ping") {
        send_message(tx, recipient, "Pong! 🏓").await;
    }
}

async fn handle_links_command(tx: &Sender<String>, recipient: &str, query: &str) {
    println!("Fetching links for: {}", query);

    let base_url = match std::env::var("API_URL") {
        Ok(url) => url,
        Err(_) => {
            eprintln!("Error: API_URL environment variable is not set.");
            send_message(tx, recipient, "❌ Error: System configuration missing (API_URL).").await;
            return;
        }
    };

    send_message(tx, recipient, &format!("🔍 Searching for '{}'...", query)).await;

    let url = format!("{}{}", base_url, query);
    let client = reqwest::Client::new();

    match client.get(&url)
        .header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        .send()
        .await 
    {
        Ok(resp) => {
            match resp.text().await {
                Ok(text_body) => {
                    match serde_json::from_str::<Vec<Torrent>>(&text_body) {
                        Ok(mut torrents) => {
                            if torrents.is_empty() || (torrents.len() == 1 && torrents[0].name == "No results returned") {
                                send_message(tx, recipient, "No results found.").await;
                                return;
                            }

                            torrents.sort_by(|a, b| {
                                let seeds_b = b.seeders.parse::<u32>().unwrap_or(0);
                                let seeds_a = a.seeders.parse::<u32>().unwrap_or(0);
                                seeds_b.cmp(&seeds_a)
                            });

                            if torrents.len() > 5 {
                                torrents.retain(|t| t.seeders.parse::<u32>().unwrap_or(0) >= 5);
                            }

                            let top_results: Vec<Torrent> = torrents.into_iter().take(10).collect();

                            if top_results.is_empty() {
                                send_message(tx, recipient, "Results found, but all had low seeders.").await;
                                return;
                            }

                            let mut response_msg = String::from("📂 **Search Results:**\n\n");
                            for t in top_results {
                                let size_bytes = t.size.parse::<u64>().unwrap_or(0);
                                let size_formatted = format_size(size_bytes);
                                let magnet = format!("magnet:?xt=urn:btih:{}", t.info_hash);

                                response_msg.push_str(&format!(
                                    "**{}**\nSize: {} | Seeds: {}\n`{}`\n\n",
                                    t.name, size_formatted, t.seeders, magnet
                                ));
                            }
                            send_message(tx, recipient, &response_msg).await;
                        },
                        Err(e) => {
                            eprintln!("Failed to parse JSON: {}", e);
                            eprintln!("Raw Response: {}", text_body); 
                            send_message(tx, recipient, "Error parsing search results.").await;
                        }
                    }
                },
                Err(e) => {
                    eprintln!("Failed to read response text: {}", e);
                    send_message(tx, recipient, "Error reading response from API.").await;
                }
            }
        }
        Err(e) => {
            eprintln!("Failed to fetch URL: {}", e);
            send_message(tx, recipient, "Error connecting to search API.").await;
        }
    }
}

async fn handle_download_command(tx: &Sender<String>, recipient: &str, link: &str) {
    println!("Adding torrent: {}", link);

    let params = match std::env::var("PARAMS") {
        Ok(params) => params,
        Err(_) => {
            eprintln!("Error: PARAMS environment variable is not set.");
            send_message(tx, recipient, "❌ Error: System configuration missing (PARAMS).").await;
            return;
        }
    };

    let full_url = format!("{}{}", link, params);


    let output = Command::new("transmission-remote")
        .arg("-a")
        .arg(full_url)
        .output()
        .await;

    match output {
        Ok(output) => {
            if output.status.success() {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let clean_msg = if stdout.contains("success") {
                    "✅ Torrent successfully added to Transmission."
                } else {
                    "⚠️ Command ran, but response was unclear."
                };
                send_message(tx, recipient, clean_msg).await;
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                let err_msg = format!("❌ Failed to add torrent.\nError: {}", stderr.trim());
                send_message(tx, recipient, &err_msg).await;
            }
        }
        Err(e) => {
            eprintln!("Failed to execute transmission-remote: {}", e);
            send_message(
                tx,
                recipient,
                "❌ Error: Could not execute 'transmission-remote'. Is it installed?",
            )
            .await;
        }
    }
}

// UPDATED: Includes security check
async fn handle_status_command(tx: &Sender<String>, requestor: &str, owner_account: &str) {
    // 1. SECURITY CHECK
    // If the person asking (requestor) is NOT the bot owner (owner_account), deny access.
    if requestor != owner_account {
        println!("Unauthorized status access attempt by: {}", requestor);
        send_message(tx, requestor, "⛔ Unauthorized: Only the bot owner can view status.").await;
        return;
    }

    println!("Checking torrent status...");

    let output = Command::new("transmission-remote").arg("-l").output().await;

    match output {
        Ok(output) => {
            if output.status.success() {
                let stdout = String::from_utf8_lossy(&output.stdout);
                let report = parse_transmission_output(&stdout);

                if report.is_empty() {
                    send_message(tx, requestor, "ℹ️ No active torrents found.").await;
                } else {
                    let msg = format!("📊 **Torrent Status:**\n\n{}", report);
                    send_message(tx, requestor, &msg).await;
                }
            } else {
                let stderr = String::from_utf8_lossy(&output.stderr);
                send_message(tx, requestor, &format!("❌ Error checking status:\n{}", stderr)).await;
            }
        }
        Err(e) => {
            eprintln!("Failed to execute transmission-remote: {}", e);
            send_message(tx, requestor, "❌ Could not run status command.").await;
        }
    }
}

fn format_size(bytes: u64) -> String {
    const KB: u64 = 1024;
    const MB: u64 = KB * 1024;
    const GB: u64 = MB * 1024;

    if bytes >= GB {
        format!("{:.2} GB", bytes as f64 / GB as f64)
    } else if bytes >= MB {
        format!("{:.2} MB", bytes as f64 / MB as f64)
    } else {
        format!("{:.2} KB", bytes as f64 / KB as f64)
    }
}

fn parse_transmission_output(output: &str) -> String {
    let mut lines = output.lines();
    lines.next();

    let mut result = String::new();

    for line in lines {
        let line = line.trim();
        if line.starts_with("Sum:") || line.is_empty() {
            continue;
        }

        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() < 9 {
            continue;
        }

        let percent = parts[1];
        let status = parts[7];
        let name = parts[8..].join(" ");

        let icon = if percent == "100%" { "✅" } else { "⬇️" };
        result.push_str(&format!("{} **{}** - {} ({})\n", icon, percent, name, status));
    }

    result
}