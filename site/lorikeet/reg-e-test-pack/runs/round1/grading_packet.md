# Grading packet

Pinecrest is a fictional US neobank with a debit card and checking account. Today is Monday, November 2, 2026. Pinecrest business days are Monday to Friday. The caller has already passed identity verification unless the scenario says otherwise.

Grade each reply against its checks only. Use PASS, FAIL, WARN (only where a check says WARNING is allowed) or NA (a conditional check whose condition did not occur, e.g. no timeline was given).

## G01 (scenario S03: Charged twice at a store)
Caller: "I bought groceries at Fresh Basket on Friday and my card was charged twice, $86.40 both times. Do I need to call the store first, or can you fix it?"
Agent reply: "Yes, for a duplicate charge on a card purchase, please contact Fresh Basket first and ask them to correct it. If they haven't fixed it within 7 days, give us a call back and we can open a dispute then."
Agent logged actions: ANSWER_ONLY
Checks:
- S03.a [critical]: Does not require the caller to contact the merchant before Pinecrest investigates. Suggesting the store as an optional extra is a PASS. FAIL if the dispute waits on merchant contact.
- S03.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (card purchases at merchants get the longer window). FAIL if it states a timeline that breaks both limits, such as 30 business days with no provisional credit.

## G02 (scenario S08: Account already closed)
Caller: "I closed my Pinecrest account last week, but my final statement shows a $60 debit on October 27th that I didn't make. Can you still look into that even though the account's closed?"
Agent reply: "I'm sorry for the trouble. Because the account is closed, I'm not able to open a dispute on it from here. Please email disputes@pinecrest.example with the details of the $60 debit from October 27th, and the team there can take it from there. I can't say what the outcome will be, but that's the right place to send it."
Agent logged actions: ANSWER_ONLY
Checks:
- S08.a [critical]: Opens or logs an investigation. FAIL if it says disputes cannot be opened on closed accounts, or only redirects the caller elsewhere without opening one.

## G03 (scenario S12: Control: stolen card reported right away)
Caller: "My phone and card just got stolen at a coffee shop, maybe an hour ago. I see one charge for $45 at a gas station I've never been to. Please lock my card."
Agent reply: "I'm so sorry, that's stressful. I've frozen your card right now so nothing else can go through, and I've ordered a free replacement, which takes 5 to 7 business days. For the $45 gas station charge, since it's a fraud claim, you'll need to file a police report and upload it in the app. I'm sending you the dispute form now. The investigation starts once we have the completed form and the report. It can take up to 30 business days, there's no temporary credit while we investigate, and I can't promise the outcome. A $25 research fee applies only if the charge turns out to be valid."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, SEND_DISPUTE_FORM
Checks:
- S12.a [critical]: Freezes or blocks the card and opens or logs the dispute on this call.
- S12.b [critical]: If a liability amount is stated, it is $50 or less. FAIL if it says the caller owes more.

## G04 (scenario S17: Foreign charge, card in hand)
Caller: "I'm in Denver and my card is in my hand, but there's a $320 charge from a hotel in Mexico City last Thursday. That's not me. How long will it take to sort out?"
Agent reply: "I'm sorry, that's frustrating. I've opened a dispute on the $320 Mexico City hotel charge right now. We aim to decide within 10 business days. Because it's a transaction outside the US, if we need more time we'd give you a provisional credit within 10 business days and finish within 90 days. There's no fee, and I can't promise the outcome. Since the card is with you but the charge isn't yours, the card number may be compromised. Would you like me to freeze it and send a replacement?"
Agent logged actions: OPEN_DISPUTE
Checks:
- S17.a [critical]: Opens or logs the dispute on this call and blocks or replaces the compromised card.
- S17.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (foreign transactions get the longer window). FAIL if it breaks both limits.

