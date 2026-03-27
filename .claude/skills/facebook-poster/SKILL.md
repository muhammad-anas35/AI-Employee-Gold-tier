---
name: facebook-poster
description: Post content to Facebook using Playwright automation with approval workflow
---

# Facebook Poster Skill

Automatically post business content to Facebook using browser automation.

## Features

- Browser-based posting (no API credentials needed)
- Approval workflow for all posts
- Session persistence (login once)
- Screenshot proof of posting
- Support for text and images

## Usage

### Create a post

```bash
python .claude/skills/facebook-poster/scripts/facebook_poster.py --create "Your post content here"
```

### Publish approved posts

```bash
python .claude/skills/facebook-poster/scripts/facebook_poster.py --publish
```

### Test setup

```bash
python .claude/skills/facebook-poster/scripts/facebook_poster.py --test
```

## Workflow

1. Create post → saved to `/Pending_Approval/POST_facebook_*.md`
2. Human reviews and approves → moves to `/Approved/`
3. Script publishes from `/Approved/` folder
4. Takes screenshot proof
5. Moves to `/Done/` with timestamp

## First-Time Setup

On first run, the script will:
1. Open Facebook in browser
2. Ask you to log in manually
3. Save session for future use
4. All future posts are automatic

## Security

- Session cookies stored locally
- Never committed to Git
- All posts require human approval
