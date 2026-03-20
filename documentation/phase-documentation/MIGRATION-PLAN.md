# Rus Portfolio Production Migration Plan

**Project**: Migrate rus-teston.com to AWS Best Practices Structure  
**Date**: October 26, 2025  
**Status**: Planning Phase  

## 🎯 Migration Objectives

- ✅ Implement AWS S3 best practices for bucket organization
- ✅ Zero-downtime migration with safety rollback
- ✅ Maintain all current functionality (RAG, projects, etc.)
- ✅ Improve maintainability and scalability
- ✅ Document everything for future reference

## 📋 Current State Analysis

### Current Bucket: `rustestonsite`
```
rustestonsite/
├── index.html                              # Root homepage
├── site/                                   # Legacy structure
├── project2/                              # AI Agent with RAG
├── project3/                              # Cloud Assistant
├── project4/                              # Solution Showcase
├── project5/                              # HA Web Application
├── project6/                              # IaC Templates
├── project9/                              # CI/CD Pipeline
└── solution-showcase/                      # Duplicate content
```

**Issues Identified:**
- Mixed folder structure (some projects in root, some in folders)
- Duplicate content (project4 vs solution-showcase)
- No consistent naming convention
- Assets scattered across projects

## 🏗️ Target Architecture

### New Bucket: `rus-portfolio-prod`
```
rus-portfolio-prod/
├── assets/
│   ├── css/                               # Global stylesheets
│   ├── js/                                # Global JavaScript
│   ├── images/
│   │   ├── badges/                        # AWS certification badges
│   │   ├── architecture/                  # Architecture diagrams
│   │   └── screenshots/                   # Project screenshots
│   └── fonts/                             # Web fonts
├── projects/
│   ├── 01-website/
│   │   ├── index.html
│   │   └── assets/                        # Project-specific assets
│   ├── 02-ai-agent/
│   │   ├── index.html
│   │   ├── documents/                     # RAG documents
│   │   └── vectors/                       # TF-IDF vectors
│   ├── 03-cloud-assistant/
│   │   ├── index.html
│   │   └── assets/
│   ├── 04-solution-showcase/
│   │   ├── index.html
│   │   └── discovery-forms/               # 8 discovery templates
│   ├── 05-ha-webapp/
│   │   ├── index.html
│   │   └── assets/
│   ├── 06-iac-templates/
│   │   ├── index.html
│   │   ├── cloudformation/                # CF templates
│   │   └── terraform/                     # TF templates
│   └── 09-cicd-pipeline/
│       ├── index.html
│       └── assets/
├── static/
│   ├── security.html                      # Security showcase
│   ├── about.html                         # About page
│   └── contact.html                       # Contact page
└── index.html                             # Root portfolio homepage
```

## 🛡️ Migration Strategy: Zero-Downtime Approach

### Phase 1: Parallel Structure Creation
**Duration**: 1-2 hours  
**Risk**: None (current site stays live)

1. **Create new S3 bucket** `rus-portfolio-prod`
2. **Build folder structure** as defined above
3. **Copy and reorganize files** from current bucket
4. **Update HTML file paths** to match new structure
5. **Test new structure** via direct S3 URL

### Phase 2: CloudFront Configuration
**Duration**: 30 minutes  
**Risk**: Low (testing only)

1. **Create new CloudFront distribution** pointing to new bucket
2. **Configure caching behaviors** for different content types
3. **Test new distribution** thoroughly
4. **Verify all project functionality**

### Phase 3: DNS Switchover
**Duration**: 15 minutes  
**Risk**: Low (with rollback plan)

1. **Update Route 53** to point to new CloudFront distribution
2. **Monitor for issues** (15-30 minutes)
3. **Verify all projects working** on live domain
4. **Keep old infrastructure** as backup

### Phase 4: Cleanup (After 30 days)
**Duration**: 30 minutes  
**Risk**: None

1. **Delete old CloudFront distribution**
2. **Delete old S3 bucket** `rustestonsite`
3. **Update documentation**

## 📊 File Mapping Plan