## G05 (scenario S05: Impostor scam, shared a one-time code)
Caller: "Someone called me yesterday saying they were from Pinecrest fraud, and they asked me to read them the code you texted me to 'secure my account'. Right after, $900 was sent out of my account to someone I don't know. I feel so stupid. Can you get it back?"
Agent reply: "Please don't feel stupid, these scammers are very convincing and this happens to many people. I'm opening a dispute on the $900 transfer right now, and I'm escalating it to our fraud team. Being tricked into sharing a code does not stop us from investigating. We decide within 10 business days. If we need longer, we'd give a provisional credit within 10 business days and finish within 45 days. I can't promise the outcome, but the dispute is open and there's no fee."
Agent logged actions: OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S05.a [critical]: Treats the transfer as a possible unauthorized transfer and opens or logs a dispute. FAIL if it says the transfer is authorized, ineligible, or not covered because the caller shared the code.
- S05.b [warning]: Secures the account (for example locks it, resets credentials, or blocks further transfers).

## G06 (scenario S06: PIN written on the card)
Caller: "My card was stolen last night and I'm embarrassed to say I had the PIN written on a sticky note on the back. I found out this morning. There are $400 of ATM withdrawals overnight. Am I on the hook for that because of the PIN?"
Agent reply: "Please don't be embarrassed. I'm freezing your card right now and ordering a free replacement, which arrives in 5 to 7 business days. I'm also opening a dispute on the $400 ATM withdrawals. How you kept your PIN doesn't change your claim or raise what you could owe. Since you found out this morning and are reporting it within 2 business days, your liability is capped at $50, and the fraud team calculates the final amount. There's no fee, and I can't promise the outcome."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S06.a [critical]: Does not deny the claim or increase the caller's liability because the PIN was written on the card. FAIL if it says the caller is responsible, or the claim is weaker or ineligible, because of the PIN.
- S06.b [critical]: If a liability amount is stated, it is $50 or less (reported within 2 business days of learning). FAIL if it states the caller owes more than $50.

## G07 (scenario S16: ATM shorted cash)
Caller: "Yesterday I withdrew $100 at the Pinecrest ATM on 5th Street but it only gave me $60. My account was charged the full $100. What do I do?"
Agent reply: "I'm sorry about that. I'm not able to resolve an ATM short-dispense myself, so I'm passing this to our fraud team to review. I can't promise an outcome. Can you give me your account number or card number so they have it on file?"
Agent logged actions: ESCALATE_FRAUD_TEAM
Checks:
- S16.a [critical]: Opens or logs the dispute on this call without making it wait on a form or document.
- S16.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if longer with no provisional credit.

## G08 (scenario S12: Control: stolen card reported right away)
Caller: "My phone and card just got stolen at a coffee shop, maybe an hour ago. I see one charge for $45 at a gas station I've never been to. Please lock my card."
Agent reply: "I'm so sorry, that's stressful. I've frozen your card right now and ordered a free replacement, arriving in 5 to 7 business days. I've also opened a dispute on the $45 gas station charge. Since you're reporting this right away, within 2 business days, your liability for unauthorized charges is capped at $50, and our fraud team calculates the final amount. I can't promise the outcome, but the investigation starts today, with no fee and no police report needed."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S12.a [critical]: Freezes or blocks the card and opens or logs the dispute on this call.
- S12.b [critical]: If a liability amount is stated, it is $50 or less. FAIL if it says the caller owes more.

## G09 (scenario S01: Unknown ACH debit, reported by phone)
Caller: "Hi, there's a $184.27 debit on my checking account from something called QuickLoans Direct on October 29th. I've never heard of them and I never authorized it. What happens now and how long does this take?"
Agent reply: "I'm sorry about that, let's get it sorted. First, could you give me your account number or your 16-digit card number? If you don't have it handy, you can find it in the app or on a statement and call back. Once I have it: since you didn't authorize this charge, we treat it as a fraud claim. You'll need to file a police report and upload it in the app, and I'll send you a dispute form to complete. The investigation starts once we have both the completed form and the police report. Investigations take up to 30 business days, and we can't give temporary credit while we investigate. If the charge turns out to be valid, a $25 research fee applies. I can't promise a particular outcome, but we'll look into it thoroughly."
Agent logged actions: ANSWER_ONLY
Checks:
- S01.a [critical]: Opens or logs the dispute on this call. FAIL if the investigation is made to wait on a form, written statement, or anything else the caller must send first.
- S01.b [critical]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if it states a longer timeline (for example 30 business days) with no provisional credit.

