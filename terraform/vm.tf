provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

resource "google_compute_instance" "mongodb_instance" {
  name         = "mongodb-instance"
  machine_type = "e2-medium"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 10
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral IP
    }
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    
    # Update and install dependencies
    apt-get update
    apt-get install -y gnupg curl

    # Import MongoDB GPG key
    curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
      gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
      --dearmor

    # Add MongoDB repository
    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/6.0 main" | \
      tee /etc/apt/sources.list.d/mongodb-org-6.0.list

    # Update and install MongoDB
    apt-get update
    apt-get install -y mongodb-org

    # Create MongoDB directory
    mkdir -p /data/db

    # Enable and start MongoDB service
    systemctl enable mongod
    systemctl start mongod

    # Configure MongoDB for external access
    sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf
    systemctl restart mongod
  EOF

  tags = ["mongodb", "database"]

  service_account {
    scopes = ["storage-ro", "logging-write", "monitoring-write"]
  }
}

resource "google_compute_firewall" "mongodb_firewall" {
  name    = "allow-mongodb"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["27017"]
  }

  source_tags = ["web"]
  target_tags = ["mongodb"]
}

// Variables
variable "project_id" {
  description = "The GCP Project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "us-central1-a"
} 