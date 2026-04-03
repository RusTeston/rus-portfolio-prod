# rus-portfolio-prod Rules

## Project Standards
- Always follow the Deployment Discipline Agreement - require explicit "APPROVED TO PROCEED" before each phase
- AWS region: us-east-1, Account ID: 901779867920
- All projects use static hosting (S3 + CloudFront)

## Deployment Patterns
- Frontend deploys to `s3://rus-portfolio-prod/`
- CloudFront Distribution: E3IA5ZUL2HT0NT (rus-teston.com)

## Code Practices
- Keep responses minimal - don't be verbose
- Read existing project code for patterns before making changes
- Match existing theme and style conventions per project page

## Deployment Discipline
<!-- See documentation/migration-reports/DEPLOYMENT-DISCIPLINE-AGREEMENT.md -->
- Minor changes (comments, text edits, doc updates, small fixes): proceed efficiently with approval
- Major changes (new pages, rewrites, new infrastructure, new projects): follow full Deployment Discipline Agreement
  - Propose → Review → Test Plan → Rollback Plan → "APPROVED TO PROCEED" → Execute → Validate → Document
  - Create mockup/preview before deploying to production
- After confirming changes are working, always commit and push to GitHub before moving to the next task

## Safety
- Preview HTML changes locally (open in browser) before deploying to S3
- Never deploy without explicit approval
- Always have a rollback plan
- Clean up test data from S3 after testing
- Back up current files before making UI changes
- Before any CI/CD workflow that syncs or deletes from S3, compare S3 contents against local files and download any S3-only files first
- Never use `--delete` flag on S3 sync without first verifying all S3 assets exist locally