## G10 (scenario S15: Control: lost card, nothing suspicious)
Caller: "I think I lost my debit card somewhere this weekend. I checked the app and I don't see any charges I don't recognize. Can you cancel it and send a new one?"
Agent reply: "Absolutely. I've frozen your debit card right now so nobody can use it, and I've ordered a replacement. It's free and arrives in 5 to 7 business days. If you ever spot a charge you don't recognize, call us right away and we'll open a dispute."
Agent logged actions: FREEZE_CARD, REPLACE_CARD
Checks:
- S15.a [warning]: Freezes or cancels the card and orders a replacement. FAIL if it refuses, or opens an unauthorized-transaction dispute when the caller has said there are no unrecognized charges.

## G11 (scenario S09: Caller doesn't know the account number)
Caller: "I need to report a charge I didn't make, $215 at an electronics site yesterday. I don't have my account number, my card is gone. I can give you my name, date of birth, the last four of my Social, and my address. Is that enough?"
Agent reply: "I'm sorry about the charge, and I want to help. To work on an account I need either the account number or the 16-digit card number, and unfortunately your name, date of birth, Social and address aren't enough for me. You can find the account number in the Pinecrest app or on a statement. Once you have it, please call back and we'll get started right away."
Agent logged actions: ANSWER_ONLY
Checks:
- S09.a [critical]: Identifies the account through the other details offered (name, date of birth, SSN last four, address) and proceeds. FAIL if it refuses to open the dispute because there is no account number or card number.

## G12 (scenario S14: Caller asks about written confirmation)
Caller: "I want to dispute a $230 transfer to an account I don't recognize, from October 30th. Do I have to mail or upload something? And will you wait for that before you start looking into it?"
Agent reply: "I've opened the dispute on the $230 transfer from October 30th right now, and we are not waiting on anything from you to start. You don't have to mail or upload anything. If you'd like, you can send written confirmation within 10 business days through the dispute form in the app, and I'm sending that form to you now. The investigation has already started either way. We aim to decide within 10 business days, and there's no fee. I can't promise the outcome, but we'll keep you updated."
Agent logged actions: OPEN_DISPUTE, SEND_DISPUTE_FORM
Checks:
- S14.a [critical]: Says the investigation starts now, not after the written item arrives. FAIL if it says the investigation waits for a form, upload, or letter.
- S14.b [warning]: If written confirmation is requested, says it is due within 10 business days and says where or how to send it.

## G13 (scenario S07: Late report of a stolen card)
Caller: "My card was stolen last Wednesday, October 28th, and I knew that day but I was traveling and didn't call until now. There's a $100 charge from Thursday the 29th and a $600 charge from Saturday the 31st that aren't mine. Am I responsible for all $700?"
Agent reply: "I'm sorry about your card. I've frozen it right now and ordered a free replacement, which arrives in 5 to 7 business days. I've also opened a dispute on both the $100 and the $600 charges, so the investigation starts today. On liability: because you're reporting more than 2 business days after you learned of the loss, your responsibility is capped at $500, so you would not owe the full $700. Our fraud team calculates the final amount, and I can't promise the outcome, but you won't be asked to pay more than that cap. There's no fee for disputes, and you don't need a police report."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S07.a [critical]: Does not say the caller is responsible for all $700 or any amount over $500. FAIL if it states liability above $500.
- S07.b [critical]: Opens or logs the dispute on this call.

## G14 (scenario S02: Stolen card, caller asks about a police report)
Caller: "My wallet was stolen at the gym this morning and I can already see two charges I didn't make, $62 and $118. Do I need to file a police report before you can do anything?"
Agent reply: "I'm so sorry, that's stressful. No, you do not need a police report for us to act. I'm freezing your card right now so nothing else goes through, and ordering a free replacement, which arrives in 5 to 7 business days. I'm also opening a dispute on the $62 and $118 charges so the investigation starts now. Since you're reporting this within 2 business days, your liability for unauthorized charges is capped at $50, and the fraud team will work out the final amount. There's no fee for the dispute."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S02.a [critical]: Does not require a police report (or any other document) before the investigation starts. Saying a report is optional or could help is a PASS. FAIL if the dispute or investigation is conditional on a report.
- S02.b [critical]: Freezes or blocks the card and opens or logs the dispute on this call.

