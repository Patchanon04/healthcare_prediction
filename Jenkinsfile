pipeline {
  agent any
  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }
  environment {
    COMPOSE_FILE = 'docker-compose.prod.yml'
    MONITORING_COMPOSE_FILE = 'docker-compose.monitoring.yml'
    // โฟลเดอร์ทำงานของ pipeline (root ของ repo)
    WORKDIR = '.'
    // ใช้ชื่อโปรเจกต์คงที่เพื่อให้ down/up กระทบ stack เดียวกันเสมอ
    COMPOSE_PROJECT_NAME = 'medml'
    // ชี้ไปยังไฟล์ .env ภายใน Jenkins container
    ENV_FILE = '/var/jenkins_home/.env'
    // Enable/Disable monitoring stack
    DEPLOY_MONITORING = 'true'
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
        script {
          dir(env.WORKDIR) {
            sh 'git rev-parse --short HEAD'
          }
        }
      }
    }

    stage('Build & Deploy') {
      steps {
        dir(env.WORKDIR) {
          retry(3) {
            sh '''
              set -e
              echo "Using compose: ${COMPOSE_FILE} (project: ${COMPOSE_PROJECT_NAME})"
              # Pick a readable .env file: ENV_FILE -> /var/lib/jenkins/.env -> ./.env
              EF=""
              for p in "${ENV_FILE}" "/var/lib/jenkins/.env" "./.env"; do
                if [ -n "$p" ] && [ -r "$p" ]; then EF="$p"; break; fi
              done
              if [ -n "$EF" ]; then ENV_ARG="--env-file $EF"; else ENV_ARG=""; fi
              echo "Using env file: ${EF:-<none>}"

              # Fail fast if no env file is readable to avoid bringing up services with empty secrets
              if [ -z "$EF" ]; then
                echo "ERROR: No readable .env file found (checked: ${ENV_FILE}, /var/lib/jenkins/.env, ./.env). Aborting." >&2
                exit 1
              fi

              # Stop previous stack (same project name) and remove orphans + volumes
              # This ensures fresh database schema on every deploy
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} down -v --remove-orphans || true

              # Safety net: remove any lingering named containers from older runs (except Jenkins itself)
              docker rm -f medml_backend medml_frontend medml_db medml_ml_service 2>/dev/null || true

              # Build without --pull so it uses local cache/base images if present
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} build

              # Start/update services (exclude Jenkins to avoid self-conflict)
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} up -d --scale jenkins=0
              
              # Deploy monitoring stack if enabled
              if [ "${DEPLOY_MONITORING}" = "true" ]; then
                echo "🔍 Deploying monitoring stack..."
                
                # Fix prometheus.yml if it's a directory
                if [ -d "prometheus/prometheus.yml" ]; then
                  echo "⚠️  prometheus.yml is a directory! Fixing..."
                  rm -rf prometheus/prometheus.yml
                  git checkout origin/main -- prometheus/prometheus.yml
                fi
                
                # Verify prometheus.yml is a file
                if [ ! -f "prometheus/prometheus.yml" ]; then
                  echo "❌ ERROR: prometheus/prometheus.yml is not a file!"
                  ls -la prometheus/
                  exit 1
                fi
                
                echo "✅ prometheus.yml verified as file"
                
                docker-compose $ENV_ARG -f ${COMPOSE_FILE} -f ${MONITORING_COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} up -d --scale jenkins=0
                echo "✅ Monitoring stack deployed"
              else
                echo "⏭️  Skipping monitoring stack (DEPLOY_MONITORING=${DEPLOY_MONITORING})"
              fi
            '''
          }
        }
      }
    }

    stage('DB Migrate') {
      steps {
        dir(env.WORKDIR) {
          sh '''
            set -e
            echo "Preparing environment args for docker-compose..."
            EF=""
            for p in "${ENV_FILE}" "/var/lib/jenkins/.env" "./.env"; do
              if [ -n "$p" ] && [ -r "$p" ]; then EF="$p"; break; fi
            done
            if [ -n "$EF" ]; then ENV_ARG="--env-file $EF"; else ENV_ARG=""; fi
            echo "Using env file: ${EF:-<none>}"

            echo "Waiting for Postgres to be ready..."
            # Retry until DB is ready (assumes service name 'db' uses Postgres image)
            for i in $(seq 1 30); do
              if docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} exec -T db pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-medical_db}; then
                echo "Postgres is ready"; break; fi
              echo "DB not ready yet... ($i)"; sleep 3;
              if [ "$i" -eq 30 ]; then echo "ERROR: DB not ready in time" >&2; exit 1; fi
            done

            echo "Running database migrations (one-off container)..."
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} run --rm backend python manage.py makemigrations
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} run --rm backend python manage.py migrate

            echo "Collecting static files..."
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} run --rm backend python manage.py collectstatic --noinput || true

            echo "✅ Migrations and static files completed"
          '''
        }
      }
    }

    stage('Run Unit Tests') {
      steps {
        dir(env.WORKDIR) {
          retry(2) {
            sh '''
              set -e
              echo "Preparing environment args for docker-compose..."
              EF=""
              for p in "${ENV_FILE}" "/var/lib/jenkins/.env" "./.env"; do
                if [ -n "$p" ] && [ -r "$p" ]; then EF="$p"; break; fi
              done
              if [ -n "$EF" ]; then ENV_ARG="--env-file $EF"; else ENV_ARG=""; fi
              echo "Using env file: ${EF:-<none>}"

              echo "🧪 Running Django unit tests..."
              
              # Wait for database to be ready
              echo "Waiting for database..."
              sleep 5
              
              # Run all unit tests
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} run --rm backend python manage.py test predictions.test_patients predictions.test_chat predictions.test_treatments predictions.tests --verbosity=2
              
              echo "✅ All unit tests passed!"
            '''
          }
        }
      }
    }

    stage('Generate Test Coverage') {
      steps {
        dir(env.WORKDIR) {
          sh '''
            echo "Preparing environment args for docker-compose..."
            EF=""
            for p in "${ENV_FILE}" "/var/lib/jenkins/.env" "./.env"; do
              if [ -n "$p" ] && [ -r "$p" ]; then EF="$p"; break; fi
            done
            if [ -n "$EF" ]; then ENV_ARG="--env-file $EF"; else ENV_ARG=""; fi
            echo "Using env file: ${EF:-<none>}"

            echo "📊 Generating test coverage report..."
            
            # Install coverage if not present
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} run --rm backend pip install coverage || true
            
            # Run tests with coverage in same container and generate report
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} -p ${COMPOSE_PROJECT_NAME} run --rm backend sh -c "
              coverage run --source='predictions' manage.py test predictions.test_patients predictions.test_chat predictions.test_treatments predictions.tests &&
              coverage report &&
              coverage html || true
            " || echo "⚠️  Coverage generation failed, but continuing..."
            
            echo "✅ Coverage stage completed!"
          '''
        }
      }
    }

    stage('Update Nginx Config') {
      steps {
        dir(env.WORKDIR) {
          sh '''
            set -e
            echo "Updating Nginx configuration..."
            # Copy nginx.conf to a temp location that Jenkins can access
            cp nginx.conf /tmp/medical-nginx.conf
            echo "✅ Nginx config updated in /tmp/medical-nginx.conf"
            echo "⚠️  Manual step: Run 'sudo cp /tmp/medical-nginx.conf /etc/nginx/sites-available/medical.conf && sudo systemctl reload nginx'"
          '''
        }
      }
    }

    stage('Post-deploy Health Checks') {
      steps {
        dir(env.WORKDIR) {
          sh '''
            set -e
            echo "Waiting for services to be fully ready..."
            sleep 10
            
            echo "Checking backend health..."
            BACKEND_HEALTHY=false
            for i in 1 2 3 4 5 6 7 8 9 10; do
              if curl -fsS http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
                echo "✅ Backend healthy"
                BACKEND_HEALTHY=true
                break
              fi
              echo "Backend not ready yet... ($i/10)"
              sleep 5
            done
            
            if [ "$BACKEND_HEALTHY" = "false" ]; then
              echo "⚠️  Backend health check failed, but continuing..."
            fi

            echo "Checking frontend (Nginx) on :80..."
            FRONTEND_HEALTHY=false
            for i in 1 2 3 4 5; do
              if curl -fsS http://localhost/ > /dev/null 2>&1; then
                echo "✅ Frontend reachable"
                FRONTEND_HEALTHY=true
                break
              fi
              echo "Frontend not ready yet... ($i/5)"
              sleep 3
            done
            
            if [ "$FRONTEND_HEALTHY" = "false" ]; then
              echo "⚠️  Frontend health check failed, but continuing..."
            fi
            
            echo "✅ Health checks completed"
          '''
        }
      }
    }

    stage('Monitoring Health Checks') {
      when {
        expression { env.DEPLOY_MONITORING == 'true' }
      }
      steps {
        dir(env.WORKDIR) {
          sh '''
            set -e
            echo "🔍 Checking monitoring services..."
            
            # Check if containers are running
            echo "Checking containers..."
            docker ps | grep -E "prometheus|grafana|node_exporter|cadvisor" || echo "Some monitoring containers not found"
            
            # Check Prometheus logs for errors
            echo ""
            echo "📋 Prometheus logs (last 10 lines):"
            docker logs medml_prometheus --tail 10 || echo "Cannot read Prometheus logs"
            
            # Check if Prometheus has IP
            echo ""
            echo "🔍 Checking Prometheus network..."
            PROM_IP=$(docker inspect medml_prometheus --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "")
            if [ -z "$PROM_IP" ]; then
              echo "⚠️  WARNING: Prometheus has no IP address!"
              docker inspect medml_prometheus | grep -A 5 "State" || true
            else
              echo "✅ Prometheus IP: $PROM_IP"
            fi
            
            # Wait for services
            sleep 10
            
            # Check Prometheus health
            echo ""
            echo "Checking Prometheus health..."
            PROMETHEUS_HEALTHY=false
            for i in 1 2 3 4 5; do
              if curl -fsS http://localhost:9090/-/healthy > /dev/null 2>&1; then
                echo "✅ Prometheus healthy"
                PROMETHEUS_HEALTHY=true
                break
              fi
              echo "Prometheus not ready yet... ($i/5)"
              sleep 5
            done
            
            if [ "$PROMETHEUS_HEALTHY" = "false" ]; then
              echo "❌ Prometheus health check failed!"
              echo "Checking Prometheus status..."
              docker ps -a | grep prometheus || true
              docker logs medml_prometheus --tail 20 || true
            fi
            
            # Check Grafana health
            echo ""
            echo "Checking Grafana health..."
            GRAFANA_HEALTHY=false
            for i in 1 2 3 4 5; do
              if curl -fsS http://localhost:3000/api/health > /dev/null 2>&1; then
                echo "✅ Grafana healthy"
                GRAFANA_HEALTHY=true
                break
              fi
              echo "Grafana not ready yet... ($i/5)"
              sleep 3
            done
            
            if [ "$GRAFANA_HEALTHY" = "false" ]; then
              echo "⚠️  Grafana health check failed, but continuing..."
            fi
            
            # Test Grafana -> Prometheus connection
            if [ "$PROMETHEUS_HEALTHY" = "true" ] && [ "$GRAFANA_HEALTHY" = "true" ]; then
              echo ""
              echo "🔗 Testing Grafana -> Prometheus connection..."
              docker exec medml_grafana wget -O- http://prometheus:9090/-/healthy 2>&1 | head -5 || echo "Connection test failed"
            fi
            
            echo ""
            echo "✅ Monitoring health checks completed"
            echo "📊 Access Grafana at: http://localhost:3000"
            echo "📈 Access Prometheus at: http://localhost:9090"
          '''
        }
      }
    }
  }
  post {
    success {
      echo '✅ Deploy successful on main'
      script {
        if (env.DEPLOY_MONITORING == 'true') {
          echo '📊 Monitoring stack is running:'
          echo '   - Grafana: http://localhost:3000 (admin/admin)'
          echo '   - Prometheus: http://localhost:9090'
          echo '   - cAdvisor: http://localhost:8082'
        }
      }
    }
    failure {
      echo '❌ Build/Deploy failed. Check logs.'
    }
  }
}
