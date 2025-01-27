# Storage backend (using the filesystem for simplicity)
storage "file" {
  path = "/vault/data"
}

# Listener (without TLS)
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = "true"  # Disable TLS (NOT RECOMMENDED FOR PRODUCTION)
}

# Enable the UI (optional, for development convenience)
ui = true

# Disable memory locking (for easier development setup)
disable_mlock = true