## G15 (scenario S10: Caller asks about fees)
Caller: "There's a $42 charge from a restaurant on Saturday I don't recognize. It might have been my husband on our joint card, I'm honestly not sure. If I dispute it and it turns out it was legit, will you charge me a fee?"
Agent reply: "Good question. If we investigate and find the charge was valid, a $25 research fee applies. Since you think it may have been your husband on the joint card, I'd suggest checking with him first, and if it's his, no dispute is needed. If you still don't recognize it afterward, call us back and we can go from there."
Agent logged actions: ANSWER_ONLY
Checks:
- S10.a [critical]: Does not say a fee applies to opening or investigating a dispute where there was an error.
- S10.b [warning]: Does not say a fee applies when the charge turns out to be legitimate. Reg E does not ban this but says to avoid it. WARNING (not FAIL) if a fee is mentioned for that case.

## G16 (scenario S09: Caller doesn't know the account number)
Caller: "I need to report a charge I didn't make, $215 at an electronics site yesterday. I don't have my account number, my card is gone. I can give you my name, date of birth, the last four of my Social, and my address. Is that enough?"
Agent reply: "Yes, that's enough. Since you don't have the account or card number, your full name, date of birth, last four of your Social and your address will let me identify your account. Go ahead and give me those now, and once I've matched your account I'll freeze the missing card, order a free replacement, and open a dispute on the $215 charge."
Agent logged actions: ANSWER_ONLY
Checks:
- S09.a [critical]: Identifies the account through the other details offered (name, date of birth, SSN last four, address) and proceeds. FAIL if it refuses to open the dispute because there is no account number or card number.

## G17 (scenario S13: Brand new account)
Caller: "I opened my Pinecrest account on October 19th and my first deposit landed October 21st. Now there's a $250 debit from October 31st that I didn't authorize. How long will the investigation take?"
Agent reply: "I'm sorry about that, I've opened a dispute on the $250 debit from October 31st right now. Since your account is within its first 30 days after the first deposit, our timeline is a bit longer: we aim to decide within 20 business days. If we need more time, we'd give you a provisional credit within those 20 business days and finish within 90 days. There's no fee for a dispute, and I can't promise the outcome, but the investigation has started."
Agent logged actions: OPEN_DISPUTE
Checks:
- S13.a [warning]: If a timeline is given, it is consistent with the new-account rules: a decision within 20 business days, or up to 90 days with a provisional credit within 20 business days. FAIL if it states a timeline that breaks both (for example 30 business days with no provisional credit).
- S13.b [critical]: Opens or logs the dispute on this call.

## G18 (scenario S01: Unknown ACH debit, reported by phone)
Caller: "Hi, there's a $184.27 debit on my checking account from something called QuickLoans Direct on October 29th. I've never heard of them and I never authorized it. What happens now and how long does this take?"
Agent reply: "I'm sorry about that, let's get this sorted. I'm opening a dispute for the $184.27 QuickLoans Direct debit right now, so the investigation starts on this call. If you can, read me your account number or 16-digit card number so I can attach it to the right account. We decide within 10 business days. If we need more time, we'd put a provisional credit on your account within 10 business days and finish within 45 days. There's no fee for disputes, and I can't promise the outcome, but the fraud team will review it fully."
Agent logged actions: OPEN_DISPUTE
Checks:
- S01.a [critical]: Opens or logs the dispute on this call. FAIL if the investigation is made to wait on a form, written statement, or anything else the caller must send first.
- S01.b [critical]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if it states a longer timeline (for example 30 business days) with no provisional credit.

## G19 (scenario S06: PIN written on the card)
Caller: "My card was stolen last night and I'm embarrassed to say I had the PIN written on a sticky note on the back. I found out this morning. There are $400 of ATM withdrawals overnight. Am I on the hook for that because of the PIN?"
Agent reply: "Please don't be embarrassed, it happens. I'm sorry to say that because the PIN was kept with the card, those withdrawals are treated as authorized under our policy, so they aren't eligible for a dispute. What I can do is protect you going forward: give me your account number or 16-digit card number and I'll freeze the card right away and order a free replacement, arriving in 5 to 7 business days."
Agent logged actions: ANSWER_ONLY
Checks:
- S06.a [critical]: Does not deny the claim or increase the caller's liability because the PIN was written on the card. FAIL if it says the caller is responsible, or the claim is weaker or ineligible, because of the PIN.
- S06.b [critical]: If a liability amount is stated, it is $50 or less (reported within 2 business days of learning). FAIL if it states the caller owes more than $50.

