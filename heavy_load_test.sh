#!/bin/bash

# Get the frontend service IP
FRONTEND_IP=$(kubectl get service todo-frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$FRONTEND_IP" ]; then
  echo "Could not get frontend IP, trying hostname instead..."
  FRONTEND_IP=$(kubectl get service todo-frontend-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
fi

if [ -z "$FRONTEND_IP" ]; then
  echo "Could not determine frontend service address. Exiting."
  exit 1
fi

echo "Frontend service found at: $FRONTEND_IP"
echo "Starting HEAVY load test - will run 500 parallel aggressive requests continuously"
echo "Press Ctrl+C to stop the test"

# Kill any existing frontend_load_test processes
pkill -f "frontend_load_test" || true

# Function to generate random query params to avoid caching
random_str() {
  cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 10 | head -n 1
}

# Run 500 parallel connections - much more aggressive
for i in {1..500}; do
  (
    while true; do
      # Add random query params to avoid caching
      RAND=$(random_str)
      
      # Make multiple rapid requests to static assets
      for j in {1..10}; do
        curl -s "http://$FRONTEND_IP/?nocache=$RAND-$j" > /dev/null &
        curl -s "http://$FRONTEND_IP/static/js/main.js?nocache=$RAND-$j" > /dev/null &
        curl -s "http://$FRONTEND_IP/static/css/main.css?nocache=$RAND-$j" > /dev/null &
        curl -s "http://$FRONTEND_IP/static/media/logo.png?nocache=$RAND-$j" > /dev/null &
      done
      wait
      
      # No sleep - continuously hammer the server
    done
  ) &
done

echo "HEAVY load test running in background. Monitor HPA with:"
echo "kubectl get hpa todo-frontend-hpa --watch"

# Keep script running
wait 