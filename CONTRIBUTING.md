# Contributing

Add a public Grok Bot template by pull request. One bot per PR when you can.

## Required

- A live official share link: `https://x.ai/bot/<id>`
- Name (as shown on the share page)
- One-line description (no prompt body)
- Category from the README section list

## Optional

- Twitter / X handle of the author, if it is already public. Written as `twitter` in `data/templates.json` (no `@`). Do not invent a handle.

That share link is the only URL you must provide.

## How to add

1. Confirm the share link opens and is meant to be copied by others.
2. Append one object to `data/templates.json`:

```json
{
  "name": "Example Bot",
  "description": "One line on what it does.",
  "category": "Engineering",
  "twitter": "handle",
  "share_url": "https://x.ai/bot/xxxxxxxxxxxxxxxxxxxxxxx",
  "scraped_at": "2026-08-29"
}
```

Use `twitter: null` when there is no public handle.

3. Add the same row to every README, under the matching category, alphabetically by name:

```markdown
- [Example Bot](https://x.ai/bot/xxxxxxxxxxxxxxxxxxxxxxx) — One line on what it does. [@handle](https://x.com/handle)
```

If `twitter` is null, stop after the description.

4. Run `python3 scripts/validate.py`.

## Rejected

- Private or broken share links
- Prompt packs, instruction dumps, memory files, packed configs
- Secrets, API keys, personal data
- Made-up `https://x.ai/bot/…` ids
- Invented Twitter handles
- Extra marketplace or directory URLs on the listing line

## Line format

```markdown
- [Name](https://x.ai/bot/ID) — one-line description. [@author](https://x.com/author)
```

Name links only to the official share URL.

## Categories

Assistants · Engineering · Research · Money · Sales · Creative · Life

## Conduct

Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 中文

用 PR 添加公开的 Grok Bot 模板。

**必填：** 真实可用的 `https://x.ai/bot/…` 分享链接、名称、一行简介、分类。

**可选：** 作者已公开的 Twitter/X 用户名（不要编造）。

不要提交提示词正文、打包配置、记忆转储或密钥。列表行里的名称只能指向官方分享链接。
