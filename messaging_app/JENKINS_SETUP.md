# Jenkins Setup Guide for Messaging App

This guide explains how to set up Jenkins and configure the CI/CD pipeline for the messaging app.

## Prerequisites

- Docker installed and running
- GitHub repository with the messaging app code
- Jenkins plugins: Git, Pipeline, ShiningPanda

## Step 1: Run Jenkins in Docker Container

Execute the following command to start Jenkins:

```bash
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
```

This command:
- Pulls the latest LTS Jenkins image
- Exposes Jenkins on port 8080
- Maps Jenkins home directory to persist data
- Exposes port 50000 for Jenkins agents

## Step 2: Access Jenkins Dashboard

1. Open your browser and navigate to: `http://localhost:8080`
2. Get the initial admin password:
   ```bash
   docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
   ```
3. Follow the setup wizard to install suggested plugins

## Step 3: Install Required Plugins

Install the following plugins via Jenkins Dashboard → Manage Jenkins → Manage Plugins:

1. **Git Plugin** - For GitHub integration
2. **Pipeline Plugin** - For Jenkinsfile support
3. **ShiningPanda Plugin** - For Python environment management
4. **HTML Publisher Plugin** - For test report display
5. **JUnit Plugin** - For test result reporting
6. **Cobertura Plugin** (optional) - For coverage reports

## Step 4: Configure GitHub Credentials

1. Go to Jenkins Dashboard → Manage Jenkins → Manage Credentials
2. Click on "System" → "Global credentials"
3. Click "Add Credentials"
4. Configure:
   - **Kind**: Username with password (or SSH Username with private key)
   - **Username**: Your GitHub username
   - **Password**: Your GitHub personal access token (or password)
   - **ID**: `github-credentials` (must match Jenkinsfile)
   - **Description**: GitHub credentials for messaging app

### Creating GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Copy the token and use it as the password in Jenkins credentials

## Step 5: Update Jenkinsfile

Before using the pipeline, update the Jenkinsfile with your GitHub repository URL:

1. Open `messaging_app/Jenkinsfile`
2. Update the GitHub URL:
   ```groovy
   url: 'https://github.com/YOUR_USERNAME/alx-backend-python.git'
   ```
3. Update the credentials ID if you used a different name:
   ```groovy
   credentialsId: 'github-credentials'
   ```
4. Update the branch name if needed:
   ```groovy
   branches: [[name: '*/main']]  // or '*/master', '*/develop', etc.
   ```

## Step 6: Create Jenkins Pipeline Job

1. Go to Jenkins Dashboard → New Item
2. Enter a job name (e.g., "messaging-app-pipeline")
3. Select "Pipeline" as the job type
4. Click OK
5. Configure the pipeline:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: Your GitHub repository URL
   - **Credentials**: Select the credentials you created
   - **Branch**: `*/main` (or your default branch)
   - **Script Path**: `messaging_app/Jenkinsfile`
6. Click Save

## Step 7: Run the Pipeline

1. Go to your pipeline job
2. Click "Build Now" to trigger the pipeline manually
3. Monitor the build progress in the console output
4. View test reports and coverage reports in the build results

## Pipeline Stages

The Jenkinsfile includes the following stages:

1. **Checkout**: Clones code from GitHub
2. **Setup Python Environment**: Creates and activates virtual environment
3. **Install Dependencies**: Installs requirements and pytest
4. **Run Database Migrations**: Sets up test database
5. **Run Tests with pytest**: Executes tests and generates reports
6. **Publish Test Results**: Publishes JUnit and HTML reports
7. **Test Summary**: Displays summary of test execution

## Test Reports

After pipeline execution, you can view:

- **JUnit Test Results**: In the build page under "Test Result"
- **HTML Test Report**: In the build page under "Pytest Test Report"
- **Coverage Report**: In the build page under "Coverage Report"

## Troubleshooting

### Issue: Tests fail because pytest-django is not installed

**Solution**: The pipeline installs pytest-django automatically. If it fails, ensure the virtual environment is activated correctly.

### Issue: Cannot connect to GitHub

**Solution**: 
- Verify GitHub credentials are correct
- Check if the repository URL is correct
- Ensure the personal access token has the `repo` scope

### Issue: Python not found

**Solution**: 
- Ensure Python 3.10+ is installed on the Jenkins agent
- The ShiningPanda plugin can help manage Python versions

### Issue: Database connection errors

**Solution**: The pipeline uses SQLite for testing. If you need MySQL, configure it in the pipeline or use Docker containers.

## Manual Pipeline Trigger

The pipeline is configured to allow manual triggers. Simply click "Build Now" in the Jenkins dashboard whenever you want to run the pipeline.

## Next Steps

- Add more test cases to improve coverage
- Configure automatic triggers (webhooks) for GitHub pushes
- Add deployment stages to the pipeline
- Set up email notifications for build results