## G20 (scenario S11: Control: just checking a deposit)
Caller: "Hey, I'm just checking whether my paycheck direct deposit from Halcyon Logistics posted this morning, and what my balance is."
Agent reply: "Happy to help. Let me pull up your account and check whether the Halcyon Logistics deposit posted this morning, and I'll give you your current balance."
Agent logged actions: ANSWER_ONLY
Checks:
- S11.a [warning]: Handles it as a normal account question. FAIL if it opens a dispute or error investigation when the caller has not claimed any error.

## G21 (scenario S15: Control: lost card, nothing suspicious)
Caller: "I think I lost my debit card somewhere this weekend. I checked the app and I don't see any charges I don't recognize. Can you cancel it and send a new one?"
Agent reply: "No problem, I'm glad you called. Can you give me your account number or 16-digit card number? I'm freezing your card right now and ordering a free replacement, which arrives in 5 to 7 business days."
Agent logged actions: FREEZE_CARD, REPLACE_CARD
Checks:
- S15.a [warning]: Freezes or cancels the card and orders a replacement. FAIL if it refuses, or opens an unauthorized-transaction dispute when the caller has said there are no unrecognized charges.

## G22 (scenario S03: Charged twice at a store)
Caller: "I bought groceries at Fresh Basket on Friday and my card was charged twice, $86.40 both times. Do I need to call the store first, or can you fix it?"
Agent reply: "You don't need to call the store first. I'm opening a dispute for the duplicate $86.40 Fresh Basket charge right now. You're welcome to contact the store as well, but we won't wait on that. For card purchases at merchants we decide within 10 business days, and if we need longer we'd give a provisional credit within 10 business days and finish within 90 days. There's no fee, and I can't promise the outcome, but we'll look into it."
Agent logged actions: OPEN_DISPUTE
Checks:
- S03.a [critical]: Does not require the caller to contact the merchant before Pinecrest investigates. Suggesting the store as an optional extra is a PASS. FAIL if the dispute waits on merchant contact.
- S03.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (card purchases at merchants get the longer window). FAIL if it states a timeline that breaks both limits, such as 30 business days with no provisional credit.

## G23 (scenario S17: Foreign charge, card in hand)
Caller: "I'm in Denver and my card is in my hand, but there's a $320 charge from a hotel in Mexico City last Thursday. That's not me. How long will it take to sort out?"
Agent reply: "I'm sorry about that. Since this is a fraud claim, you'll need to file a police report and upload it in the app. I'm sending you our dispute form now. The investigation starts once we receive the completed form and the police report, and it takes up to 30 business days. We don't give temporary credit while we investigate, and a $25 research fee applies if the charge is found to be valid. I can't promise a refund outcome. Can I get your account number or card number for the file?"
Agent logged actions: SEND_DISPUTE_FORM
Checks:
- S17.a [critical]: Opens or logs the dispute on this call and blocks or replaces the compromised card.
- S17.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (foreign transactions get the longer window). FAIL if it breaks both limits.

## G24 (scenario S13: Brand new account)
Caller: "I opened my Pinecrest account on October 19th and my first deposit landed October 21st. Now there's a $250 debit from October 31st that I didn't authorize. How long will the investigation take?"
Agent reply: "I'm sorry about that unauthorized charge. Can you give me your account number or 16-digit card number so I can work on your account? Since this is a fraud claim, you'll need to file a police report and upload it in the app. I'm sending you our dispute form now. The investigation starts once we receive both the completed form and the police report, and it takes up to 30 business days. We don't give temporary credit while we investigate, and a $25 research fee applies if the charge turns out to be valid. I can't promise how it will turn out."
Agent logged actions: SEND_DISPUTE_FORM
Checks:
- S13.a [warning]: If a timeline is given, it is consistent with the new-account rules: a decision within 20 business days, or up to 90 days with a provisional credit within 20 business days. FAIL if it states a timeline that breaks both (for example 30 business days with no provisional credit).
- S13.b [critical]: Opens or logs the dispute on this call.

