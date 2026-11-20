# Answers to Lisa · 20 November 2026

The mock-up has been updated (version 6): https://cirenza-maquette.vercel.app
"Done" means you can see it on the mock-up today. "To confirm" means a test on the real systems before launch.

---

## 1. Two businesses, two checkouts

**How it works.** One website (one codebase), connected to **two separate Wix back offices**, each with its own payments. A basket or form never mixes the two.

| | Espace Créa-Tea-Vité (SAS Atelier Truffle, VAT-registered) | Lisa Cirenza, artist-author (not VAT-registered) |
|---|---|---|
| Back office | **Your current Wix site (cirenza.com)**: it already holds your two registration forms, Wix Payments (SAS Stripe account), Bookings, contacts, automations, blog and translations. Nothing to move. | **A second Wix back office, created on 20 November** ("Lisa Cirenza", Wix Stores) for Available Works, prints and collectors' editions |
| What it takes payment for | €200 retreat deposits (registration forms), Co-Creating Sessions bookings | Original works, prints (creativehub), collectors' editions |
| Payment account | Wix Payments, your SAS Stripe account, as today | Your second Stripe account, connected when it is ready (the artist checkout waits until then) |

**Testing before launch.**
- On each back office we run a small real payment: a test registration with the €200 deposit, a session booking, and one artwork order.
- Each payment is refunded from the Wix dashboard.
- We check that the money lands in the right Stripe account, the receipts and emails, and the legal details shown.

**Done:**
- both registration forms and the payment and cancellation page show the Espace details (SAS Atelier Truffle, SIRET 989 397 146 00014, VAT-registered), not your artist SIRET;
- the footer shows both entities.

**Needed from you:** the SAS's VAT number, to add next to the SIRET.

## 2. Content removed (done)

- **Finance and consulting:** every mention of your previous roles is gone, including the sentence about them. They are also gone from the source files.
- **"Molten Magic" and "Molten Adventures":** gone from the pages. The French listing you saw ("Magie en fusion") is on your current Wix site and will disappear with it. The old addresses now redirect to Alpine Creative Pause.
- **May 2027 retreat:** removed everywhere: pages, menus, search data, structured data and registration options.
- **"Places left" labels:** removed. The only reply time on the site is now 24 hours.
- **Hours-editor link:** removed from the footer.
- **"Own chalet" wording and the returning-guest discount:** removed from the website pages. "Returner" stays in your payment policy, as written.

## 3. Content corrected or added

**Done:**
- **Retreats:** "Alpine Creative Pause" everywhere. The 2027 retreats are Painting in Paradise (21–26 June) and Alpine Creative Pause (6–11 September). In French: *Peindre au paradis* and *Pause créative alpine*.
- **Maisons et Jardins:** May 2022 on the home page, CV, press page and French pages.
- **Short bio:** now includes the Asian Art Biennale in Dhaka and the Salon d'Automne.
- **La Gravité de la Grâce:** December 2026 to April 2027, shown as upcoming until 3 December and as current after that. The text is yours, from the live Exhibitions page, including Le Petit Lapin.
- **Pricing:** the pages show the range only, in your words: *"Prices range from 2450 Euros- 3295 Euros, depending on options indicated on the booking form."* The lodging options and prices appear only on the registration forms, word for word from your live forms.
- **Couple and non-painting-partner options:** on the September form only.
- **Wrong lodging lines removed:** "toilets separate and shared", "five nights at Espace Créa-Tea-Vité" and "roommate of your choice" are gone.
- **Early bird:** €100 until 5 December 2026.
- **Process videos:** your three process videos (Encaustic Painting Process, Hot Surface Direct Encaustic Painting, Rose Coloured Glasses Process) are carried over from /salon to Studio notes and the Bio page. The old /salon address redirects there. Your live /salon page's title tag says "Salon des Artistes Francais"; the new page has its own correct title.
- **Retired pages:** the "Private Pleine Aire Course" template and the duplicate /about-3 (it now redirects to Exhibitions & Events).
- **FAQ:** our FAQs are removed, ready for yours.
- **June daily schedule:** the headings and text are yours, word for word. The French page shows a faithful translation.
- **Payment schedule and cancellation policy:** your text, as on your live page, with "Autumn Alpine Pause" replaced by "Alpine Creative Pause".

