use serde::Deserialize;

#[derive(Deserialize, Debug, Clone)]
pub struct Torrent {
    pub name: String,
    pub info_hash: String,
    pub seeders: String, // API returns seeders as a string number
    pub size: String,    // API returns size as a string number (bytes)
}