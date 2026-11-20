# Answers to Lisa · second list · 20 November 2026

Your new site is updated (version 7): https://headless-znxwbqojlvv-kiwixteam-1409.wix-site-host.com (a temporary Wix address; cirenza.com comes at launch).
"Done" means you can see it on the site today. "Proposed" means a rule for you to confirm.

---

## 1. Portfolio, and Commissions and Available Works (done)

- **Portfolio:**
  - "Works" is now **Portfolio**, in your Artist menu.
  - Its web address stays "works" for now. We can change it at launch, with a redirect.
- **"Enquire about this work":**
  - It replaces the availability on every Portfolio work.
  - It opens an email to **atelier@cirenza.com** with the work's title.
  - No price is shown on the Portfolio.
- **Commissions and Available Works:** this is the new name of the shop. At the top:
  - a Commissions block, ready for your text and photos (for now, three commissions from the Portfolio stand in);
  - a **"Discuss a commission"** button;
  - a link to your past commissions.
- **Prices:**
  - Every work shown as available displays its price.
  - On the mock-up, works whose price isn't public yet read "Price to come from Artwork Archive".
  - At launch, each available work shows its Artwork Archive price, unless you choose "price on request" (point 2).

## 2. How Artwork Archive feeds the two pages

**What Artwork Archive offers:**
- **No public API.** A website cannot read your account directly.
- **An export to CSV or Excel** (Pieces › New Report › Export to CSV). It includes the links to your images.
- **An embed code.** It shows your public portfolio in Artwork Archive's own design, so it doesn't fit your site.

**Our setup:**
- Artwork Archive stays your master inventory.
- Each update copies your works into your Wix back office: works, prices and images.
- The site reads them from Wix.

**Timing**
- **When updates happen:** Artwork Archive can't send changes on its own, so nothing is instant and nothing runs on a schedule.
- **You trigger the update yourself, in two steps:**
  1. Export your pieces to CSV in Artwork Archive.
  2. Drop the file on a private "Update works" page that only you can open.
- **How fast:** the site shows the changes within a few minutes.
- **When to do it:** after a new work, a price change or a sale made elsewhere. Otherwise once a week is plenty.
- **Sales on the site** need no update. The work is reserved straight away and you get an email reminding you to click "Register Sale" in Artwork Archive.

**Selection (proposed)**
- **Portfolio:** every piece set to **Public** in Artwork Archive that has at least one image. Private pieces never appear.
- **Commissions and Available Works:** public pieces whose **status is Available**.
- **Sold:** on the next update, the work leaves the available page and stays in the Portfolio, with "Enquire about this work" and no price.
- **Not for sale, on loan, reserved:** Portfolio only.
- **Series:** your Artwork Archive **Collections** become the rooms of the Portfolio.
- **To check:** we'll confirm on your real export that the Public setting, collections and tags come across. If one doesn't, the same choice can be made with a tag.

**Photos**
- **Which images:** all the images of a piece, in their Artwork Archive order.
- **Lead image:** the first one, the primary image you choose in Artwork Archive, leads. The others become detail shots in the work's sheet.
- **To check:** whether the export lists every image or only the primary one. We'll see on your real export.
- **Resolution and speed:**
  - We import the full-resolution file once into Wix.
  - Wix then sends each visitor the size their screen needs, in light modern formats: small in the grids, large for the zoom.
  - Your originals stay sharp and the pages stay fast.

**Information**
- **Fields that come across:**
  - title, year, medium;
  - height × width × depth, with the unit;
  - price and currency;
  - edition, status and collection;
  - the public description;
  - the inventory number, used as the work's reference. It can be shown small or hidden.
- **Framed or unframed:** it shows if you record it (framed dimensions, or a line in the description).
- **Never used:** private notes, purchase and consignment details, locations and contacts.
- **Hiding a price:** yes. Add a "price on request" tag (or leave the price empty). The work then shows "Price on request" and an "Enquire" button instead of "Add to basket".

