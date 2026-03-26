# Current Project Status - rus-portfolio-prod
**Last Updated**: March 25, 2026  
**Status**: ✅ FULLY OPERATIONAL — CI/CD ENABLED — BOTH SITES ON CLOUDFRONT

---

## 🎯 CURRENT STATE SUMMARY

### Website Status
- ✅ **Portfolio Site**: https://rus-teston.com — Fully operational
- ✅ **AI Projects Site**: https://ai.rus-teston.com — Fully operational (CloudFront added March 25, 2026)
- ✅ **WWW Support**: https://www.rus-teston.com — Working with proper SSL
- ✅ **Performance**: Sub-300ms response times globally
- ✅ **Security**: TLS 1.2+ on both sites, enterprise security headers
- ✅ **All Projects**: 10 portfolio projects + 8 AI projects live
- ✅ **CI/CD**: GitHub Actions + OIDC federation on both repos
- ✅ **Certifications**: 8 AWS certifications displayed (1 pursuing)

### Infrastructure Status
- ✅ **CloudFront (Portfolio)**: `E3IA5ZUL2HT0NT` — rus-teston.com, www.rus-teston.com
- ✅ **CloudFront (Lonestar)**: `E6LY7PZWUOBBP` — ai.rus-teston.com
- ✅ **Security Headers**: Enterprise-grade response headers policies on both distributions
- ✅ **S3 Buckets**: `rus-portfolio-prod` (portfolio), `ai-2026-project-lonestar` (AI projects)
- ✅ **DNS**: Route 53 with alias records for both sites
- ✅ **SSL**: ACM certificates covering all domains
- ✅ **CI/CD**: Auto-deploy + CloudFront invalidation on both repos

---

## 📊 INFRASTRUCTURE INVENTORY

### CloudFront Distributions
```
E3IA5ZUL2HT0NT (rus-teston.com, www.rus-teston.com)
├── Origin: rus-portfolio-prod.s3-website-us-east-1.amazonaws.com
├── Security Headers Policy: rus-portfolio-security-headers
├── Cache Behavior: /resume.html (PDF viewer compatible)
└── Cache Behavior: /projects/02-ai-agent/test.html (AI agent compatible)

E6LY7PZWUOBBP (ai.rus-teston.com)
├── Origin: ai-2026-project-lonestar.s3-website-us-east-1.amazonaws.com
├── Security Headers Policy: lonestar-security-headers (HSTS, CSP, X-Frame, XSS, Content-Type-Options)
├── TLS 1.2+, SNI, PriceClass_100
└── Custom error page: /error.html (404)
```

### Route 53
```
Hosted Zone: rus-teston.com (Z00478791SCIWJ5ZZ3U3T)
├── rus-teston.com → E3IA5ZUL2HT0NT (A alias)
├── www.rus-teston.com → E3IA5ZUL2HT0NT (A alias)
├── ai.rus-teston.com → E6LY7PZWUOBBP (A alias)
└── ACM validation CNAME for ai.rus-teston.com
```

### SSL Certificates
```
ACM (us-east-1):
├── 8ffff3b7... (ACTIVE) — rus-teston.com, www.rus-teston.com
├── 44d125cf... (ACTIVE) — ai.rus-teston.com
└── 25a7ce12... (unused)
```

### CI/CD Pipeline
```
GitHub Actions (OIDC Federation — no stored credentials)
IAM Role: GitHubActions-Deploy
├── S3: PutObject/GetObject/DeleteObject/ListBucket on both buckets
├── Lambda: UpdateFunctionCode in us-east-1
└── CloudFront: CreateInvalidation on E3IA5ZUL2HT0NT and E6LY7PZWUOBBP

Repos:
├── github.com/RusTeston/rus-portfolio-prod → S3 sync + CloudFront invalidation
└── github.com/RusTeston/AI-2026-Project-Lonestar → S3 deploy + CloudFront invalidation
```

---

## 🔄 RECENT CHANGES (March 25, 2026)

### CloudFront for Lonestar
- Created CloudFront distribution `E6LY7PZWUOBBP` for `ai.rus-teston.com`
- Requested and validated ACM certificate via Route 53
- Added Route 53 alias record
- Added security response headers policy
- Updated CI/CD workflow with CloudFront invalidation step
- Updated IAM role with new distribution permissions
- Migrated all S3 URLs to `https://ai.rus-teston.com` across all project pages, README, error page, and portfolio site

### Project Summary Modals
- Added clickable project summary modals to all 8 AI project pages
- Light theme modal for Projects 1, 3, 4, 5, 8
- Dark theme modal for Projects 6 (green accents), 7 (blue accents), 9 (blue accents)

### Project 9 Fixes
- Fixed Restore Healthy button to clear AI verdict and incident timeline
- Added `restored` flag to prevent auto-refresh from overwriting cleared state

### Portfolio Homepage Updates
- Added "U.S. Air Force Veteran" below tagline
- Updated AI Projects link to `https://ai.rus-teston.com/`

### Public Papers Page Updates
- Renamed "Cloud vs On-Prem" to "Full Report: Cloud vs On-Prem"
- Renamed "Example & Diagram" to "Business Example w/ Diagram"
- Renamed "IaC" to "IaC Templates"
- Removed emoji icons from section titles
- Added CloudFormation and Terraform lines under IaC Templates (Coming Soon)

### IaC Templates Page
- Removed Architecture Overview card (card 11)

### Takeaways Page Rewrite
- Complete rewrite reflecting full project evolution
- Updated timeline: S3 → CloudFront → IaC → AI projects → CI/CD → SAM → Step Functions
- Updated metrics: 19 projects shipped, 9 AI projects, 20+ AWS services, 2 live sites
- Updated lessons: OIDC, Bedrock prompt engineering, SAM, event-driven, security headers, cost awareness
- Matched Inter font and dark theme to rest of portfolio

### Workflow Rule Added
- New project rule: "After confirming changes are working, always commit and push to GitHub before moving to the next task"

---

## 🚨 OUTSTANDING ITEMS

### Maintenance Required
- 🔧 **Project 2 AI Agent**: Under maintenance — requires infrastructure rebuild
- ⏸️ **Lambda CORS tightening**: Deferred — requires SAM redeploys of Projects 6, 7, 9 + Lambda update for Project 1

### Non-Critical
- 🔄 **Project 5 Resources**: Stopped when not demoing (~$30-45/month savings)
- 🧹 **Mockup files**: `mockup-af-logo.html` and `mockup-takeaways.html` in rus-portfolio-prod root (can be cleaned up)
- 📜 **Unused ACM cert**: `25a7ce12...` can be deleted

---

## 📞 PROJECT CONTACTS

**Project Owner**: Rus Teston  
**Portfolio Site**: https://rus-teston.com  
**AI Projects Site**: https://ai.rus-teston.com  
**GitHub**: github.com/RusTeston  

---

*Both sites fully operational with HTTPS, CDN, CI/CD, and enterprise security headers.*
