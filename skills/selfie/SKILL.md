---
name: aigf-selfie
description: >
  AI girlfriend selfie skill. Generates realistic selfie photos using Volcengine Seedream 4.5
  and sends them via Feishu/QQ. Scene, outfit, and mood are driven by aigf-core.
  When user asks for a selfie or says things like "what are you doing", "send me a photo",
  execute: python3 ~/.openclaw/skills/selfie/selfie.py "<channel_id>" "<scene>" "" "<msg_id>"
  Then poll with timeout 120000 until output contains [SELFIE_SENT_ASYNC] or [SELFIE_FAILED].
---

# AI Girlfriend Selfie Skill

Generates selfie photos with consistent face, mood-driven expressions, weather-based outfits,
and time-aware scenes.

## Usage

```bash
python3 ~/.openclaw/skills/selfie/selfie.py "<channel_id>" "<scene_description>" "" "<msg_id>"
```

## Dependencies

- aigf-core (mood, scene, outfit systems)
- Volcengine Seedream 4.5 API
- Reference image: ref_small.jpeg (place in this directory)