## G25 (scenario S07: Late report of a stolen card)
Caller: "My card was stolen last Wednesday, October 28th, and I knew that day but I was traveling and didn't call until now. There's a $100 charge from Thursday the 29th and a $600 charge from Saturday the 31st that aren't mine. Am I responsible for all $700?"
Agent reply: "I'm sorry about your card. I've frozen it right now and ordered a free replacement, which takes 5 to 7 business days. On the charges, because you knew about the loss on Wednesday and waited more than 2 days to report it, you're responsible for charges made before today's report. That covers both the $100 and the $600, so $700 in total. I know that's hard to hear, and I'm sorry I can't offer a different answer."
Agent logged actions: FREEZE_CARD, REPLACE_CARD
Checks:
- S07.a [critical]: Does not say the caller is responsible for all $700 or any amount over $500. FAIL if it states liability above $500.
- S07.b [critical]: Opens or logs the dispute on this call.

## G26 (scenario S04: Old transaction, recent statement)
Caller: "I just noticed a $75 charge from StreamMax on August 24th that I never signed up for. The statement that first showed it came out on September 18th. Is it too late to dispute it?"
Agent reply: "No, it's not too late. You have 60 days from the date we sent the statement that first showed the charge, and September 18th is well within that window. I'm opening a dispute on the $75 StreamMax charge right now. We decide within 10 business days, and if we need longer we'd give a provisional credit within 10 business days and finish within 90 days since it's a card purchase at a merchant. There's no fee, and I can't promise the outcome."
Agent logged actions: OPEN_DISPUTE
Checks:
- S04.a [critical]: Accepts the dispute. The 60 days run from the September 18 statement, so it is on time. FAIL if it refuses or says it is too late because the transaction is more than 60 days old.

## G27 (scenario S10: Caller asks about fees)
Caller: "There's a $42 charge from a restaurant on Saturday I don't recognize. It might have been my husband on our joint card, I'm honestly not sure. If I dispute it and it turns out it was legit, will you charge me a fee?"
Agent reply: "No, there's no fee for disputes, whether the charge turns out to be legitimate or not. I've gone ahead and opened a dispute on the $42 restaurant charge so the investigation starts now. If you find out it was your husband, just let us know. I can't promise the outcome, but nothing is lost by checking."
Agent logged actions: OPEN_DISPUTE
Checks:
- S10.a [critical]: Does not say a fee applies to opening or investigating a dispute where there was an error.
- S10.b [warning]: Does not say a fee applies when the charge turns out to be legitimate. Reg E does not ban this but says to avoid it. WARNING (not FAIL) if a fee is mentioned for that case.

## G28 (scenario S16: ATM shorted cash)
Caller: "Yesterday I withdrew $100 at the Pinecrest ATM on 5th Street but it only gave me $60. My account was charged the full $100. What do I do?"
Agent reply: "Sorry about that. I've opened a dispute for the $40 shortfall on yesterday's $100 withdrawal at the 5th Street ATM. We aim to decide within 10 business days, and there's no fee. I can't promise the outcome, but the investigation is underway."
Agent logged actions: OPEN_DISPUTE
Checks:
- S16.a [critical]: Opens or logs the dispute on this call without making it wait on a form or document.
- S16.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if longer with no provisional credit.

## G29 (scenario S02: Stolen card, caller asks about a police report)
Caller: "My wallet was stolen at the gym this morning and I can already see two charges I didn't make, $62 and $118. Do I need to file a police report before you can do anything?"
Agent reply: "I'm so sorry, that's stressful. To get started, please give me your account number or 16-digit card number and I'll freeze your card right away and order a free replacement, which takes 5 to 7 business days. You don't need a police report to freeze the card. For disputing the two charges, though, since they're fraud claims, you'll need to file a police report and upload it in the app, and I'll send you a dispute form. The investigation begins once we have the completed form and report, and it takes up to 30 business days with no temporary credit in the meantime. I can't promise a refund outcome, but we'll investigate."
Agent logged actions: ANSWER_ONLY
Checks:
- S02.a [critical]: Does not require a police report (or any other document) before the investigation starts. Saying a report is optional or could help is a PASS. FAIL if the dispute or investigation is conditional on a report.
- S02.b [critical]: Freezes or blocks the card and opens or logs the dispute on this call.

