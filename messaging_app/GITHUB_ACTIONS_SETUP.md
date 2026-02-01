# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions workflows for the messaging app.

## Workflows

1. **CI Workflow** (`.github/workflows/ci.yml`): Runs Django tests on every push and pull request
2. **Docker Deployment Workflow** (`.github/workflows/dep.yml`): Builds and pushes Docker image to Docker Hub

## Setting Up Docker Hub Secrets

To use the Docker deployment workflow, you need to configure GitHub Secrets for Docker Hub authentication.

### Step 1: Create Docker Hub Access Token

1. Go to [Docker Hub](https://hub.docker.com/)
2. Log in to your account
3. Click on your username → **Account Settings**
4. Go to **Security** → **New Access Token**
5. Create a token with a descriptive name (e.g., "GitHub Actions")
6. Copy the token (you won't be able to see it again!)

### Step 2: Add Secrets to GitHub Repository

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   **Secret 1: DOCKER_HUB_USERNAME**
   - Name: `DOCKER_HUB_USERNAME`
   - Value: Your Docker Hub username (e.g., `littlegod20`)

   **Secret 2: DOCKER_HUB_TOKEN**
   - Name: `DOCKER_HUB_TOKEN`
   - Value: The access token you created in Step 1

### Step 3: Verify Secrets

After adding the secrets, they will appear in the secrets list (values are hidden for security).

## Workflow Details

### CI Workflow (ci.yml)

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to those branches
- Only runs when files in `messaging_app/**` change

**What it does:**
- Sets up Python 3.10
- Installs system and Python dependencies
- Sets up MySQL 8.0 service
- Runs database migrations
- Runs tests with pytest
- Publishes test results

### Docker Deployment Workflow (dep.yml)

**Triggers:**
- Push to `main`, `master`, or `develop` branches
- Pull requests to those branches
- Manual trigger via GitHub Actions UI

**What it does:**
- Sets up Docker Buildx
- Logs in to Docker Hub using secrets
- Builds Docker image from `messaging_app/Dockerfile`
- Tags the image with multiple tags (branch, SHA, latest)
- Pushes image to Docker Hub
- Uses build cache for faster builds

**Image Tags:**
- `littlegod20/django-messaging-app:latest` (on default branch)
- `littlegod20/django-messaging-app:main-<sha>` (branch + commit SHA)
- `littlegod20/django-messaging-app:<branch-name>` (branch name)

## Manual Workflow Trigger

You can manually trigger the Docker deployment workflow:

1. Go to your repository on GitHub
2. Click on **Actions** tab
3. Select **Build and Push Docker Image** workflow
4. Click **Run workflow**
5. Select the branch and click **Run workflow**

## Viewing Workflow Results

1. Go to the **Actions** tab in your repository
2. Click on a workflow run to see detailed logs
3. Check the build status and any errors
4. View test results and Docker image push status

## Troubleshooting

### Issue: Docker login fails

**Solution:**
- Verify `DOCKER_HUB_USERNAME` secret is correct
- Verify `DOCKER_HUB_TOKEN` secret is correct (use access token, not password)
- Ensure the access token has not expired

### Issue: Docker build fails

**Solution:**
- Check that the Dockerfile exists at `messaging_app/Dockerfile`
- Verify all dependencies in `Requirements.txt` are valid
- Check build logs for specific error messages

### Issue: Workflow doesn't trigger

**Solution:**
- Ensure you're pushing to the correct branch (`main`, `master`, or `develop`)
- Check that files in `messaging_app/**` were changed
- Verify the workflow file is at `.github/workflows/dep.yml` in the repository root

### Issue: Tests fail in CI workflow

**Solution:**
- Check MySQL service is running (wait step should handle this)
- Verify environment variables are set correctly
- Review test logs for specific test failures
- Ensure all dependencies are installed correctly

## Updating Docker Hub Repository Name

If you need to change the Docker Hub repository name:

1. Edit `.github/workflows/dep.yml`
2. Update the `DOCKER_HUB_REPO` environment variable:
   ```yaml
   env:
     DOCKER_HUB_REPO: your-dockerhub-username
   ```

## Security Best Practices

1. **Never commit secrets**: Always use GitHub Secrets
2. **Use access tokens**: Use Docker Hub access tokens instead of passwords
3. **Rotate tokens regularly**: Update access tokens periodically
4. **Limit token scope**: Create tokens with minimal required permissions
5. **Review workflow logs**: Regularly check workflow logs for any issues

## Next Steps

- Monitor workflow runs in the Actions tab
- Set up branch protection rules to require passing tests
- Configure deployment workflows for production environments
- Add notifications for workflow failures
