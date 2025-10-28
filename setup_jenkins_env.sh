#!/bin/bash
# Script to copy .env file to Jenkins container
# Usage: ./setup_jenkins_env.sh

set -e

echo "🔧 Setting up Jenkins environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found in current directory"
    echo "Please create .env file first"
    exit 1
fi

# Check if Jenkins container is running
if ! docker ps | grep -q medml_jenkins; then
    echo "❌ Error: Jenkins container (medml_jenkins) is not running"
    echo "Start Jenkins first with: docker-compose -f docker-compose.prod.yml up -d jenkins"
    exit 1
fi

echo "📄 Copying .env to Jenkins container..."

# Copy .env to Jenkins home directory
docker cp .env medml_jenkins:/var/jenkins_home/.env

echo "✅ .env copied to /var/jenkins_home/.env"

# Verify the file was copied
echo "🔍 Verifying..."
if docker exec medml_jenkins test -f /var/jenkins_home/.env; then
    echo "✅ Verification successful!"
    echo ""
    echo "📋 File contents preview:"
    docker exec medml_jenkins sh -c "head -5 /var/jenkins_home/.env | sed 's/=.*/=***HIDDEN***/' || echo 'Cannot read file'"
else
    echo "❌ Verification failed - file not found in container"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo "Jenkins can now access environment variables from /var/jenkins_home/.env"
echo ""
echo "Next steps:"
echo "1. Go to Jenkins UI: http://localhost:8080"
echo "2. Trigger a build to test the deployment"
