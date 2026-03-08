---
name: linkedin-poster
description: |
  Automatically post to LinkedIn about business updates to generate sales.
  Uses Playwright for browser automation. Use when you need to schedule
  and publish LinkedIn posts, engage with content, or grow professional network.
---

# LinkedIn Poster Skill

Automatically create and publish LinkedIn posts to promote business and generate sales.

## Overview

The LinkedIn Poster is a **Silver Tier** AI Employee skill that:
- Creates LinkedIn posts from business updates
- Schedules posts for optimal engagement times
- Uses Playwright for browser automation
- Tracks post performance
- Maintains brand voice consistency

## Prerequisites

### 1. Install Dependencies

```bash
cd AI_Employee_Vault/watchers
pip install playwright
playwright install chromium
```

### 2. LinkedIn Account

- Active LinkedIn account
- Company page (optional, for business posts)
- Be aware of LinkedIn's Terms of Service

## Usage

### Basic Usage

```bash
# Create and schedule post
python watchers/linkedin_poster.py --action create --topic "business_update"

# Review draft posts
python watchers/linkedin_poster.py --action list_drafts

# Publish scheduled posts
python watchers/linkedin_poster.py --action publish
```

### Post Creation with Qwen

```bash
# Create post from business goals
qwen "Create a LinkedIn post about our Q1 2026 business achievements. Include engagement hooks and relevant hashtags."

# Create post from recent wins
qwen "Draft a LinkedIn post celebrating our recent client success. Keep it professional but engaging."
```

## Post Templates

### Business Update Template

```markdown
---
type: linkedin_post
status: draft
created: 2026-02-25T10:30:00Z
scheduled: 2026-02-26T09:00:00Z
topic: business_update
tone: professional
---

# LinkedIn Post: Business Update

## Content

🚀 Exciting news! 

We just completed [achievement] for [client/industry]. 

Here's what we learned:
• Key insight 1
• Key insight 2
• Key insight 3

Ready to transform your [business area]? Let's connect!

#Hashtag1 #Hashtag2 #Hashtag3

## Media
- [ ] Add relevant image
- [ ] Add company logo
- [ ] Include link to blog post

## Engagement Goals
- Target impressions: 1000+
- Target engagements: 50+
- Target leads: 5+

---
*Created by LinkedInPoster v0.1.0*
```

### Client Success Template

```markdown
---
type: linkedin_post
status: draft
topic: client_success
---

# LinkedIn Post: Client Success Story

## Content

📈 Client Success Story

Helped [Client Name] achieve [specific result] in [timeframe].

The challenge: [brief description]
Our solution: [brief description]  
The result: [quantifiable outcome]

Proud of what we accomplished together!

#ClientSuccess #Results #Industry

## Media
- Before/after metrics graphic
- Client testimonial (with permission)
```

### Thought Leadership Template

```markdown
---
type: linkedin_post
status: draft
topic: thought_leadership
---

# LinkedIn Post: Industry Insight

## Content

💡 Hot take: [contrarian or insightful opinion]

Most people think [common belief], but here's what I've learned:

[Insight 1]
[Insight 2]
[Insight 3]

What's your experience? Drop a comment 👇

#ThoughtLeadership #Industry #Insights
```

## Posting Schedule

### Optimal Times

| Day | Best Times (local) |
|-----|-------------------|
| Tuesday | 9-11 AM, 12 PM |
| Wednesday | 9-11 AM, 12 PM |
| Thursday | 9-11 AM, 12 PM |
| Monday | 10 AM - 12 PM |
| Friday | 10 AM - 11 AM |

### Recommended Frequency

- **Minimum:** 2 posts per week
- **Optimal:** 3-5 posts per week
- **Maximum:** 1 post per day

## Content Calendar

Create `Content_Calendar.md`:

```markdown
# LinkedIn Content Calendar - February 2026

| Date | Topic | Status | Scheduled Time |
|------|-------|--------|----------------|
| Mon 2/24 | Client Success | ✅ Published | 9:00 AM |
| Wed 2/26 | Business Update | ⏰ Scheduled | 10:00 AM |
| Fri 2/28 | Thought Leadership | 📝 Draft | 11:00 AM |
```

## Integration with Business Goals

### Post from Business_Goals.md

```bash
qwen "Read Business_Goals.md Q1 objectives and create 4 LinkedIn posts that align with our revenue target. Schedule throughout the month."
```

### Post from Completed Tasks

```bash
qwen "Review Done folder for this week's completed projects. Create LinkedIn posts highlighting 2-3 client wins."
```

## Engagement Workflow

### Auto-Engagement (Optional)

```python
# Engage with comments on posts
def engage_with_comments():
    for comment in get_new_comments():
        if comment.is_question():
            draft_response(comment)
        elif comment.is_positive():
            like_and_thank(comment)
```

### Lead Capture

```python
# Track inbound leads from LinkedIn
def capture_lead(profile, message):
    create_action_file({
        'type': 'linkedin_lead',
        'profile': profile,
        'message': message,
        'priority': 'high'
    })
```

## Best Practices

### Content
1. **Hook first:** First 2 lines determine engagement
2. **Use emojis:** 2-4 relevant emojis per post
3. **Add hashtags:** 3-5 relevant hashtags
4. **Include CTA:** Tell readers what to do next
5. **Keep it scannable:** Short paragraphs, bullet points

### Timing
1. **Post consistently:** Same days/times build audience
2. **Test and learn:** Track which times work best
3. **Avoid weekends:** Lower B2B engagement

### Engagement
1. **Respond quickly:** Reply to comments within 2 hours
2. **Ask questions:** Encourage discussion
3. **Tag relevant parties:** Increase reach (sparingly)

## Security Considerations

- ✅ Session stored locally
- ✅ No credentials in vault
- ✅ All posts logged before publishing
- ⚠️ LinkedIn ToS may restrict automation
- ⚠️ Use personal account at own risk
- ⚠️ Consider LinkedIn Marketing API for business

## Troubleshooting

### Issue: Login Failed

**Solutions:**
1. Clear browser cache
2. Re-authenticate manually
3. Check for LinkedIn captcha
4. Verify account is in good standing

### Issue: Post Not Publishing

**Solutions:**
1. Check post length (< 3000 characters)
2. Verify media files exist
3. Review LinkedIn for outages
4. Check session is valid

## Metrics to Track

| Metric | Target | Tracking |
|--------|--------|----------|
| Impressions | 1000+ per post | LinkedIn Analytics |
| Engagement Rate | 3%+ | Likes + Comments / Impressions |
| Profile Views | 50+ per week | LinkedIn Analytics |
| Connection Requests | 20+ per week | Manual count |
| Inbound Leads | 5+ per week | Needs_Action folder |

## Related Skills

- **WhatsApp Watcher** - Monitor for urgent messages
- **Gmail Watcher** - Process email inquiries
- **Approval Workflow** - Approve posts before publishing
- **Task Scheduler** - Schedule posting times

## Reference

- [LinkedIn Marketing Solutions](https://business.linkedin.com/)
- [Playwright Documentation](https://playwright.dev/python/)
- [Company Handbook](Company_Handbook.md) - Brand voice guidelines
- [Business_Goals.md](Business_Goals.md) - Content alignment

---

*LinkedIn Poster Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
