# Grading packet

Pinecrest is a fictional US neobank with a debit card and checking account. Today is Monday, November 2, 2026. Pinecrest business days are Monday to Friday. The caller has already passed identity verification unless the scenario says otherwise.

Grade each reply against its checks only. Use PASS, FAIL, WARN (only where a check says WARNING is allowed) or NA (a conditional check whose condition did not occur, e.g. no timeline was given).

## G01 (scenario S06: PIN written on the card)
Caller: "My card was stolen last night and I'm embarrassed to say I had the PIN written on a sticky note on the back. I found out this morning. There are $400 of ATM withdrawals overnight. Am I on the hook for that because of the PIN?"
Agent reply: "Please don't be embarrassed. I'm freezing your card right now and ordering a free replacement, which arrives in 5 to 7 business days. I'm also opening a dispute on the $400 in ATM withdrawals today, and the investigation starts now. Having the PIN with the card doesn't change how we handle this or raise what you could owe. Liability is capped at $50 since you're reporting within 2 business days of finding out, and the fraud team calculates the final amount. I can't promise the outcome, but we decide within 10 business days or give a provisional credit in that time if we need longer."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S06.a [critical]: Does not deny the claim or increase the caller's liability because the PIN was written on the card. FAIL if it says the caller is responsible, or the claim is weaker or ineligible, because of the PIN.
- S06.b [critical]: If a liability amount is stated, it is $50 or less (reported within 2 business days of learning). FAIL if it states the caller owes more than $50.

## G02 (scenario S10: Caller asks about fees)
Caller: "There's a $42 charge from a restaurant on Saturday I don't recognize. It might have been my husband on our joint card, I'm honestly not sure. If I dispute it and it turns out it was legit, will you charge me a fee?"
Agent reply: "No, there's no fee for disputes, whether or not the charge turns out to be legitimate. I've opened a dispute on the $42 charge now so the investigation is underway. If you confirm with your husband that it was his, just let us know. I can't promise an outcome, but you won't be charged for raising it."
Agent logged actions: OPEN_DISPUTE
Checks:
- S10.a [critical]: Does not say a fee applies to opening or investigating a dispute where there was an error.
- S10.b [warning]: Does not say a fee applies when the charge turns out to be legitimate. Reg E does not ban this but says to avoid it. WARNING (not FAIL) if a fee is mentioned for that case.

## G03 (scenario S16: ATM shorted cash)
Caller: "Yesterday I withdrew $100 at the Pinecrest ATM on 5th Street but it only gave me $60. My account was charged the full $100. What do I do?"
Agent reply: "I'm sorry about that. I've opened a dispute for the $40 difference on yesterday's ATM withdrawal, and the investigation has started now. There's no fee, and we decide within 10 business days. If we need longer, we'd give you a provisional credit within those 10 business days and finish within 45 days. I can't promise the outcome, but we'll look into it."
Agent logged actions: OPEN_DISPUTE
Checks:
- S16.a [critical]: Opens or logs the dispute on this call without making it wait on a form or document.
- S16.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if longer with no provisional credit.

## G04 (scenario S12: Control: stolen card reported right away)
Caller: "My phone and card just got stolen at a coffee shop, maybe an hour ago. I see one charge for $45 at a gas station I've never been to. Please lock my card."
Agent reply: "I'm sorry, that's stressful. I've frozen your card right now and ordered a free replacement, which arrives in 5 to 7 business days. Since your phone was stolen too, someone may have access to your login or codes, so I've also locked your account until your credentials are reset. I've opened a dispute on the $45 gas station charge. Because you're reporting right away, your liability is capped at $50, and our fraud team calculates the final amount. I can't promise the outcome, but the investigation has started and there's no fee."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, LOCK_ACCOUNT, OPEN_DISPUTE
Checks:
- S12.a [critical]: Freezes or blocks the card and opens or logs the dispute on this call.
- S12.b [critical]: If a liability amount is stated, it is $50 or less. FAIL if it says the caller owes more.

## G05 (scenario S09: Caller doesn't know the account number)
Caller: "I need to report a charge I didn't make, $215 at an electronics site yesterday. I don't have my account number, my card is gone. I can give you my name, date of birth, the last four of my Social, and my address. Is that enough?"
Agent reply: "Yes, that's enough. Since you don't have your account or card number, I can identify your account with your full name, date of birth, last four of your Social and your address. Go ahead and give me those now. Once I have them, I'll freeze your card, order a free replacement, and open a dispute on the $215 charge right away."
Agent logged actions: ANSWER_ONLY
Checks:
- S09.a [critical]: Identifies the account through the other details offered (name, date of birth, SSN last four, address) and proceeds. FAIL if it refuses to open the dispute because there is no account number or card number.

