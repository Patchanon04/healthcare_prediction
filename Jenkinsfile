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
          withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USR', passwordVariable: 'DOCKER_PSW')]) {
            retry(3) {
              sh '''
                set -e
                echo "$DOCKER_PSW" | docker login -u "$DOCKER_USR" --password-stdin https://index.docker.io/v1/
                docker info | awk -F': ' '/Username/ {print $0}'; true
              '''
            }
          }
          retry(3) {
            sh '''
              set -e
              echo "Using compose: ${COMPOSE_FILE}"
              docker-compose -f ${COMPOSE_FILE} pull || true
              docker-compose -f ${COMPOSE_FILE} build --no-cache --pull
              docker-compose -f ${COMPOSE_FILE} up -d
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
