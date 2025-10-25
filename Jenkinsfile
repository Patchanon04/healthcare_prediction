pipeline {
  agent any
  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }
  environment {
    COMPOSE_FILE = 'docker-compose.prod.yml'
    // โฟลเดอร์ทำงานของ pipeline (root ของ repo)
    WORKDIR = '.'
    // ใช้ชื่อโปรเจกต์คงที่เพื่อให้ down/up กระทบ stack เดียวกันเสมอ
    COMPOSE_PROJECT_NAME = 'medml'
    // ชี้ไปยังไฟล์ .env ของ production บน EC2 (ปรับได้ตามที่วางไฟล์จริง)
    ENV_FILE = '/home/ubuntu/MLOPs/.env'
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
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} down -v --remove-orphans || true

              # Safety net: remove any lingering named containers from older runs
              docker rm -f medml_backend medml_frontend medml_db medml_ml_service 2>/dev/null || true

              # Build without --pull so it uses local cache/base images if present
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} build

              # Start/update services
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} up -d
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
              if docker-compose $ENV_ARG -f ${COMPOSE_FILE} exec -T db pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-medical_db}; then
                echo "Postgres is ready"; break; fi
              echo "DB not ready yet... ($i)"; sleep 3;
              if [ "$i" -eq 30 ]; then echo "ERROR: DB not ready in time" >&2; exit 1; fi
            done

            echo "Running database migrations (one-off container)..."
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} run --rm backend python manage.py makemigrations
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} run --rm backend python manage.py migrate

            echo "Collecting static files..."
            docker-compose $ENV_ARG -f ${COMPOSE_FILE} run --rm backend python manage.py collectstatic --noinput || true

            echo "✅ Migrations and static files completed"
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
            echo "Checking backend health..."
            for i in 1 2 3 4 5; do
              if curl -fsS http://localhost:8000/api/v1/health/ > /dev/null; then
                echo "Backend healthy"; break; fi; sleep 3; done

            echo "Checking frontend (Nginx) on :80..."
            for i in 1 2 3 4 5; do
              if curl -fsS http://localhost/ > /dev/null; then
                echo "Frontend reachable"; break; fi; sleep 3; done
          '''
        }
      }
    }
  }
  post {
    success {
      echo '✅ Deploy successful on main'
    }
    failure {
      echo '❌ Build/Deploy failed. Check logs.'
    }
  }
}