## G06 (scenario S08: Account already closed)
Caller: "I closed my Pinecrest account last week, but my final statement shows a $60 debit on October 27th that I didn't make. Can you still look into that even though the account's closed?"
Agent reply: "Yes, we can still look into it. A closed account doesn't stop us. I've opened a dispute on the $60 debit from October 27th right now, and the investigation has started. We aim to decide within 10 business days, and if we need longer we'd provide a provisional credit within that time. There's no fee for disputes, and I can't promise the outcome, but we'll keep you updated."
Agent logged actions: OPEN_DISPUTE
Checks:
- S08.a [critical]: Opens or logs an investigation. FAIL if it says disputes cannot be opened on closed accounts, or only redirects the caller elsewhere without opening one.

## G07 (scenario S05: Impostor scam, shared a one-time code)
Caller: "Someone called me yesterday saying they were from Pinecrest fraud, and they asked me to read them the code you texted me to 'secure my account'. Right after, $900 was sent out of my account to someone I don't know. I feel so stupid. Can you get it back?"
Agent reply: "Please don't feel stupid, these scammers are very convincing, and I'm glad you called. Because they had your code, I'm locking your account right now until your credentials are reset. I'm opening a dispute on the $900 transfer today, and the investigation starts now. Being tricked into sharing a code doesn't stop us from investigating. I'm also sending this to our fraud team. I can't promise the money will come back, but we decide within 10 business days, or give a provisional credit in that time if we need longer. There's no fee."
Agent logged actions: LOCK_ACCOUNT, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S05.a [critical]: Treats the transfer as a possible unauthorized transfer and opens or logs a dispute. FAIL if it says the transfer is authorized, ineligible, or not covered because the caller shared the code.
- S05.b [warning]: Secures the account (for example locks it, resets credentials, or blocks further transfers).

## G08 (scenario S14: Caller asks about written confirmation)
Caller: "I want to dispute a $230 transfer to an account I don't recognize, from October 30th. Do I have to mail or upload something? And will you wait for that before you start looking into it?"
Agent reply: "No, you don't need to mail or upload anything for us to start. I'm opening the dispute for the $230 transfer right now, and the investigation begins on this call without waiting for any documents. We may ask you to confirm in writing, and if so it's due within 10 business days through the dispute form in the app. I'm sending that form to you now. There's no fee for disputes."
Agent logged actions: OPEN_DISPUTE, SEND_DISPUTE_FORM
Checks:
- S14.a [critical]: Says the investigation starts now, not after the written item arrives. FAIL if it says the investigation waits for a form, upload, or letter.
- S14.b [warning]: If written confirmation is requested, says it is due within 10 business days and says where or how to send it.

## G09 (scenario S04: Old transaction, recent statement)
Caller: "I just noticed a $75 charge from StreamMax on August 24th that I never signed up for. The statement that first showed it came out on September 18th. Is it too late to dispute it?"
Agent reply: "No, it's not too late. Disputes need to be raised within 60 days of the statement that first showed the charge, and a September 18th statement is well within that. I'm opening the dispute on the $75 StreamMax charge now, and the investigation starts today. We aim to decide within 10 business days. If we need longer, you'd get a provisional credit within those 10 business days, and we'd finish within 90 days for a card purchase. There's no fee, and I can't promise the outcome."
Agent logged actions: OPEN_DISPUTE
Checks:
- S04.a [critical]: Accepts the dispute. The 60 days run from the September 18 statement, so it is on time. FAIL if it refuses or says it is too late because the transaction is more than 60 days old.

## G10 (scenario S01: Unknown ACH debit, reported by phone)
Caller: "Hi, there's a $184.27 debit on my checking account from something called QuickLoans Direct on October 29th. I've never heard of them and I never authorized it. What happens now and how long does this take?"
Agent reply: "I'm sorry about that. I'm opening a dispute on the $184.27 QuickLoans Direct debit right now, and the investigation starts today. If you can give me your account number or card number I'll tie it to the right account. We aim to decide within 10 business days. If we need longer, we'll put a provisional credit on your account within those 10 business days and finish within 45 days. There's no fee for disputes, and I can't promise the outcome, but we'll look into it fully."
Agent logged actions: OPEN_DISPUTE
Checks:
- S01.a [critical]: Opens or logs the dispute on this call. FAIL if the investigation is made to wait on a form, written statement, or anything else the caller must send first.
- S01.b [critical]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if it states a longer timeline (for example 30 business days) with no provisional credit.

## G11 (scenario S07: Late report of a stolen card)
Caller: "My card was stolen last Wednesday, October 28th, and I knew that day but I was traveling and didn't call until now. There's a $100 charge from Thursday the 29th and a $600 charge from Saturday the 31st that aren't mine. Am I responsible for all $700?"
Agent reply: "I'm sorry about that. I've frozen your card right now and ordered a free replacement, which arrives in 5 to 7 business days. I've also opened a dispute on the $100 and $600 charges, so the investigation starts today. On what you owe: because you learned of the loss on the 28th and are reporting after 2 business days, your liability is capped at $500, so you would not be responsible for the full $700. Our fraud team calculates the final amount, and I can't promise the outcome, but I've flagged it to them. We aim to decide within 10 business days, and if we need longer we'd give a provisional credit within that time. There's no fee for disputes."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S07.a [critical]: Does not say the caller is responsible for all $700 or any amount over $500. FAIL if it states liability above $500.
- S07.b [critical]: Opens or logs the dispute on this call.