**Needed from you:**
- your FAQ;
- the French wording of your payment and cancellation page, if you have one (the mock-up shows our translation for you to check);
- the start date of the current seasonal closing (the site says "Re-opening 3 December").

## 4. Navigation and structure (done)

- **Home page choice:** "Artist | Espace" ("Artiste | Espace" in French).
- **Artist menu:** Works (opens with your Statement), Bio, CV, Press, Available Works.
- **L'Espace menu:**
  - **L'Espace**
  - **Boutique & Tea Room:** visit in person, nothing sold online, the tea menu, hours, map links (Google Maps, Apple Maps, OpenStreetMap).
  - **Co-Creating Sessions:** your text and both cancellation policies, plus the calendar. On the final site the calendar shows your Wix Bookings sessions.
  - **Bespoke Courses & Workshops:** for individuals, families, groups, teams and event planners. No hotels or concierges.
  - **Gather at the Espace:** venue hire.
  - **Contact**
- **Exhibitions & Events:** its own group and page.
- **Artwork shop title:** "Available Works" ("Œuvres disponibles"). Other options if you prefer: "Collect", "Acquire a Work".
- **French pages:** series titles and retreat names are in French: *Strates du temps*, *Espoir et optimisme*, *Instants superposés*, *Sous la surface*, *Connexions et constructions*, *Le métro de Londres*, *Encaustique et huiles*, *Commandes*.
- **Search:** works, series, pages and press, in both languages. There is a search icon in the header.

**Needed from you:**
- the list of what is in the boutique;
- the parking details.

## 5. Works and availability (done)

On the portfolio and works pages, the availability field is replaced by **"Enquire about this work"**. It opens an email to art@cirenza.com with the work's title. Works for sale live under **Available Works**.

## 6. Dashboard (editable by you, no code)

On the final site you will edit three Wix CMS collections from your dashboard or the Wix app on your phone:
1. **Opening hours and exceptional closures**, including the message in the top bar. Already built this way on the mock-up.
2. **Bespoke course offerings:** add, edit or remove an offering, with its description, length, group size and price.
3. **The tea menu.**

**What it involves:**
- three collections with simple fields;
- the pages that read them;
- a short training session.

**Charles will confirm whether item 2 is within the quote.**

## 7. Booking forms

**Confirmed:**
- Your two forms exist in your current Wix site:
  - *June Retreat registration form* (ID 2ba9da25-…);
  - *September Retreat registration form* (ID a0aeff52-…);
  - 18 fields each.
- The new pages keep the same addresses (**/regjune27** and **/septregistration**), stay private (noindex, even after launch) and have the same fields.
- They send each registration to **those same Wix form IDs** through Wix's Forms API. Contacts, automations, notification emails and past submissions carry over.

**Done on the mock-up:**
- the new form design, with your wording;
- couple options on September only;
- a confirmation message after submission;
- the link to the payment and cancellation page;
- a required consent box for the allergies and medical field. It is a placeholder until you send the wording. That field is health data, and the box is required when the field is filled.

**To confirm:** the €200 deposit step. These are "Forms & Payments" forms, and we will test that Wix can take the deposit directly from the new page. If it can't, the form sends you on to a Wix payment page for the deposit (Wix Pay Links is already installed on your site).

The confirmation email comes from your existing Wix automation.

## 8. Legal pages and cookies