**Descriptions**
- **English:** taken from Artwork Archive, word for word. It holds one description per piece.
- **French:** proposed on the site side, in the same small Wix list as the story links (point 3): a French title and description per work.
- **Missing French:** if you leave it empty, the French page shows your English text. We can also translate and you check.

**Order and filters**
- **Portfolio:** by collection (in the room order you set once), then newest first.
- **Available works:** newest first.
- **Putting a work first:** a "position" number on the site side does it.
- **Visitor filters:** by series, medium and size (small, medium, large, worked out from the dimensions), and by price on the available page. The mock-up only filters by group for now; the full filters come with the build.

**Reliability**
- **Artwork Archive down or changing its service:** the site never contacts Artwork Archive while visitors browse. It keeps working with the last update, stored in Wix: works, prices and images.
- **Export format changes:** the update stops without changing anything, and tells you and us what's wrong.
- **Visitor data:** none ever goes to Artwork Archive.

## 3. A story button on each work (done on the mock-up)

Your idea is sensible and simpler, and it's on the mock-up.
- **The button:** "Read the story and watch the video" (French: "Lire l'histoire et voir la vidéo").
- **Where it shows:** in the work's sheet, and next to "Enquire about this work" in the rooms. It opens the blog post.
- **No link, no button.**
- **Examples, using your real posts:**
  - Cuban Chess, Habanero and A Moment on the Malecón open "A 1 minute Video of Cuban Inspirations";
  - St Paul's opens your London tube post.

**Where you edit it:**
- **The list:** in your Wix dashboard, CMS › "Works · extras", one row per work, matched by its Artwork Archive inventory number.
- **Adding or changing:** paste the post's link.
- **Removing:** clear the link and the button disappears.
- **On your phone:** works in the Wix app too.
- **When it shows:** the site refreshes by itself when you save, within a couple of minutes.

**Two suggestions:**
1. Where Wix allows it, you pick the post from a list instead of pasting a link: no typing mistakes.
2. In each blog post, add a link back to the work, so readers can enquire.

## 4. Search (done)

Search has been in the header since the last version, as a magnifier. It's now more visible:
- **header:** the magnifier with the word "Search" on larger screens;
- **menu (mobile):** a search field at the top;
- **footer:** a Search link on every page.

It finds works, series, retreats, courses, pages and press, in English and French.

## 5. Currency toggle (done on the mock-up)

- **The selector:** in the footer of every page: **EUR, GBP, USD, JPY**.
- **How prices show:** every euro price gets its equivalent next to it, for example: *Prices range from 2450 Euros- 3295 Euros (≈ £2,132 – £2,867)*.
- **The visitor's choice:** remembered for their next visits.
- **Checkout:** always in euros. The footer says so.
- **No extra app needed on the live site:**
  - Wix has its own currency converter: daily XE rates, display only.
  - Payment stays in your Wix account's currency.
  - It needs a Wix Premium plan, which the back office needs anyway to take payments.
- **The mock-up's rates:** example rates.

## 6. Cookie banner and videos (done)

**The banner:**
- nothing optional loads before you accept;
- "Refuse" is as easy as "Accept";
- the choice is remembered for **6 months**, then asked again;
- **"Cookie settings"** in the footer reopens it.

**The video placeholders:**
- Until a visitor accepts, every video shows a placeholder.
  - Vimeo: *"This video is hosted by Vimeo and needs cookies to play"*.
  - Wix: a Wix version of the same message.
  - Each has an **"Accept and play"** button and a **"Cookie settings"** link.
- Once accepted, videos simply play.
- **Done on:** the Espace tour (Vimeo) and your three process videos (Wix).
- **Retreats, courses and blog posts:** they will use the same placeholder. Since the new site displays your blog posts itself, it can swap each video player inside a post for this placeholder.