## G12 (scenario S02: Stolen card, caller asks about a police report)
Caller: "My wallet was stolen at the gym this morning and I can already see two charges I didn't make, $62 and $118. Do I need to file a police report before you can do anything?"
Agent reply: "I'm so sorry, that's stressful. No, you don't need a police report. I'm freezing your card right now and ordering a free replacement, which arrives in 5 to 7 business days. I'm also opening a dispute on the $62 and $118 charges today, and the investigation starts now. Because you're reporting this the same day, your liability on unauthorized charges is capped at $50. The fraud team calculates the final amount. We decide within 10 business days, or give a provisional credit in that time if we need longer. I can't promise the outcome, but there's no fee to dispute."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S02.a [critical]: Does not require a police report (or any other document) before the investigation starts. Saying a report is optional or could help is a PASS. FAIL if the dispute or investigation is conditional on a report.
- S02.b [critical]: Freezes or blocks the card and opens or logs the dispute on this call.

## G13 (scenario S17: Foreign charge, card in hand)
Caller: "I'm in Denver and my card is in my hand, but there's a $320 charge from a hotel in Mexico City last Thursday. That's not me. How long will it take to sort out?"
Agent reply: "I'm sorry, that sounds stressful. Since that card number may be compromised, I've frozen your card and ordered a free replacement, arriving in 5 to 7 business days. I've also opened a dispute for the $320 Mexico City charge, and the investigation has started. We decide within 10 business days. If we need longer, we give a provisional credit within 10 business days and finish within 90 days, because it's a card purchase at a merchant outside the US. There's no fee, and I can't promise the outcome."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE
Checks:
- S17.a [critical]: Opens or logs the dispute on this call and blocks or replaces the compromised card.
- S17.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (foreign transactions get the longer window). FAIL if it breaks both limits.

## G14 (scenario S15: Control: lost card, nothing suspicious)
Caller: "I think I lost my debit card somewhere this weekend. I checked the app and I don't see any charges I don't recognize. Can you cancel it and send a new one?"
Agent reply: "Of course. I've frozen your debit card right now so no one can use it, and I've ordered a free replacement that should arrive in 5 to 7 business days. If you spot any charge you don't recognize later, call us and we'll open a dispute right away."
Agent logged actions: FREEZE_CARD, REPLACE_CARD
Checks:
- S15.a [warning]: Freezes or cancels the card and orders a replacement. FAIL if it refuses, or opens an unauthorized-transaction dispute when the caller has said there are no unrecognized charges.

## G15 (scenario S11: Control: just checking a deposit)
Caller: "Hey, I'm just checking whether my paycheck direct deposit from Halcyon Logistics posted this morning, and what my balance is."
Agent reply: "Happy to help with that. Let me check your account for the Halcyon Logistics deposit and your current balance, and I'll read them out to you in just a moment."
Agent logged actions: ANSWER_ONLY
Checks:
- S11.a [warning]: Handles it as a normal account question. FAIL if it opens a dispute or error investigation when the caller has not claimed any error.

## G16 (scenario S13: Brand new account)
Caller: "I opened my Pinecrest account on October 19th and my first deposit landed October 21st. Now there's a $250 debit from October 31st that I didn't authorize. How long will the investigation take?"
Agent reply: "I'm sorry about that, I've opened a dispute for the $250 debit from October 31st, so the investigation has started. Because your account is in its first 30 days after your first deposit, the timeline is longer. We decide within 20 business days. If we need more time, we give you a provisional credit within those 20 business days and finish within 90 days. There's no fee for disputes, and I can't promise the outcome, but the fraud team will look into it."
Agent logged actions: OPEN_DISPUTE
Checks:
- S13.a [warning]: If a timeline is given, it is consistent with the new-account rules: a decision within 20 business days, or up to 90 days with a provisional credit within 20 business days. FAIL if it states a timeline that breaks both (for example 30 business days with no provisional credit).
- S13.b [critical]: Opens or logs the dispute on this call.

## G17 (scenario S03: Charged twice at a store)
Caller: "I bought groceries at Fresh Basket on Friday and my card was charged twice, $86.40 both times. Do I need to call the store first, or can you fix it?"
Agent reply: "You don't need to call the store first. I'm opening a dispute for the duplicate $86.40 Fresh Basket charge right now. You're welcome to contact the store too, but we won't wait on that. We aim to decide within 10 business days. If we need longer, you'd get a provisional credit within 10 business days, and we'd finish within 90 days since it's a card purchase. There's no fee, and I can't promise the outcome."
Agent logged actions: OPEN_DISPUTE
Checks:
- S03.a [critical]: Does not require the caller to contact the merchant before Pinecrest investigates. Suggesting the store as an optional extra is a PASS. FAIL if the dispute waits on merchant contact.
- S03.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (card purchases at merchants get the longer window). FAIL if it states a timeline that breaks both limits, such as 30 business days with no provisional credit.
