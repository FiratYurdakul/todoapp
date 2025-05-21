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

# Create a simple status file to check if setup completed
echo "MongoDB setup completed at $(date)" > /var/log/mongodb-setup-complete.log 