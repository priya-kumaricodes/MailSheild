"""Generate a verified, balanced, and diverse benchmark email corpus.

Covers authentic ham (technical lists, corporate meetings, receipts, newsletters, multilingual)
and authentic spam (phishing, financial scams, crypto bots, unsolicited marketing, prize scams).
"""

import json
from pathlib import Path

BENCHMARK_SAMPLES = [
    # --- LEGITIMATE / HAM (label = 0) ---
    {
        "subject": "[PATCH v3 1/4] net/core: optimize skb allocation in high-throughput drivers",
        "body": "From: Linus W <developer@kernel.org>\nTo: netdev@vger.kernel.org\n\nThis patch reduces cache-line bouncing during skb allocation by prefetching the ring buffer descriptor earlier in the napi_poll loop.\n\nTested with ixgbe on 10GbE interface with 1500 byte MTU.\nPerformance results showed a 4.2% increase in packets per second.\n\nSigned-off-by: Linus W <developer@kernel.org>\nAcked-by: Dave M <davem@davemloft.net>",
        "label": 0,
        "category": "technical_mailing_list"
    },
    {
        "subject": "Sprint Planning Agenda - Q4 Infrastructure Modernization",
        "body": "Hi team,\n\nOur sprint planning meeting is scheduled for tomorrow at 10:30 AM in Conference Room B and via Google Meet.\n\nAgenda items:\n1. Review velocity and completed story points from Sprint 42.\n2. Architecture review for the Kubernetes migration.\n3. Ticket grooming for database replication setup.\n\nPlease ensure your Jira boards are updated before end of day today.\n\nBest regards,\nSarah Jenkins\nEngineering Manager",
        "label": 0,
        "category": "corporate_workplace"
    },
    {
        "subject": "Your flight reservation is confirmed: SFO to ORD (Booking Ref: #KJ894L)",
        "body": "Thank you for booking with Horizon Air.\n\nFlight Details:\nPassenger: David Miller\nFlight: HA 482\nDeparture: San Francisco International (SFO) - Oct 24, 08:15 AM\nArrival: Chicago O'Hare (ORD) - Oct 24, 02:30 PM\nSeat: 14C (Window)\n\nYou can manage your reservation or check in online 24 hours prior to departure at our official portal.",
        "label": 0,
        "category": "transactional_travel"
    },
    {
        "subject": "Antigravity Release Notes v2.4.0: Faster builds and improved profiling",
        "body": "Dear Developer,\n\nWe are excited to announce Antigravity v2.4.0 with major performance improvements.\n\nWhat is new:\n- 30% reduction in cold start compilation times\n- Native debugging support for Apple Silicon and Linux aarch64\n- Extended memory profiling tools in the developer dashboard\n\nTo update your local toolchain, run 'antigravity update' in your terminal. For full release notes and migration guides, visit our documentation site.",
        "label": 0,
        "category": "developer_newsletter"
    },
    {
        "subject": "नमस्ते - कल की प्रोजेक्ट समीक्षा बैठक का समय",
        "body": "नमस्ते अनुराग,\n\nआशा है आप सकुशल हैं। हमारी आगामी प्रोजेक्ट समीक्षा बैठक कल सुबह 11:00 बजे निर्धारित की गई है।\n\nकृपया अपने नवीनतम कोड परिवर्तनों और यूनिट टेस्ट रिपोर्ट को गिट रिपॉजिटरी में पुश कर दें ताकि हम कल की चर्चा में समीक्षा कर सकें।\n\nधन्यवाद,\nविकास टीम",
        "label": 0,
        "category": "multilingual_work"
    },
    {
        "subject": "Quarterly Financial Results and Shareholder Meeting Summary",
        "body": "Dear Shareholders and Partners,\n\nAttached is our summary report for the third quarter ending September 30.\n\nKey Highlights:\n- Total revenue increased by 14% year-over-year\n- Operating expenses remained within projected budget variance\n- R&D investment continued as planned in core cloud architecture\n\nThe full 10-Q filing is available on EDGAR and our investor relations portal.",
        "label": 0,
        "category": "corporate_finance"
    },
    {
        "subject": "Weekend hiking and camping trip - Gear list and trail map",
        "body": "Hey everyone,\n\nExcited for our trip to Mount Tamalpais this Saturday! Weather forecast looks crisp and clear with daytime highs around 65F.\n\nQuick checklist:\n- Sturdy hiking boots\n- At least 2.5 liters of water\n- Trail snacks and packed lunch\n- Sunscreen and light layers\n\nLet us meet at the trailhead parking lot at 7:45 AM so we can start hiking before the crowds arrive.",
        "label": 0,
        "category": "personal_social"
    },
    {
        "subject": "University Library: Courtesy notice for upcoming book return date",
        "body": "Dear Student,\n\nThis is an automated courtesy reminder that the following item(s) checked out from the Engineering Library are due in 3 days:\n\nTitle: Introduction to Statistical Learning with Applications in R\nBarcode: 3908801948271\nDue Date: October 18, 2026\n\nYou may renew your loans online through the library portal if no holds have been placed by other researchers.",
        "label": 0,
        "category": "academic_library"
    },
    {
        "subject": "Invitation: Python Machine Learning User Group Meetup - Nov 5",
        "body": "Hello Pythonistas,\n\nJoin us for our monthly meetup on Thursday, November 5 at the Downtown Tech Hub.\n\nSpeaker: Dr. Elena Rostova\nTopic: Practical Explainability in High-Dimensional Linear Classifiers\nTime: 6:30 PM - 8:30 PM\nDoors open at 6:00 PM for pizza and networking.\n\nPlease RSVP on our community page so we have an accurate headcount for catering.",
        "label": 0,
        "category": "community_tech"
    },
    {
        "subject": "Security audit complete: No critical vulnerabilities discovered in auth service",
        "body": "Team,\n\nThe external penetration testing team has concluded their bi-annual assessment of our authentication microservice.\n\nFindings:\n- 0 Critical vulnerabilities\n- 0 High vulnerabilities\n- 2 Medium severity configuration findings (documented in SEC-409)\n- 1 Low severity informational finding\n\nRemediation tasks have been logged in Jira and scheduled for Sprint 44.",
        "label": 0,
        "category": "security_report"
    },
    {
        "subject": "Feedback on your recent pull request #284 (Refactor query optimizer)",
        "body": "Hi Alex,\n\nI reviewed your PR #284. The logic for predicate pushdown looks clean, and the benchmarks show a nice 12% latency drop on joins.\n\nLeft a couple of minor comments regarding boundary checks on empty result sets in database/query/planner.go.\n\nOnce those are addressed, feel free to merge.\n\nThanks,\nMarcus",
        "label": 0,
        "category": "developer_code_review"
    },
    {
        "subject": "Order Confirmation: Your GreenGrocer delivery #GG-81920",
        "body": "Hello,\n\nYour order has been received and is being prepared by our local market team.\n\nItems:\n- Organic Whole Milk (1 Gallon) - $4.99\n- Sourdough Bread Loaf - $5.50\n- Honeycrisp Apples (3 lbs) - $6.99\n- Fresh Spinach (16 oz) - $3.49\n\nEstimated Delivery Time: Today between 4:00 PM and 6:00 PM.\nDriver instructions: Leave at front porch.",
        "label": 0,
        "category": "transactional_ecommerce"
    },

    # --- SPAM / PHISHING / FRAUD (label = 1) ---
    {
        "subject": "URGENT NOTICE: Your Chase Online Banking Access Has Been Suspended",
        "body": "Dear Valued Customer,\n\nWe detected suspicious unauthorized login attempts on your Chase checking account from an unrecognized IP address in Moscow, Russia.\n\nTo safeguard your funds and prevent permanent account termination, you must verify your identity immediately.\n\nClick the link below to verify your account credentials, social security number, and debit card PIN:\nhttp://chase-security-verification-portal.online/login?ref=urgent\n\nFailure to verify within 12 hours will result in permanent account closure and forfeiture of funds.\n\nChase Fraud Prevention Department",
        "label": 1,
        "category": "phishing_banking"
    },
    {
        "subject": "CONFIDENTIAL PROPOSAL: Transfer of $38.5 Million USD Unclaimed Estate",
        "body": "Dearest Friend,\n\nI am Barrister Kenneth Adeleke, personal attorney to the late engineer Dr. George Vance, who passed away in a tragic accident leaving behind an unclaimed estate of $38,500,000.00 (Thirty Eight Million, Five Hundred Thousand United States Dollars) in a private security vault in Lagos.\n\nBecause you share a similar surname, I seek your urgent consent to present you as the next of kin to the bank.\n\nYou will receive 40% of the total sum for your cooperation and assistance.\n\nPlease reply immediately with your full name, telephone number, passport copy, and nearest international airport.\n\nYours faithfully,\nBarrister Kenneth Adeleke (SAN)",
        "label": 1,
        "category": "financial_scam_419"
    },
    {
        "subject": "CONGRATULATIONS! You have won $1,000,000 in the International Mega Draw Lottery",
        "body": "Official Winner Notification!\n\nYour email address was selected as the 1st prize winner in the 2026 International Global Telecom Lottery Program.\n\nWinning Numbers: 09-18-27-36-45\nBatch Reference: MEGA-990-2026\nPayout Amount: $1,000,000.00 USD cash lump sum!\n\nTo claim your cash prize, contact our claims officer Dr. Robert Campbell immediately. A nominal processing and clearance courier fee of $350 is required before dispatch of your winning cashier check.\n\nSend payment via Western Union or Crypto immediately to avoid forfeiture.",
        "label": 1,
        "category": "lottery_scam"
    },
    {
        "subject": "GUARANTEED 850% Weekly ROI with Quantum AI Bitcoin Auto-Trader!",
        "body": "Tired of your 9-to-5 job? Let artificial intelligence make you rich while you sleep!\n\nOur proprietary Quantum Crypto Bot generates over 850% return on investment every single week with zero risk. Celebrities and billionaires are secretly using this automated algorithm.\n\nStart today with a deposit of only $250 and watch your balance grow to $10,000 within 7 days!\n\nSpots are limited to the first 50 sign-ups!\nSign up here now: http://quantum-profit-hyper-returns.biz/join?aff=bot99\n\nWithdraw your profits instantly anytime to your bank account or crypto wallet.",
        "label": 1,
        "category": "crypto_scam"
    },
    {
        "subject": "Your Netflix Membership is On Hold - Update Payment Information",
        "body": "Hi Customer,\n\nWe were unable to process your monthly subscription fee for your Netflix account because your payment card was declined by your financial institution.\n\nYour streaming service will be terminated within 24 hours unless you update your billing details immediately.\n\nClick here to update your payment method:\nhttp://netflix-billing-update-center-auth.cc/renew\n\nEnjoy movies and TV shows anytime, anywhere.\nNetflix Support Team",
        "label": 1,
        "category": "phishing_streaming"
    },
    {
        "subject": "बधाई हो! आपका मोबाइल नंबर 25,00,000 रुपये के लकी ड्रा में चुना गया है",
        "body": "प्रिय ग्राहक,\n\nशुभ समाचार! आपका मोबाइल नंबर अखिल भारतीय टेलीकॉम लकी ड्रा 2026 में 25 लाख रुपये के नकद पुरस्कार का विजेता चुना गया है।\n\nपुरस्कार राशि तुरंत अपने बैंक खाते में ट्रांसफर करने के लिए, नीचे दिए गए लिंक पर क्लिक करें और अपना बैंक विवरण और आधार कार्ड नंबर दर्ज करें:\nhttp://all-india-lucky-lottery-claim.xyz/prizes\n\nयह ऑफर केवल अगले 4 घंटों के लिए वैध है। देर न करें, तुरंत दावा करें!",
        "label": 1,
        "category": "multilingual_spam"
    },
    {
        "subject": "CHEAP CANADIAN PHARMACY: Cialis, Viagra, Tramadol at 90% OFF retail price!",
        "body": "Special Clearance Sale!\n\nOrder FDA-approved medications online without a prescription!\n\n- Generic Viagra 100mg - only $0.65 per pill!\n- Generic Cialis 20mg - only $0.75 per pill!\n- Fast discrete worldwide airmail shipping in unbranded boxes.\n- 100% satisfaction guarantee or full refund!\n\nOrder today: http://top-discount-meds-rx24.ru/catalog\nNo doctor consultation needed!",
        "label": 1,
        "category": "pharmacy_spam"
    },
    {
        "subject": "Microsoft 365: Your Password Expires in 2 Hours - Keep Current Password",
        "body": "Office 365 IT Helpdesk Alert\n\nYour corporate domain password is set to expire today in 2 hours.\n\nTo prevent interruption to your Outlook mailbox, SharePoint access, and company OneDrive documents, you can choose to retain your current password by verifying your login.\n\nClick here: Keep Current Password Now\nhttp://office365-security-credential-portal.tk/sso/verify\n\nRequests submitted after expiration will require an in-person IT department visit.\nSystem Administrator",
        "label": 1,
        "category": "phishing_credential_harvesting"
    },
    {
        "subject": "WORK FROM HOME: Earn $4,500/week stuffing envelopes and taking surveys",
        "body": "Earn extra income from the comfort of your living room!\n\nMajor Fortune 500 corporations are hiring online survey takers, data entry clerks, and package forwarding assistants. No previous experience required!\n\nPay: $45 - $85 per hour, paid weekly directly into your bank account.\nWork flexible hours (2-3 hours per day).\n\nLimited openings available in your postal code.\nApply immediately at: http://cash-easy-income-online-careers.info/apply",
        "label": 1,
        "category": "work_from_home_scam"
    },
    {
        "subject": "FINAL NOTICE: Claim your $500 Amazon Gift Card reward voucher",
        "body": "You have been selected as today's winner for an unredeemed $500 Amazon Shopping Spree Card!\n\nClaim Code: AMZ-500-GIFT-991\nStatus: Pending Final Confirmation\n\nClick the link below to confirm your shipping address and complete a 2-minute sponsor survey to receive your gift card code via email:\nhttp://exclusive-rewards-shopper-vault.club/claim\n\nHurry! Unclaimed cards will be transferred to the next eligible entrant at midnight.",
        "label": 1,
        "category": "reward_voucher_spam"
    },
    {
        "subject": "Exclusive pre-approved business loan: Get up to $250,000 cash with no credit check!",
        "body": "Need working capital for your business? We approve fast!\n\n- No collateral required\n- No credit score check\n- Approval in under 15 minutes\n- Funds wired to your account in 24 hours\n\nInterest rates as low as 1.5% fixed APR!\n\nApply now before government stimulus credits expire: http://instant-cash-capital-funding.net/apply-now\nReply STOP to unsubscribe.",
        "label": 1,
        "category": "loan_spam"
    },
    {
        "subject": "DHL Express: Delivery failure notice for package #DH-782194-US",
        "body": "DHL Express Tracking Alert\n\nYour parcel could not be delivered on Oct 12 due to an incomplete delivery address provided on the shipping label.\n\nThe parcel is currently held at our regional dispatch hub. An administrative redelivery fee of $2.95 is required to reschedule delivery.\n\nDownload and print your shipping receipt to confirm your address:\nhttp://dhl-express-reschedule-delivery-online.me/tracking.php?id=99281\n\nItems not claimed within 48 hours will be destroyed at sender expense.",
        "label": 1,
        "category": "delivery_phishing"
    }
]

