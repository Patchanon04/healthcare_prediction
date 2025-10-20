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
    COMPOSE_PROJECT_NAME = 'dogbreed'
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

              # Stop previous stack (same project name) and remove orphans
              docker-compose $ENV_ARG -f ${COMPOSE_FILE} down --remove-orphans || true

              # Safety net: remove any lingering named containers from older runs
              docker rm -f dogbreed_backend dogbreed_frontend dogbreed_db dogbreed_ml_service 2>/dev/null || true

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
            docker-compose -f ${COMPOSE_FILE} exec -T backend python manage.py makemigrations predictions || true
            docker-compose -f ${COMPOSE_FILE} exec -T backend python manage.py migrate
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