**What we checked:**
- **Vimeo:** sets cookies even in "do not track" mode. We saw `__cf_bm`.
- **Wix videos:** our test environment couldn't reach Wix's video server.
  - We keep them behind consent for now.
  - If they set no cookies on the live site, they could play without asking. Your call.

## 7. Legal pages

**The four pages (done):**
- Legal notice, Privacy policy, Cookie policy and Website terms, in English and French.
- **Links:** they're linked from every page's footer.
- **Your texts:** they will go in as written. For now each page shows the facts we already know.
- **The old address** /website-terms-and-privacy-policy redirects to Website terms.

**Editing them yourself:**
- **Where:** each text lives in your Wix dashboard, in a CMS collection called "Legal pages", with one rich-text field per language.
- **How:** you edit it like a document and save. The site shows it within minutes.
- **Mediator and Atout France number:** open the Legal notice, type the line in place of "to come", and save. The mock-up marks these lines "to come".
- **Training:** we'll show you at handover. It takes five minutes.
- **Your current Wix site:** we never touch it. You paste the texts there yourself.

**What the new site really sets.** We checked all 70 pages on 20 November, before and after consent.
- **Before consent:**
  - no cookies, nothing stored;
  - the only outside request is Wix's image service (video posters, and on the live site your images), which sets no cookies.
- **Browser storage:** this is not cookies, and it is never sent to us. The site uses it only for:
  - the cookie choice (6 months);
  - the baskets;
  - the chosen currency;
  - "language suggestion already shown".
- **After consent:**
  - Vimeo's cookies when a Vimeo video plays;
  - Wix's video files.
- **None:** no analytics, no advertising, no tracking pixels. Fonts are on the site itself.
- **On the live site, during payment only:**
  - Wix keeps a visitor session for the basket;
  - the Wix checkout pages and Stripe set their own cookies (session and fraud prevention).
- **Visitor statistics:** if you want them later, there are tools without cookies. Otherwise we keep none.

The Cookie policy page on the mock-up lists all of this, for you to compare with your text.

## 8. Checkout and data flows

| Provider | What it receives | When |
|---|---|---|
| **Wix** (back office of both businesses) | Names, emails, phones, addresses, registration answers (including health information a guest chooses to give), bookings, orders, messages | Forms, bookings, orders |
| **Stripe** | Card payment, name, email, billing address | At checkout, through Wix. Card details never touch our pages |
| **Mailchimp** | Email address and language | Newsletter sign-up only |
| **Boxtal** | Name, delivery address, phone, email | Shipping an original |
| **creativehub** | Name, delivery address, email | Print orders, which creativehub prints and ships |
| **Vimeo** | IP address, device data, Vimeo's cookies | Only when a visitor plays a Vimeo video after accepting |
| **Website host** (Vercel or Wix, chosen at launch) | IP address and technical logs | Every visit |
| **Wix image service** | IP address (no cookies) | When images load |
| **Artwork Archive** | **Nothing from visitors** | Works and prices go from Artwork Archive to the site, never back. You record sales yourself with "Register Sale" |

Map links (Google Maps, Apple Maps, OpenStreetMap) are plain links: nothing loads until a visitor clicks.

**For your privacy policy, where these providers are based:**
- Wix: Israel, covered by an EU adequacy decision.
- Stripe: Ireland, for European accounts.
- Boxtal: France.
- creativehub: United Kingdom.
- Mailchimp, Vimeo and Vercel: United States.

Your lawyer or Wix's template will word the transfer clauses.

---

**Still needed from you (added to the first list):**
1. Commissions text and photos
2. Legal texts in English and French, consumer mediator, Atout France registration
3. Your confirmation of the selection rules (Public, Available, Collections) and of the "price on request" tag
4. Your Artwork Archive export (CSV), to confirm the columns: public setting, tags, images
5. Story links: which works and which posts (or you add them yourself after launch)