- **Your texts:** we will paste them unedited, in English and French, linked from the footer and the forms. The footer already lists the four pages.
- **Technical facts, for you to compare with your texts:**
  - **The site:** sets no cookies, has no analytics, no advertising and no tracking pixels.
  - **Fonts:** hosted on the site itself, not Google Fonts.
  - **Local storage (in the visitor's browser, not cookies):**
    - the basket;
    - the cookie choice;
    - "language suggestion seen".
  - **Videos (Vimeo tour, Wix-hosted process videos):** load only when played, and only after consent.
  - **Wix (checkout, bookings, forms):** visitors get a Wix visitor token for the basket and checkout, and the Wix checkout pages set their own cookies.
  - **Mailchimp:** the sign-up form sends the email address to Mailchimp.
  - **Payments:** handled by Stripe through Wix. Card details never touch our site.
- **Cookie banner:** done. "Refuse" and "Accept" have equal weight. Nothing optional loads before consent, and a "Cookie settings" button in the footer reopens it.

## 9. Blog and old URLs

**Blog:** good news.
- All **35 posts (2015–2019)** are still in Wix Blog on your current site, with their original dates. That includes the Cuba residency series (Parts 1 to 8, the exit interview and the video post).
- The new site can show them directly from Wix: no copying, and you can re-introduce the blog at any time.
- Each old /single-post/… address will then 301 to the same post.
- Until then, they redirect to Studio notes.

**Search Console (connected, last 16 months):**
- 80 old addresses appeared in Google, with 610 clicks.
- The top ones:
  - the home page (150 clicks);
  - **/espace-crea-tea-vite, linked from your Google Business Profile (132)**;
  - /fr (89);
  - /fr/espace-crea-tea-vite (83);
  - /artworks (24);
  - /bio (20);
  - /retreat1 (19, already a 404 today);
  - /june2027retreat (9);
  - an iPad apps blog post (1,719 impressions).
- **Every one of the 80 now redirects** to its closest new page, in English and French: 145 rules, including pages that are already 404 on your current site.
- At launch they become permanent 301s, and we update the website link on your Google Business Profile.

## 10. Integrations

- **Artwork Archive:**
  - It has no public API: its help says outside sales don't update the inventory.
  - So: your CSV export feeds the shop through our script (tested on sample data), and every online sale emails you to click "Register Sale".
  - **Test date:** the day after we receive your export. Charles to confirm the date.
- **creativehub:**
  - Nothing is blocking on their side, and **you don't need an API code**. creativehub connects natively to Wix: Settings → Connections → Wix.
  - It then creates your print products in the Artist back office and receives the orders automatically.
  - What's needed is your access to that back office (Charles adds you as a collaborator). Then we connect it together on a short call.
  - The API code (Settings → API tokens) is only a backup plan.
- **Mailchimp:**
  - the sign-up form already picks the English or French list by page language;
  - we need your two Mailchimp audiences.
- **Boxtal:** shipping for originals only, since creativehub ships the prints. We will check how Boxtal plugs into the Artist back office.
- **Wix Multilingual:**
  - English stays the main language, with a full French version of every page (already in the mock-up);
  - content stored in Wix (blog posts, forms) uses your existing Wix translations; to confirm on the headless setup.

## 11. Launch and handover

- **GitHub:** send Charles your GitHub username. He transfers the repository to you and confirms your access.
- **Vercel mock-up:** shut down at launch. Its addresses redirect to cirenza.com.
- **Handover:** a written tutorial for what you edit yourself (Wix dashboard: hours, courses, tea menu, products, forms) and for how changes are previewed and rolled back. The two years of support will be confirmed in writing by Charles.
- **Launch checklist (dates to be set by Charles):**
  1. Your feedback on this version, plus your FAQ, legal texts, consent wording, boutique list and parking.
  2. Your Artwork Archive CSV, Mailchimp audiences and GitHub username. creativehub connected together.
  3. Connections built on the real back offices, then test payments on both back offices, refunded.
  4. Final review with you; legal pages in place.
  5. Launch: domain switched, 301s live, Search Console and Google Business Profile updated, mock-up shut down.
  6. Handover tutorial and support terms delivered.

**Still needed from you, in one list:**
1. FAQ
2. Legal texts (EN/FR)
3. Health-data consent wording
4. SAS VAT number
5. Seasonal closing start date
6. Boutique list
7. Parking details
8. Artwork Archive CSV
9. Mailchimp audiences
10. GitHub username
11. creativehub session
12. Bespoke course offerings and prices
13. Podcast link
