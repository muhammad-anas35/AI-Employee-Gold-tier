---
name: linkedin-poster
description: |
  Automatically post business content to LinkedIn for sales generation and professional presence.
  Creates post drafts with approval workflow, scheduling support, and engagement tracking. Use
  when you need to maintain LinkedIn presence, share business updates, or generate leads through
  social media. All posts require human approval before publishing.
---

# LinkedIn Poster

Automatically post business content to LinkedIn to generate sales leads and maintain professional presence.

## Overview

This skill enables automated posting to LinkedIn for business development, thought leadership, and sales generation. All posts require human approval before publishing to ensure quality and brand alignment.

## Usage

```bash
# Create a post draft
claude /post-linkedin --content "Your post content here"

# Schedule a post
claude /post-linkedin --content "Post content" --schedule "2026-03-13 09:00"

# Post with approval
claude /post-linkedin --content "Post content" --require-approval
```

## What It Does

1. **Creates post drafts** in `/Plans/POST_*.md`
2. **Requests approval** via `/Pending_Approval/`
3. **Posts to LinkedIn** after approval
4. **Tracks engagement** and logs results
5. **Schedules posts** for optimal timing

## Prerequisites

### LinkedIn API Access

**Option 1: LinkedIn API (Recommended for Production)**
1. Create LinkedIn App at [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Request API access (requires company page)
3. Get OAuth2 credentials
4. Add to `.env` file

**Option 2: Playwright Automation (Development)**
1. Install Playwright: `pip install playwright`
2. Run setup: `python scripts/linkedin_poster.py --setup`
3. Login manually (session saved)

## Configuration

### Environment Variables

```bash
# .env file
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_COMPANY_ID=your_company_id  # Optional

# Or for Playwright automation
LINKEDIN_SESSION_PATH=./linkedin_session
LINKEDIN_EMAIL=your@email.com
LINKEDIN_PASSWORD=your_password  # Use with caution
```

### Post Templates

Create templates in `AI_Employee_Vault/Templates/`:

```markdown
# templates/linkedin_business_update.md
---
type: linkedin_post
category: business_update
---

🚀 Exciting update from [Company Name]!

[Main content here]

What are your thoughts? Drop a comment below! 👇

#Business #Innovation #YourIndustry
```

## Post Workflow

```
Content Idea → Draft Created → /Pending_Approval/POST_*.md
                                        ↓
                              Human reviews & edits
                                        ↓
                              Moves to /Approved/
                                        ↓
                              LinkedIn Poster publishes
                                        ↓
                              Logs engagement → /Done/
```

## Action File Format

### Draft Post (Pending Approval)

```markdown
---
type: linkedin_post
status: pending_approval
created: 2026-03-12T20:28:00Z
scheduled_for: 2026-03-13T09:00:00Z
category: business_update
---

# LinkedIn Post Draft

## Post Content

🚀 Exciting news! We've just launched our new AI Employee automation system.

Key benefits:
✅ 24/7 autonomous operation
✅ 85% cost reduction
✅ Instant scalability

Interested in learning more? Let's connect!

#AI #Automation #BusinessInnovation

## Hashtags

#AI #Automation #BusinessInnovation #DigitalTransformation

## Target Audience

- Business owners
- CTOs and tech leaders
- Entrepreneurs

## Expected Engagement

- Reach: 500-1000
- Engagement rate: 3-5%

## To Approve

Move this file to `/Approved/` folder to publish.

## To Reject

Move this file to `/Rejected/` folder or edit and re-submit.
```

## Features

### Content Generation

```python
# Generate post from business update
claude /post-linkedin --generate \
  --topic "New product launch" \
  --tone "professional" \
  --length "medium"
```

### Scheduling

```python
# Schedule for optimal time
claude /post-linkedin --content "..." --schedule "next-business-day 09:00"

# Schedule multiple posts
claude /post-linkedin --batch posts.json
```

### Engagement Tracking

- Tracks likes, comments, shares
- Logs to `/Accounting/linkedin_engagement.json`
- Weekly engagement reports
- ROI analysis

### A/B Testing

```python
# Create variants for testing
claude /post-linkedin --content "Version A" --variant-of "post_123"
claude /post-linkedin --content "Version B" --variant-of "post_123"
```

## Best Practices

### Posting Frequency

- **Minimum:** 2-3 posts per week
- **Optimal:** 1 post per day
- **Maximum:** 2 posts per day

### Optimal Posting Times

- **Tuesday-Thursday:** 9 AM - 11 AM
- **Wednesday:** Best engagement day
- **Avoid:** Weekends, early mornings, late evenings

### Content Mix

- 40% Educational/Thought leadership
- 30% Company updates/News
- 20% Industry insights
- 10% Promotional

### Hashtag Strategy

- Use 3-5 relevant hashtags
- Mix popular and niche tags
- Create branded hashtag
- Research trending tags

## Security & Compliance

### LinkedIn Terms of Service

⚠️ **Important:** Automated posting must comply with LinkedIn's terms:
- Use official API when possible
- Avoid spam or excessive posting
- Maintain authentic engagement
- Don't automate comments/likes
- Respect rate limits

### Approval Workflow

**Always require approval for:**
- All posts (no auto-posting)
- Company announcements
- Client mentions
- Controversial topics

**Auto-approve (with caution):**
- Scheduled educational content
- Pre-approved templates
- Automated reports (with review)

### Brand Safety

- All posts reviewed by human
- Tone and style guidelines enforced
- No political or controversial content
- Professional language only
- Fact-checking required

## Monitoring

### Check Status

```bash
# View pending posts
ls -lt AI_Employee_Vault/Pending_Approval/POST_*.md

# View published posts
ls -lt AI_Employee_Vault/Done/POST_*.md

# Check engagement
cat AI_Employee_Vault/Accounting/linkedin_engagement.json | jq .
```

### Engagement Reports

```bash
# Generate weekly report
claude /linkedin-report --period "last-week"

# View top performing posts
claude /linkedin-report --top 10
```

## Troubleshooting

### "Authentication failed" error
```bash
# Re-authenticate
python scripts/linkedin_poster.py --setup

# Or refresh token
python scripts/linkedin_poster.py --refresh-token
```

### "Rate limit exceeded" error
- LinkedIn limits: 100 posts per day
- Reduce posting frequency
- Wait 24 hours before retry

### Post not appearing
- Check if post is in draft mode
- Verify approval was processed
- Check LinkedIn for errors
- Review logs for API errors

### Low engagement
- Review posting times
- Improve content quality
- Use better hashtags
- Engage with comments

## Advanced Usage

### Content Calendar

```python
# Create monthly content calendar
claude /linkedin-calendar --month "April 2026"

# Auto-schedule from calendar
claude /linkedin-schedule --calendar "april_2026.json"
```

### AI-Generated Content

```python
# Generate post from topic
claude /post-linkedin --generate \
  --topic "AI automation benefits" \
  --style "thought-leadership" \
  --include-stats

# Generate from company news
claude /post-linkedin --generate \
  --source "AI_Employee_Vault/Company_News.md"
```

### Integration with Sales

```python
# Track leads from LinkedIn
claude /linkedin-leads --export "leads.csv"

# Connect with CRM
claude /linkedin-sync --crm "odoo"
```

## Performance Metrics

### Track These KPIs

- **Impressions:** Total views
- **Engagement Rate:** (Likes + Comments + Shares) / Impressions
- **Click-through Rate:** Link clicks / Impressions
- **Follower Growth:** New followers per week
- **Lead Generation:** Inquiries from posts

### Target Benchmarks

- Engagement rate: 2-5%
- CTR: 0.5-2%
- Follower growth: 5-10% monthly
- Lead conversion: 1-3%

## Dependencies

```
# For API approach
requests==2.31.0
python-linkedin-v2==0.9.0

# For Playwright approach
playwright==1.41.0
```

## Alternative: LinkedIn Official API

For production use:
- [LinkedIn Marketing API](https://docs.microsoft.com/en-us/linkedin/marketing/)
- Official API with full features
- Requires company page
- Better rate limits
- Compliance-friendly

## See Also

- `/process-vault-tasks` - Process post drafts
- `/update-dashboard` - Track engagement metrics
- `Company_Handbook.md` - Social media guidelines
- `orchestrator.py` - Automated scheduling
