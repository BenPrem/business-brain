# Meta Graph API — Connecting a Client's Facebook Page and Instagram Account

Goal: obtain a **long-lived Page access token** for a client's Facebook Page (and its linked Instagram Business account) so your tooling can read posted content and insights programmatically.

**Time:** ~20 minutes, one-time per client. A long-lived user token survives ~60 days; Page tokens derived from it do not expire as long as the underlying user token stays valid and in periodic use.

**Prerequisite:** you need an **Admin or Editor** role on the client's Facebook Page. If you don't have it, the client grants it under Page Settings → Page Access / Page Roles.

Meta's flows and product names shift over time — if a screen below doesn't match, check the current Graph API docs at developers.facebook.com/docs/graph-api.

---

## Step 1 — Create a Meta Developer App (~5 min)

1. Go to https://developers.facebook.com/apps/
2. Click **Create App**.
3. Use case: **Other** → app type: **Business**.
4. Name it something recognizable (e.g., `<YOUR_AGENCY> Content Reader`), add your contact email, attach a Business Portfolio if you have one (optional).
5. Create the app; you'll land on its dashboard.

## Step 2 — Add Products (~2 min)

On the app dashboard, under **Add products**, set up:
- **Facebook Login for Business**
- **Instagram** (adds the Instagram Graph API)

Clicking "Set up" on each is sufficient; no further configuration needed for read access.

## Step 3 — Generate a Short-Lived User Token with the Right Scopes (~5 min)

1. Open the Graph API Explorer: https://developers.facebook.com/tools/explorer/
2. Select your app in the **Meta App** dropdown.
3. Token type: **User Token**.
4. Add these permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `instagram_basic`
   - `instagram_manage_insights`
   - `business_management`
5. Click **Generate Access Token** and approve the login popup, selecting the client's Page when asked which Pages to grant.
6. Copy the token shown. This is a **short-lived user token** (~1 hour). Don't store it anywhere permanent.

## Step 4 — Exchange for a Long-Lived User Token (~3 min)

```bash
APP_ID="<YOUR_APP_ID>"                 # app dashboard
APP_SECRET="<YOUR_APP_SECRET>"        # app dashboard → Settings → Basic
SHORT_TOKEN="<TOKEN_FROM_STEP_3>"

curl -sG "https://graph.facebook.com/v21.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=$APP_ID" \
  -d "client_secret=$APP_SECRET" \
  -d "fb_exchange_token=$SHORT_TOKEN"
```

The JSON response contains `"access_token": "..."` — the **long-lived user token** (~60 days).

## Step 5 — Get the Long-Lived Page Access Token (~2 min)

```bash
LONG_USER_TOKEN="<TOKEN_FROM_STEP_4>"
curl -sG "https://graph.facebook.com/v21.0/me/accounts" \
  -d "access_token=$LONG_USER_TOKEN"
```

The response lists every Page you manage. Find the client's Page and copy two values:
- `id` → this becomes `META_PAGE_ID`
- `access_token` → this becomes `META_ACCESS_TOKEN`. A Page token obtained from a long-lived user token does not expire while the user token remains valid.

## Step 6 — Get the Instagram Business Account ID (~1 min)

```bash
PAGE_ID="<META_PAGE_ID>"
PAGE_TOKEN="<META_ACCESS_TOKEN>"
curl -sG "https://graph.facebook.com/v21.0/$PAGE_ID" \
  -d "fields=instagram_business_account" \
  -d "access_token=$PAGE_TOKEN"
```

Response: `{"instagram_business_account": {"id": "<IG_BUSINESS_ID>"}}`. That id becomes `META_IG_ID`. (If the field comes back empty, the Instagram account isn't linked to the Page as a Business/Creator account — fix that in the Page's Instagram settings first.)

## Step 7 — Store in Your `.env` (~1 min)

Append to your project's `.env` file (which must be gitignored):

```
META_APP_ID=<YOUR_APP_ID>
META_APP_SECRET=<YOUR_APP_SECRET>
META_PAGE_ID=<PAGE_ID_FROM_STEP_5>
META_ACCESS_TOKEN=<PAGE_TOKEN_FROM_STEP_5>
META_IG_ID=<IG_BUSINESS_ID_FROM_STEP_6>
```

Never paste token values into chat with an agent — reference them by variable name only. Anything pasted into a conversation persists in plaintext transcript files.

## Step 8 — Test with a Real Call

```bash
PAGE_TOKEN=$(grep '^META_ACCESS_TOKEN=' .env | cut -d= -f2)
PAGE_ID=$(grep '^META_PAGE_ID=' .env | cut -d= -f2)
curl -sG "https://graph.facebook.com/v21.0/$PAGE_ID/posts" \
  -d "fields=message,created_time,permalink_url" \
  -d "limit=5" \
  -d "access_token=$PAGE_TOKEN"
```

A JSON list of the Page's recent posts means the connection is live. A configured integration is not "done" until a real call returns real data.

---

## Security Notes

- Treat `META_ACCESS_TOKEN` like a password — anyone holding it can act on the Page to the extent of its scopes.
- Never commit `.env`; confirm it's in `.gitignore` before the first commit.
- If a token leaks, invalidate it in the app dashboard and regenerate from Step 3.
- Review the app's granted permissions periodically in Meta Business Settings (business.facebook.com/settings).
- When a client relationship ends, have them remove your Page role and revoke the app.