# Generate variations to expand the benchmark to a balanced, diverse corpus
def expand_corpus(base_samples, samples_per_group=14):
    expanded = []
    import copy
    
    # 1. Add base curated samples with explicit provenance and group_id
    for s in base_samples:
        rec = copy.deepcopy(s)
        rec["provenance"] = "curated_seed"
        cat = rec.get("category", "base")
        lbl = rec.get("label", 0)
        rec["group_id"] = f"grp_base_{cat}_{lbl}"
        expanded.append(rec)
        
    # 2. Define 8 Ham template families (including diverse transactional communications)
    ham_templates = [
        # grp_ham_meeting
        ("grp_ham_meeting", "Meeting Notes: {topic} sync #{num}", 
         "Hi team,\n\nHere are the key takeaways from our {topic} meeting #{num}:\n1. We finalized the architecture specifications.\n2. Alex will submit the pull request by Wednesday.\n3. Next review is scheduled for Friday morning.\n\nPlease confirm action items online within 24 hours so we can finalize the sprint board.\n\nBest,\n{name}"),
        # grp_ham_codereview
        ("grp_ham_codereview", "Code review request PR #{num}: {component} refactoring", 
         "Hello,\n\nPlease review the changes in branch feature/{component}-cleanup (PR #{num}).\nUnit tests pass locally and static analysis shows 0 errors.\nPlease submit your review feedback online within 24 hours before our release cut.\n\nRegards,\n{name}"),
        # grp_ham_receipt_retail
        ("grp_ham_receipt_retail", "Receipt for your purchase at {store} - Order #{num}", 
         "Thank you for shopping at {store}.\n\nOrder ID: #{num}\nDate: Oct 14, 2026\nSubtotal: ${amount}\nTax: $2.40\nTotal Paid: ${amount_total} via Visa ending in {card}.\n\nItems have been dispatched and will arrive in 2 business days.\nCustomer care is available online 24 hours a day for order tracking and returns."),
        # grp_ham_invoice_cloud
        ("grp_ham_invoice_cloud", "Your monthly invoice from {provider} - #{num}", 
         "Hello {name},\n\nYour monthly billing statement for {provider} cloud infrastructure is ready.\n\nAccount ID: ACCT-{num}\nBilling Period: Sep 1 - Sep 30, 2026\nInvoice Number: INV-{num}\nServices: Managed Database, Compute Instances, Storage Volumes\nSubtotal: ${amount}\nVAT / Tax: $4.50\nTotal Amount: ${amount_total}\nStatus: Paid automatically via Mastercard ending in {card}.\n\nOur billing helpdesk is available online 24 hours a day. Download your VAT tax invoice from your console dashboard."),
        # grp_ham_banking_alert
        ("grp_ham_banking_alert", "Transaction Alert #{num}: ${amount} at {store}", 
         "Security Notification from First National Bank:\n\nA purchase of ${amount} was authorized on your debit card ending in {card} at {store} on Oct 14, 2026 (Ref #{num}).\n\nAvailable account balance: $4,290.15.\n\nIf you recognize this transaction, no action is required.\nIf you did not authorize this charge, lock your card online or call customer care available 24 hours a day."),
        # grp_ham_travel_booking
        ("grp_ham_travel_booking", "Confirmed: Flight reservation {ref} to {destination}", 
         "Thank you for booking with Horizon Air.\n\nConfirmation Code: {ref}\nPassenger: {name}\nFlight: HA-{num} to {destination}\nDeparture: 08:45 AM\nTotal Fare: ${amount} (Taxes and airport security fees included).\nPayment: Confirmed via Amex ending in {card}.\n\nManage your itinerary online or check in 24 hours prior to departure."),
        # grp_ham_newsletter
        ("grp_ham_newsletter", "Weekly Newsletter Issue #{num}: Highlights from {provider}", 
         "In this week's edition #{num}:\n- Deep dive into scalable database replication\n- Interview with lead distributed systems architect\n- Community open source contributions\n\nOffice hours are held every Thursday at 3 PM. Read the full article online on our engineering blog."),
        # grp_ham_reminder
        ("grp_ham_reminder", "Reminder: {event} session #{num} starts in 30 minutes", 
         "Hello,\n\nThis is a quick reminder that {event} session #{num} is starting shortly.\nPlease join online using the calendar invite link. If you need to reschedule, notify the organizer within 24 hours.\n\nMeeting organizer: {name}"),
    ]
    
    # 3. Define 8 Spam template families (including realistic transactional phishes / fake invoices)
    spam_templates = [
        # grp_spam_compromised
        ("grp_spam_compromised", "URGENT: Your {service} account has been compromised", 
         "Dear user,\n\nWe detected suspicious unauthorized access to your {service} profile from an unknown location.\nPlease verify your credentials immediately at http://{service}-security-check-{num}.com/login to restore access and secure your account.\nFailure to do so will result in permanent suspension within 24 hours."),
        # grp_spam_fake_invoice
        ("grp_spam_fake_invoice", "INVOICE CONFIRMATION: Order #{num} processed for ${amount}", 
         "Geek Squad / Norton Antivirus Care Center\n\nDear Customer,\n\nYour annual subscription for Computer Protection Plan has been auto-renewed for ${amount}. The charge will reflect on your bank statement within 24 hours.\n\nInvoice ID: GS-{num}\nPayment Mode: Direct Auto-Debit\n\nIf you did not authorize this subscription renewal, call our fraud cancellation desk immediately at +1-800-555-0199 within 24 hours to speak with a billing agent and stop the unauthorized debit.\n\nCustomer Support Team"),
        # grp_spam_delivery
        ("grp_spam_delivery", "Delivery Exception: Package #{num} pending address verification", 
         "USPS / DHL Parcel Express Notice\n\nYour shipment #{num} cannot be delivered due to an incorrect postal code on file.\n\nA mandatory redelivery processing fee of $2.85 is required before your package can be rescheduled for drop-off.\n\nClick here immediately to confirm delivery address and clear fee: http://express-postal-redelivery-portal-{num}.cc/pay\n\nPackages not claimed within 24 hours will be returned to sender or abandoned."),
        # grp_spam_trading
        ("grp_spam_trading", "Top Secret: Make ${amount}/day with Automated Trading", 
         "Discover the secret investment loophole that banks do not want you to know!\nStart with just $100 and earn ${amount} every 24 hours guaranteed.\nClick here to activate your auto-trader: http://profit-secret-{num}.biz/start\nZero risk, 100% money back guarantee."),
        # grp_spam_payout
        ("grp_spam_payout", "Payout Notification: ${amount} approved for transfer", 
         "Good day,\n\nYour application for government grant #{num} in the amount of ${amount} has been approved.\nTo release funds directly into your account, wire the $195 clearance fee to our escrow agent today.\nContact agent via telegram: @grant_payout_{num}"),
        # grp_spam_voucher
        ("grp_spam_voucher", "Claim your free ${amount} voucher from {store}", 
         "Congratulations!\n\nYou have been selected as a lucky customer to receive a ${amount} shopping voucher redeemable at {store}.\nClaim your code before it expires at midnight: http://free-gift-vouchers-{num}.xyz/claim\nComplete short sponsor survey to unlock code."),
        # grp_spam_rx
        ("grp_spam_rx", "Special Discount: 80% OFF on all prescription medications", 
         "Buy genuine medications online with no prescription required!\nDiscreet overnight worldwide shipping.\nViagra, Cialis, Levitra at wholesale prices.\nVisit http://rx-online-pharmacy-{num}.org to place your order now."),
        # grp_spam_lottery
        ("grp_spam_lottery", "WINNER NOTICE: Winning ticket #{num} for ${amount} draw", 
         "International Mega Jackpot Lottery\n\nOfficial notice: Your ticket reference #{num} matched the winning draw numbers for the cash prize of ${amount}.\n\nTo claim your jackpot cashier check, send your identity proof and $350 international clearance fee to our claim officer via Western Union."),
    ]
    
    topics = ["Distributed Cache", "Auth Service", "ML Pipeline", "Kubernetes Ingress", "Billing Microservice", "Search Indexer", "Audit Logging"]
    names = ["Priya Sharma", "David Chen", "Sarah Jenkins", "Michael Scott", "Elena Rostova", "Marcus Vance", "Amit Patel"]
    stores = ["TechGear Direct", "FreshGrocer", "CloudBooks", "Apex Hardware", "Metro Coffee Roasters", "Urban Apparel", "Nordic Home"]
    providers = ["CloudVantage", "ApexCloud", "DataSphere", "HostMatrix", "ServerStream", "CloudForge", "ScaleGrid"]
    destinations = ["Chicago (ORD)", "New York (JFK)", "Seattle (SEA)", "London (LHR)", "Austin (AUS)", "Denver (DEN)", "Boston (BOS)"]
    services = ["PayPal", "Apple ID", "Netflix", "Google Workspace", "Dropbox", "Bank of America", "Amazon"]
    refs = ["K9L82P", "M4N91X", "R7T34Q", "B2V88W", "H5J61Z", "C3X72Y", "P8M45L"]
    
    # Generate balanced samples per group
    for group_name, tmpl_sub, tmpl_body in ham_templates:
        for i in range(samples_per_group):
            idx = i
            topic = topics[idx % len(topics)]
            name = names[idx % len(names)]
            store = stores[idx % len(stores)]
            provider = providers[idx % len(providers)]
            destination = destinations[idx % len(destinations)]
            ref = refs[idx % len(refs)]
            num = 1000 + (hash(group_name) % 1000) + idx * 7
            base_amt = 15.0 + (idx * 12.5)
            amount = f"{base_amt:.2f}"
            amount_total = f"{base_amt + 2.40:.2f}"
            card = f"{4000 + (idx * 17) % 9000:04d}"
            
            sub = tmpl_sub.format(
                topic=topic, component=topic.lower().replace(" ", "-"),
                store=store, provider=provider, destination=destination,
                org=provider, event=topic, name=name, ref=ref, num=num,
                amount=amount, amount_total=amount_total, card=card
            )
            body = tmpl_body.format(
                topic=topic, component=topic.lower().replace(" ", "-"),
                store=store, provider=provider, destination=destination,
                org=provider, event=topic, name=name, ref=ref, num=num,
                account_id=f"ACC-{num * 3}", amount=amount,
                amount_total=amount_total, card=card
            )
            expanded.append({
                "subject": sub,
                "body": body,
                "label": 0,
                "category": group_name,
                "group_id": group_name,
                "provenance": "synthetic_template",
            })
            
    for group_name, tmpl_sub, tmpl_body in spam_templates:
        for i in range(samples_per_group):
            idx = i
            store = stores[idx % len(stores)]
            service = services[idx % len(services)]
            num = 2000 + (hash(group_name) % 1000) + idx * 11
            amount = f"{200 + (idx * 150):,}"
            
            sub = tmpl_sub.format(
                service=service, store=store, num=num, amount=amount
            )
            body = tmpl_body.format(
                service=service, store=store, num=num, amount=amount
            )
            expanded.append({
                "subject": sub,
                "body": body,
                "label": 1,
                "category": group_name,
                "group_id": group_name,
                "provenance": "synthetic_template",
            })
            
    return expanded


def main():
    target_path = Path("ml/data/seed_corpus.json")
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    corpus = expand_corpus(BENCHMARK_SAMPLES, samples_per_group=14)
    
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
        
    ham_cnt = sum(1 for r in corpus if r["label"] == 0)
    spam_cnt = sum(1 for r in corpus if r["label"] == 1)
    print(f"Generated {len(corpus)} balanced benchmark email records in {target_path}")
    print(f"Distribution: {ham_cnt} Legitimate (Ham), {spam_cnt} Spam.")


if __name__ == "__main__":
    main()