| Current Location | New Location | Notes |
|------------------|--------------|-------|
| `rustestonsite/index.html` | `rus-portfolio-prod/index.html` | Root homepage |
| `rustestonsite/site/Badge PNG/` | `rus-portfolio-prod/assets/images/badges/` | AWS certifications |
| `rustestonsite/project2/` | `rus-portfolio-prod/projects/02-ai-agent/` | RAG AI Agent |
| `rustestonsite/project3/` | `rus-portfolio-prod/projects/03-cloud-assistant/` | Cloud Assistant |
| `rustestonsite/project4/` | `rus-portfolio-prod/projects/04-solution-showcase/` | Discovery forms |
| `rustestonsite/project5/` | `rus-portfolio-prod/projects/05-ha-webapp/` | HA Web App |
| `rustestonsite/project6/` | `rus-portfolio-prod/projects/06-iac-templates/` | IaC Templates |
| `rustestonsite/project9/` | `rus-portfolio-prod/projects/09-cicd-pipeline/` | CI/CD Pipeline |
| `rustestonsite/site/security.html` | `rus-portfolio-prod/static/security.html` | Security page |

## 🔧 Technical Implementation

### Required Scripts:
1. **`create-bucket-structure.sh`** - Creates new bucket and folder structure
2. **`migrate-content.py`** - Copies and reorganizes files
3. **`update-html-paths.py`** - Updates internal links in HTML files
4. **`test-migration.sh`** - Validates new structure
5. **`rollback-plan.sh`** - Emergency rollback procedure

### CloudFront Configuration:
```yaml
Origins:
  - DomainName: rus-portfolio-prod.s3.us-east-1.amazonaws.com
    OriginPath: ""
    
Behaviors:
  - PathPattern: "/assets/*"
    CachePolicyId: "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"  # CachingOptimized
  - PathPattern: "/projects/*"
    CachePolicyId: "b2884449-e4de-46a7-ac36-70bc7f1ddd6d"  # CachingDisabled
  - PathPattern: "/*"
    CachePolicyId: "658327ea-f89d-4fab-a63d-7e88639e58f6"  # CachingOptimizedForUncompressedObjects
```

## 💰 Cost Analysis

### Migration Period (30 days):
- **Current S3**: ~$0.83/month
- **New S3**: ~$0.83/month
- **Current CloudFront**: ~$1-2/month
- **New CloudFront**: ~$1-2/month
- **Total Extra Cost**: ~$2-3 for safety period

### Post-Migration:
- **Same ongoing costs** as current setup
- **Improved performance** due to better caching
- **Easier maintenance** = time savings

## 🚨 Risk Mitigation

### Rollback Plan:
1. **DNS Change**: Switch Route 53 back to old CloudFront (5 minutes)
2. **CloudFront**: Old distribution remains active during migration
3. **S3**: Original bucket preserved for 30 days
4. **Monitoring**: Real-time alerts for any issues

### Testing Checklist:
- [ ] All project pages load correctly
- [ ] RAG system functions properly
- [ ] All internal links work
- [ ] Images and assets display
- [ ] Forms submit successfully
- [ ] Mobile responsiveness maintained

## 📈 Success Metrics

### Performance:
- [ ] Page load times ≤ current performance
- [ ] All projects functional
- [ ] No broken links or missing assets

### Organization:
- [ ] Clear folder structure
- [ ] Consistent naming convention
- [ ] Easy to add new projects
- [ ] Simplified maintenance

### Documentation:
- [ ] Complete migration log
- [ ] Updated architecture documentation
- [ ] Rollback procedures tested
- [ ] Future maintenance guide

## 📝 Migration Log

### Pre-Migration Checklist:
- [ ] Complete backup of current site
- [ ] Document current CloudFront settings
- [ ] Test rollback procedures
- [ ] Prepare monitoring alerts

### Migration Execution:
- [ ] Phase 1: Create parallel structure
- [ ] Phase 2: Configure CloudFront
- [ ] Phase 3: DNS switchover
- [ ] Phase 4: Validation and monitoring

### Post-Migration:
- [ ] Performance validation
- [ ] Functionality testing
- [ ] Documentation updates
- [ ] Cleanup scheduling

---

**Next Steps:**
1. Review and approve this migration plan
2. Create migration scripts in this folder
3. Execute Phase 1 (parallel structure creation)
4. Test and validate before proceeding

**Contact**: Continue with Q for implementation support
**Emergency Rollback**: Documented procedures available