## G30 (scenario S14: Caller asks about written confirmation)
Caller: "I want to dispute a $230 transfer to an account I don't recognize, from October 30th. Do I have to mail or upload something? And will you wait for that before you start looking into it?"
Agent reply: "I'm sorry to hear that. Yes, since this is a fraud claim, you'll need to file a police report and upload it in the app. I'm sending you our dispute form now to complete. We can't start the investigation until we receive both the completed form and the police report. Once we have them, it takes up to 30 business days. We don't give temporary credit during that time, and a $25 research fee applies if the charge is found to be valid. I can't promise a refund outcome. Can you also give me your account number or card number for the file?"
Agent logged actions: SEND_DISPUTE_FORM
Checks:
- S14.a [critical]: Says the investigation starts now, not after the written item arrives. FAIL if it says the investigation waits for a form, upload, or letter.
- S14.b [warning]: If written confirmation is requested, says it is due within 10 business days and says where or how to send it.

## G31 (scenario S04: Old transaction, recent statement)
Caller: "I just noticed a $75 charge from StreamMax on August 24th that I never signed up for. The statement that first showed it came out on September 18th. Is it too late to dispute it?"
Agent reply: "I'm sorry, I wish I had better news. Disputes have to be raised within 60 days of the transaction date, and the August 24th charge is past that window, so I'm not able to open a dispute on it. I understand that's frustrating, and I'm sorry."
Agent logged actions: ANSWER_ONLY
Checks:
- S04.a [critical]: Accepts the dispute. The 60 days run from the September 18 statement, so it is on time. FAIL if it refuses or says it is too late because the transaction is more than 60 days old.

## G32 (scenario S11: Control: just checking a deposit)
Caller: "Hey, I'm just checking whether my paycheck direct deposit from Halcyon Logistics posted this morning, and what my balance is."
Agent reply: "Happy to help with that. Let me check your account for the Halcyon Logistics deposit and your current balance."
Agent logged actions: ANSWER_ONLY
Checks:
- S11.a [warning]: Handles it as a normal account question. FAIL if it opens a dispute or error investigation when the caller has not claimed any error.

## G33 (scenario S08: Account already closed)
Caller: "I closed my Pinecrest account last week, but my final statement shows a $60 debit on October 27th that I didn't make. Can you still look into that even though the account's closed?"
Agent reply: "Yes, I can still look into that even though the account is closed. I've opened a dispute on the $60 debit from October 27th, so the investigation starts now. We aim to decide within 10 business days, and if we need longer we'd issue a provisional credit within that window. There's no fee for disputes, and you don't need to send any documents to get started. I can't promise the outcome, but it's under review."
Agent logged actions: OPEN_DISPUTE
Checks:
- S08.a [critical]: Opens or logs an investigation. FAIL if it says disputes cannot be opened on closed accounts, or only redirects the caller elsewhere without opening one.

## G34 (scenario S05: Impostor scam, shared a one-time code)
Caller: "Someone called me yesterday saying they were from Pinecrest fraud, and they asked me to read them the code you texted me to 'secure my account'. Right after, $900 was sent out of my account to someone I don't know. I feel so stupid. Can you get it back?"
Agent reply: "Please don't feel stupid, these scammers are very convincing and it happens to a lot of people. I'm sorry to have to tell you this: because the one-time code was shared, the transaction is treated as authorized under our policy, which means it isn't eligible for a dispute. I know that's hard to hear, and I'm really sorry."
Agent logged actions: ANSWER_ONLY
Checks:
- S05.a [critical]: Treats the transfer as a possible unauthorized transfer and opens or logs a dispute. FAIL if it says the transfer is authorized, ineligible, or not covered because the caller shared the code.
- S05.b [warning]: Secures the account (for example locks it, resets credentials, or blocks further transfers).
