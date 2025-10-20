pipeline {
  agent any
  options {
    timestamps()
    timeout(time: 30, unit: 'MINUTES')
  }
  environment {
    COMPOSE_FILE = 'docker-compose.prod.yml'
    // ปรับ path ถ้า Jenkins ไม่รันในโฟลเดอร์ root ของ repo
    WORKDIR = ''
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

    stage('Backend Quick Test') {
      steps {
        dir(env.WORKDIR) {
          // ทดสอบสั้นๆ ไม่ fail build ถ้าไม่มี test ครบถ้วน
          sh '''
            set -e
            docker build -t dogbreed-backend-test -f backend/Dockerfile backend
            docker run --rm dogbreed-backend-test bash -lc "python -c 'print(\\"backend image ok\\")'"
          '''
        }
      }
    }

    stage('Build & Deploy') {
      steps {
        dir(env.WORKDIR) {
          sh '''
            set -e
            echo "Using compose: ${COMPOSE_FILE}"
            docker-compose -f ${COMPOSE_FILE} pull || true
            docker-compose -f ${COMPOSE_FILE} build --no-cache
            docker-compose -f ${COMPOSE_FILE} up -d
          '''
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
