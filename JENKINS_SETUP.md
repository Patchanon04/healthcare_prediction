# Jenkins CI/CD Setup Guide

## 🎯 Overview
Auto-deploy เมื่อ push code ไป GitHub → Jenkins build → Deploy to EC2

## 📋 Prerequisites
- ✅ Jenkins ติดตั้งบน EC2 แล้ว
- ✅ Docker & Docker Compose บน EC2
- ✅ GitHub repository

---

## 🚀 Setup Steps

### 1. Configure Jenkins Job

#### A. Create New Pipeline Job
```
Jenkins Dashboard → New Item → Pipeline → OK
```

#### B. Configure Pipeline
**General:**
- ✅ GitHub project: `https://github.com/Patchanon04/dog_breed_prediction`

**Build Triggers:**
- ✅ GitHub hook trigger for GITScm polling

**Pipeline:**
- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `https://github.com/Patchanon04/dog_breed_prediction.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

---

### 2. Setup GitHub Webhook

#### A. Get Jenkins URL
```bash
# Your Jenkins URL (ใช้ Public IP ของ EC2)
http://54.179.8.155:8080/github-webhook/
```

#### B. Add Webhook in GitHub
1. Go to: `https://github.com/Patchanon04/dog_breed_prediction/settings/hooks`
2. Click: **Add webhook**
3. Configure:
   - **Payload URL:** `http://54.179.8.155:8080/github-webhook/`
   - **Content type:** `application/json`
   - **Which events:** `Just the push event`
   - ✅ Active
4. Click: **Add webhook**

---

### 3. Configure Jenkins Credentials

#### A. Add GitHub Credentials (if private repo)
```
Jenkins → Manage Jenkins → Credentials → System → Global credentials
→ Add Credentials
```
- Kind: `Username with password`
- Username: `Patchanon04`
- Password: `<GitHub Personal Access Token>`
- ID: `github-credentials`

#### B. Add SSH Key for EC2 (if needed)
```
Jenkins → Manage Jenkins → Credentials → System → Global credentials
→ Add Credentials
```
- Kind: `SSH Username with private key`
- ID: `ec2-ssh-key`
- Username: `ubuntu`
- Private Key: `<paste mlops-key.pem content>`

---

### 4. Setup .env File on Jenkins

```bash
# SSH to EC2
ssh -i ~/.ssh/mlops-key.pem ubuntu@54.179.8.155

# Create .env in Jenkins workspace
sudo mkdir -p /var/lib/jenkins
sudo cp ~/MLOPs/.env /var/lib/jenkins/.env
sudo chown jenkins:jenkins /var/lib/jenkins/.env
sudo chmod 600 /var/lib/jenkins/.env
```

---

### 5. Configure Jenkins Permissions

```bash
# Add jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# Verify
sudo -u jenkins docker ps
```

---

### 6. Install Jenkins Plugins

**Required Plugins:**
1. Git plugin
2. GitHub plugin
3. Pipeline plugin
4. Docker Pipeline plugin

```
Jenkins → Manage Jenkins → Plugins → Available plugins
→ Search and install above plugins
```

---

## 🎯 Test the Pipeline

### 1. Manual Trigger
```
Jenkins → Your Job → Build Now
```

### 2. Auto Trigger (Push to GitHub)
```bash
# Make a change
echo "test" >> README.md
git add README.md
git commit -m "test: trigger jenkins"
git push origin main

# Jenkins will auto-build!
```

---

## 📊 Pipeline Stages

1. **Checkout** - Pull latest code from GitHub
2. **Build & Deploy** - Build Docker images and start services
3. **DB Migrate** - Run database migrations automatically
4. **Update Nginx Config** - Update Nginx configuration
5. **Post-deploy Health Checks** - Verify services are healthy

---

## 🔍 Monitoring

### View Jenkins Logs
```
Jenkins → Your Job → Build #X → Console Output
```

### View Docker Logs
```bash
sudo docker compose -f docker-compose.prod.yml logs -f
```

### Check Service Status
```bash
sudo docker compose -f docker-compose.prod.yml ps
```

---

## 🐛 Troubleshooting

### Issue: Jenkins can't access Docker
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Issue: Webhook not triggering
1. Check GitHub webhook delivery (Settings → Webhooks → Recent Deliveries)
2. Verify Jenkins URL is accessible: `http://54.179.8.155:8080/github-webhook/`
3. Check Jenkins logs: `/var/log/jenkins/jenkins.log`

### Issue: Migrations fail
```bash
# Check backend logs
sudo docker compose -f docker-compose.prod.yml logs backend

# Run migrations manually
sudo docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Issue: Permission denied
```bash
# Fix ownership
sudo chown -R jenkins:jenkins /var/lib/jenkins/workspace/
```

---

## ✅ Success Criteria

After setup, when you push code:
1. ✅ GitHub webhook triggers Jenkins
2. ✅ Jenkins pulls latest code
3. ✅ Docker images rebuild
4. ✅ Services restart
5. ✅ Migrations run automatically
6. ✅ Health checks pass
7. ✅ Application is live!

---

## 🎉 Now You Can

```bash
# Just push code!
git add .
git commit -m "feat: new feature"
git push origin main

# Jenkins handles everything:
# - Build
# - Deploy
# - Migrate
# - Health checks
```

**No more manual deployment! 🚀**
