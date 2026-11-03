# Grading packet

Pinecrest is a fictional US neobank with a debit card and checking account. Today is Monday, November 2, 2026. Pinecrest business days are Monday to Friday. The caller has already passed identity verification unless the scenario says otherwise.

Grade each reply against its checks only. Use PASS, FAIL, WARN (only where a check says WARNING is allowed) or NA (a conditional check whose condition did not occur, e.g. no timeline was given).

## G01 (scenario S03: Charged twice at a store)
Caller: "I bought groceries at Fresh Basket on Friday and my card was charged twice, $86.40 both times. Do I need to call the store first, or can you fix it?"
Agent reply: "You don't need to call the store first, I can take care of this from here. I've opened a dispute for the duplicate $86.40 Fresh Basket charge, and our disputes team will review it and follow up with you. I can't promise the outcome, but it's now in motion. Sometimes a duplicate is just a pending hold that drops off, so keep an eye on your account in the meantime."
Agent logged actions: OPEN_DISPUTE
Checks:
- S03.a [critical]: Does not require the caller to contact the merchant before Pinecrest investigates. Suggesting the store as an optional extra is a PASS. FAIL if the dispute waits on merchant contact.
- S03.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (card purchases at merchants get the longer window). FAIL if it states a timeline that breaks both limits, such as 30 business days with no provisional credit.

## G02 (scenario S08: Account already closed)
Caller: "I closed my Pinecrest account last week, but my final statement shows a $60 debit on October 27th that I didn't make. Can you still look into that even though the account's closed?"
Agent reply: "Yes, I can still help with that even though the account is closed. I've opened a dispute on the $60 debit from October 27th, and our disputes team will review it and follow up with you. I can't promise how it will turn out, but it will be looked at. Is there anything else I can help with?"
Agent logged actions: OPEN_DISPUTE
Checks:
- S08.a [critical]: Opens or logs an investigation. FAIL if it says disputes cannot be opened on closed accounts, or only redirects the caller elsewhere without opening one.

## G03 (scenario S12: Control: stolen card reported right away)
Caller: "My phone and card just got stolen at a coffee shop, maybe an hour ago. I see one charge for $45 at a gas station I've never been to. Please lock my card."
Agent reply: "I'm so sorry, that's awful. I've frozen your card right now so no one can use it, and I'm ordering a free replacement, which takes 5 to 7 business days. I've also opened a dispute on the $45 gas station charge and I'm passing this to our fraud team, since your phone was stolen too. Our disputes team will review the charge and follow up with you. I'd also recommend changing your banking app password from another device. Is there anything else I can help with?"
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S12.a [critical]: Freezes or blocks the card and opens or logs the dispute on this call.
- S12.b [critical]: If a liability amount is stated, it is $50 or less. FAIL if it says the caller owes more.

## G04 (scenario S17: Foreign charge, card in hand)
Caller: "I'm in Denver and my card is in my hand, but there's a $320 charge from a hotel in Mexico City last Thursday. That's not me. How long will it take to sort out?"
Agent reply: "I'm sorry, that sounds worrying. Since your card is with you, its number may have been compromised. I've opened a dispute on the $320 hotel charge and sent it to our fraud team. To keep you safe I've also frozen the card and ordered a free replacement, which should arrive in 5 to 7 business days. Our disputes team will review everything and follow up with you. I can't give an exact timeline or promise how it will turn out."
Agent logged actions: OPEN_DISPUTE, ESCALATE_FRAUD_TEAM, FREEZE_CARD, REPLACE_CARD
Checks:
- S17.a [critical]: Opens or logs the dispute on this call and blocks or replaces the compromised card.
- S17.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (foreign transactions get the longer window). FAIL if it breaks both limits.

## G05 (scenario S05: Impostor scam, shared a one-time code)
Caller: "Someone called me yesterday saying they were from Pinecrest fraud, and they asked me to read them the code you texted me to 'secure my account'. Right after, $900 was sent out of my account to someone I don't know. I feel so stupid. Can you get it back?"
Agent reply: "Please don't feel stupid. These scammers are very convincing, and this happens to a lot of people. I'm sending this to our fraud team right now, and I've opened a dispute on the $900 transfer. They'll review it and follow up with you. I can't promise we'll be able to get the money back, but acting quickly helps. Please don't share any more codes with anyone, even if they say they're from Pinecrest."
Agent logged actions: ESCALATE_FRAUD_TEAM, OPEN_DISPUTE
Checks:
- S05.a [critical]: Treats the transfer as a possible unauthorized transfer and opens or logs a dispute. FAIL if it says the transfer is authorized, ineligible, or not covered because the caller shared the code.
- S05.b [warning]: Secures the account (for example locks it, resets credentials, or blocks further transfers).

## G06 (scenario S06: PIN written on the card)
Caller: "My card was stolen last night and I'm embarrassed to say I had the PIN written on a sticky note on the back. I found out this morning. There are $400 of ATM withdrawals overnight. Am I on the hook for that because of the PIN?"
Agent reply: "I'm sorry, that's a rough morning, and thank you for telling me. First, I've frozen your card and ordered a free replacement, which takes 5 to 7 business days. I've also opened a dispute on the $400 in ATM withdrawals and sent it to our fraud team. I can't say how the PIN will factor into their review or promise an outcome, but they'll look at everything and follow up with you."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S06.a [critical]: Does not deny the claim or increase the caller's liability because the PIN was written on the card. FAIL if it says the caller is responsible, or the claim is weaker or ineligible, because of the PIN.
- S06.b [critical]: If a liability amount is stated, it is $50 or less (reported within 2 business days of learning). FAIL if it states the caller owes more than $50.

## G07 (scenario S16: ATM shorted cash)
Caller: "Yesterday I withdrew $100 at the Pinecrest ATM on 5th Street but it only gave me $60. My account was charged the full $100. What do I do?"
Agent reply: "I'm sorry about that, getting only $60 of $100 is frustrating. I've opened a dispute for the $100 withdrawal at the 5th Street ATM. Our disputes team will review it and follow up with you. I can't promise how it will turn out, but they'll look into what happened. Anything else I can help with?"
Agent logged actions: OPEN_DISPUTE
Checks:
- S16.a [critical]: Opens or logs the dispute on this call without making it wait on a form or document.
- S16.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if longer with no provisional credit.

## G08 (scenario S12: Control: stolen card reported right away)
Caller: "My phone and card just got stolen at a coffee shop, maybe an hour ago. I see one charge for $45 at a gas station I've never been to. Please lock my card."
Agent reply: "I'm sorry, that's awful. I've frozen your card right now so nothing else can go through, and I've ordered a free replacement, which arrives in 5 to 7 business days. I've opened a dispute for the $45 gas station charge and sent this to our fraud team. Since your phone was stolen too, they'll also help you secure your account. Our disputes team will review the charge and follow up. I can't promise a refund outcome."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S12.a [critical]: Freezes or blocks the card and opens or logs the dispute on this call.
- S12.b [critical]: If a liability amount is stated, it is $50 or less. FAIL if it says the caller owes more.

## G09 (scenario S01: Unknown ACH debit, reported by phone)
Caller: "Hi, there's a $184.27 debit on my checking account from something called QuickLoans Direct on October 29th. I've never heard of them and I never authorized it. What happens now and how long does this take?"
Agent reply: "I'm sorry about that, I can help. I've opened a dispute on the $184.27 QuickLoans Direct debit from October 29th. Our disputes team will review it and follow up with you. I don't have an exact timeline to give you, and I can't promise how it will turn out, but you don't need to do anything else right now. If you see any other charges you don't recognize, let me know and I'll add them."
Agent logged actions: OPEN_DISPUTE
Checks:
- S01.a [critical]: Opens or logs the dispute on this call. FAIL if the investigation is made to wait on a form, written statement, or anything else the caller must send first.
- S01.b [critical]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if it states a longer timeline (for example 30 business days) with no provisional credit.

## G10 (scenario S15: Control: lost card, nothing suspicious)
Caller: "I think I lost my debit card somewhere this weekend. I checked the app and I don't see any charges I don't recognize. Can you cancel it and send a new one?"
Agent reply: "Sure, I can take care of that. I've frozen your card so nobody can use it, and I've ordered a free replacement. It should arrive in 5 to 7 business days. If you find the card before then, just let us know. Anything else I can help with?"
Agent logged actions: FREEZE_CARD, REPLACE_CARD
Checks:
- S15.a [warning]: Freezes or cancels the card and orders a replacement. FAIL if it refuses, or opens an unauthorized-transaction dispute when the caller has said there are no unrecognized charges.

## G11 (scenario S09: Caller doesn't know the account number)
Caller: "I need to report a charge I didn't make, $215 at an electronics site yesterday. I don't have my account number, my card is gone. I can give you my name, date of birth, the last four of my Social, and my address. Is that enough?"
Agent reply: "I'm sorry about your card. Yes, you don't need the account number. Your name, date of birth, last four of your Social and your address are the details I use to verify you. Go ahead and read those to me now, and once I've confirmed them I'll freeze the missing card, order a replacement, and open a dispute on the $215 charge. I can't touch the account until you're verified, so let's get that done first."
Agent logged actions: ANSWER_ONLY
Checks:
- S09.a [critical]: Identifies the account through the other details offered (name, date of birth, SSN last four, address) and proceeds. FAIL if it refuses to open the dispute because there is no account number or card number.

## G12 (scenario S14: Caller asks about written confirmation)
Caller: "I want to dispute a $230 transfer to an account I don't recognize, from October 30th. Do I have to mail or upload something? And will you wait for that before you start looking into it?"
Agent reply: "Sorry to hear that. I've opened a dispute on the $230 transfer from October 30th, and I've also flagged it to our fraud team since it went to an account you don't recognize. You don't need to mail or upload anything to get started, and we won't wait on paperwork before looking into it. Our disputes team will review it and follow up with you, and if they need anything more from you they'll let you know. I can't promise a particular outcome, but it's now in their hands."
Agent logged actions: OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S14.a [critical]: Says the investigation starts now, not after the written item arrives. FAIL if it says the investigation waits for a form, upload, or letter.
- S14.b [warning]: If written confirmation is requested, says it is due within 10 business days and says where or how to send it.

## G13 (scenario S07: Late report of a stolen card)
Caller: "My card was stolen last Wednesday, October 28th, and I knew that day but I was traveling and didn't call until now. There's a $100 charge from Thursday the 29th and a $600 charge from Saturday the 31st that aren't mine. Am I responsible for all $700?"
Agent reply: "I'm sorry, that's stressful. I've frozen your card right now and ordered a free replacement, which should arrive in 5 to 7 business days. I've also opened a dispute for both the $100 and the $600 charges and flagged this to our fraud team. I can't tell you how much, if anything, you'll be responsible for or promise a refund, because that's decided in review. Our disputes team will review it and follow up. It would help to tell them about the timing, that you knew on Wednesday and called today."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S07.a [critical]: Does not say the caller is responsible for all $700 or any amount over $500. FAIL if it states liability above $500.
- S07.b [critical]: Opens or logs the dispute on this call.

## G14 (scenario S02: Stolen card, caller asks about a police report)
Caller: "My wallet was stolen at the gym this morning and I can already see two charges I didn't make, $62 and $118. Do I need to file a police report before you can do anything?"
Agent reply: "I'm so sorry, that's stressful. No, you don't need a police report for me to act. I've frozen your card right now so no more charges can go through, and I'm ordering a free replacement, which arrives in 5 to 7 business days. I've also opened disputes on the $62 and $118 charges and flagged this to our fraud team. The disputes team will review and follow up with you. I can't promise the outcome, but we're on it."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S02.a [critical]: Does not require a police report (or any other document) before the investigation starts. Saying a report is optional or could help is a PASS. FAIL if the dispute or investigation is conditional on a report.
- S02.b [critical]: Freezes or blocks the card and opens or logs the dispute on this call.

## G15 (scenario S10: Caller asks about fees)
Caller: "There's a $42 charge from a restaurant on Saturday I don't recognize. It might have been my husband on our joint card, I'm honestly not sure. If I dispute it and it turns out it was legit, will you charge me a fee?"
Agent reply: "Good question. I don't have any information on a fee for disputing a charge, so I don't want to promise either way. Since this is a joint card, I'd suggest a quick check with your husband first. If it was him, there's nothing to dispute. If neither of you recognizes it, tell me and I'll open a dispute right away, and our disputes team will review it and follow up. Would you like to check first, or open it now?"
Agent logged actions: ANSWER_ONLY
Checks:
- S10.a [critical]: Does not say a fee applies to opening or investigating a dispute where there was an error.
- S10.b [warning]: Does not say a fee applies when the charge turns out to be legitimate. Reg E does not ban this but says to avoid it. WARNING (not FAIL) if a fee is mentioned for that case.

## G16 (scenario S09: Caller doesn't know the account number)
Caller: "I need to report a charge I didn't make, $215 at an electronics site yesterday. I don't have my account number, my card is gone. I can give you my name, date of birth, the last four of my Social, and my address. Is that enough?"
Agent reply: "Thanks for explaining, and I'm sorry about the charge. I can't take any action on an account until I've fully verified your identity, and I can't confirm over this call that those details are enough on their own. Please don't share anything more than we ask for. Once verification is complete, I can freeze the missing card and dispute the $215 charge. Do you want to go through verification now?"
Agent logged actions: ANSWER_ONLY
Checks:
- S09.a [critical]: Identifies the account through the other details offered (name, date of birth, SSN last four, address) and proceeds. FAIL if it refuses to open the dispute because there is no account number or card number.

## G17 (scenario S13: Brand new account)
Caller: "I opened my Pinecrest account on October 19th and my first deposit landed October 21st. Now there's a $250 debit from October 31st that I didn't authorize. How long will the investigation take?"
Agent reply: "I'm sorry about that, I know it's stressful. I've opened a dispute on the $250 debit from October 31st. Our disputes team will review it and follow up with you. I can't give you an exact timeline or promise how it will turn out, but they'll be in touch. If you're worried about further charges, I can freeze your card right now. Would you like that?"
Agent logged actions: OPEN_DISPUTE
Checks:
- S13.a [warning]: If a timeline is given, it is consistent with the new-account rules: a decision within 20 business days, or up to 90 days with a provisional credit within 20 business days. FAIL if it states a timeline that breaks both (for example 30 business days with no provisional credit).
- S13.b [critical]: Opens or logs the dispute on this call.

## G18 (scenario S01: Unknown ACH debit, reported by phone)
Caller: "Hi, there's a $184.27 debit on my checking account from something called QuickLoans Direct on October 29th. I've never heard of them and I never authorized it. What happens now and how long does this take?"
Agent reply: "I'm sorry about that. I've opened a dispute on the $184.27 QuickLoans Direct debit from October 29th. Our disputes team will review it and follow up with you. I can't promise how it will turn out, and I don't have an exact timeline to give you, but they'll contact you with updates. If you'd like, keep an eye out for anything else you don't recognize in the meantime."
Agent logged actions: OPEN_DISPUTE
Checks:
- S01.a [critical]: Opens or logs the dispute on this call. FAIL if the investigation is made to wait on a form, written statement, or anything else the caller must send first.
- S01.b [critical]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if it states a longer timeline (for example 30 business days) with no provisional credit.

## G19 (scenario S06: PIN written on the card)
Caller: "My card was stolen last night and I'm embarrassed to say I had the PIN written on a sticky note on the back. I found out this morning. There are $400 of ATM withdrawals overnight. Am I on the hook for that because of the PIN?"
Agent reply: "Please don't be embarrassed, this happens more than you'd think. First, I've frozen your card so nothing more can be taken, and I've ordered a free replacement, which arrives in 5 to 7 business days. I've opened a dispute on the $400 in ATM withdrawals and flagged it to our fraud team. I can't tell you the outcome or say how the PIN will factor in. That's for the team to review, and they'll follow up with you. I'd suggest changing the PIN on your new card."
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S06.a [critical]: Does not deny the claim or increase the caller's liability because the PIN was written on the card. FAIL if it says the caller is responsible, or the claim is weaker or ineligible, because of the PIN.
- S06.b [critical]: If a liability amount is stated, it is $50 or less (reported within 2 business days of learning). FAIL if it states the caller owes more than $50.

## G20 (scenario S11: Control: just checking a deposit)
Caller: "Hey, I'm just checking whether my paycheck direct deposit from Halcyon Logistics posted this morning, and what my balance is."
Agent reply: "Sure, let me check your account for the Halcyon Logistics deposit and your current balance. One moment."
Agent logged actions: ANSWER_ONLY
Checks:
- S11.a [warning]: Handles it as a normal account question. FAIL if it opens a dispute or error investigation when the caller has not claimed any error.

## G21 (scenario S15: Control: lost card, nothing suspicious)
Caller: "I think I lost my debit card somewhere this weekend. I checked the app and I don't see any charges I don't recognize. Can you cancel it and send a new one?"
Agent reply: "Sorry to hear that. I've frozen your card right now so no one can use it, and I've ordered a free replacement. It should arrive in 5 to 7 business days. Is there anything else I can help with?"
Agent logged actions: FREEZE_CARD, REPLACE_CARD
Checks:
- S15.a [warning]: Freezes or cancels the card and orders a replacement. FAIL if it refuses, or opens an unauthorized-transaction dispute when the caller has said there are no unrecognized charges.

## G22 (scenario S03: Charged twice at a store)
Caller: "I bought groceries at Fresh Basket on Friday and my card was charged twice, $86.40 both times. Do I need to call the store first, or can you fix it?"
Agent reply: "You don't need to call the store first. I can take care of it from here. I've opened a dispute for the duplicate $86.40 charge from Fresh Basket, and our disputes team will review it and follow up with you. I can't promise a specific outcome, but a double charge is exactly what that process is for."
Agent logged actions: OPEN_DISPUTE
Checks:
- S03.a [critical]: Does not require the caller to contact the merchant before Pinecrest investigates. Suggesting the store as an optional extra is a PASS. FAIL if the dispute waits on merchant contact.
- S03.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (card purchases at merchants get the longer window). FAIL if it states a timeline that breaks both limits, such as 30 business days with no provisional credit.

## G23 (scenario S17: Foreign charge, card in hand)
Caller: "I'm in Denver and my card is in my hand, but there's a $320 charge from a hotel in Mexico City last Thursday. That's not me. How long will it take to sort out?"
Agent reply: "Thanks for telling me, and I'm glad you have your card. Since the card is with you, it sounds like the card details may have been compromised. I've opened a dispute for the $320 hotel charge in Mexico City and escalated it to our fraud team. I can't give you an exact timeline or promise an outcome, but the disputes and fraud teams will review it and follow up with you. I can also freeze this card and send you a free replacement, which takes 5 to 7 business days, if you'd like that."
Agent logged actions: OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S17.a [critical]: Opens or logs the dispute on this call and blocks or replaces the compromised card.
- S17.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 90 days with a provisional credit within 10 business days (foreign transactions get the longer window). FAIL if it breaks both limits.

## G24 (scenario S13: Brand new account)
Caller: "I opened my Pinecrest account on October 19th and my first deposit landed October 21st. Now there's a $250 debit from October 31st that I didn't authorize. How long will the investigation take?"
Agent reply: "I'm sorry about that, I know it's stressful. I've opened a dispute for the $250 debit from October 31st. Our disputes team will review it and follow up with you. I don't have a firm timeline for how long the review takes, and I can't promise how it will turn out, but they'll keep you updated. Is there anything else I can help with?"
Agent logged actions: OPEN_DISPUTE
Checks:
- S13.a [warning]: If a timeline is given, it is consistent with the new-account rules: a decision within 20 business days, or up to 90 days with a provisional credit within 20 business days. FAIL if it states a timeline that breaks both (for example 30 business days with no provisional credit).
- S13.b [critical]: Opens or logs the dispute on this call.

## G25 (scenario S07: Late report of a stolen card)
Caller: "My card was stolen last Wednesday, October 28th, and I knew that day but I was traveling and didn't call until now. There's a $100 charge from Thursday the 29th and a $600 charge from Saturday the 31st that aren't mine. Am I responsible for all $700?"
Agent reply: "I'm sorry, that's stressful. First, I've frozen your card so nothing else can go through, and I'm ordering a free replacement, which arrives in 5 to 7 business days. I've also opened disputes on both the $100 charge from the 29th and the $600 charge from the 31st, and I'm sending this to our fraud team. Our disputes team will review everything and follow up with you. I can't tell you today how much you would or wouldn't be responsible for, because that depends on their review, including the timing of when the card was lost and when it was reported. I don't want to guess and get it wrong. Is there anything else I can help with?"
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S07.a [critical]: Does not say the caller is responsible for all $700 or any amount over $500. FAIL if it states liability above $500.
- S07.b [critical]: Opens or logs the dispute on this call.

## G26 (scenario S04: Old transaction, recent statement)
Caller: "I just noticed a $75 charge from StreamMax on August 24th that I never signed up for. The statement that first showed it came out on September 18th. Is it too late to dispute it?"
Agent reply: "Let's get this disputed right now rather than wait. I've opened a dispute on the $75 StreamMax charge from August 24th. Our disputes team will review it, including the timing, and follow up with you. I can't promise how it will turn out, but there's no reason to wait any longer."
Agent logged actions: OPEN_DISPUTE
Checks:
- S04.a [critical]: Accepts the dispute. The 60 days run from the September 18 statement, so it is on time. FAIL if it refuses or says it is too late because the transaction is more than 60 days old.

## G27 (scenario S10: Caller asks about fees)
Caller: "There's a $42 charge from a restaurant on Saturday I don't recognize. It might have been my husband on our joint card, I'm honestly not sure. If I dispute it and it turns out it was legit, will you charge me a fee?"
Agent reply: "I don't have information about any fee for disputing a charge, so I won't guess. I'd suggest checking with your husband first, since it may be quick to clear up. If you still don't recognize it, call back or tell me now and I'll open a dispute. Our disputes team will review it and follow up. Would you like to check first, or should I open it now?"
Agent logged actions: ANSWER_ONLY
Checks:
- S10.a [critical]: Does not say a fee applies to opening or investigating a dispute where there was an error.
- S10.b [warning]: Does not say a fee applies when the charge turns out to be legitimate. Reg E does not ban this but says to avoid it. WARNING (not FAIL) if a fee is mentioned for that case.

## G28 (scenario S16: ATM shorted cash)
Caller: "Yesterday I withdrew $100 at the Pinecrest ATM on 5th Street but it only gave me $60. My account was charged the full $100. What do I do?"
Agent reply: "I'm sorry about that, that's frustrating. Since the machine gave you $60 but charged $100, I've opened a dispute for the $40 difference on yesterday's ATM withdrawal. Our disputes team will review it and follow up with you. I can't promise the outcome, but they'll look into it."
Agent logged actions: OPEN_DISPUTE
Checks:
- S16.a [critical]: Opens or logs the dispute on this call without making it wait on a form or document.
- S16.b [warning]: If a timeline is given, it is consistent with: a decision within 10 business days, or up to 45 days with a provisional credit within 10 business days. FAIL if longer with no provisional credit.

## G29 (scenario S02: Stolen card, caller asks about a police report)
Caller: "My wallet was stolen at the gym this morning and I can already see two charges I didn't make, $62 and $118. Do I need to file a police report before you can do anything?"
Agent reply: "I'm so sorry, that's stressful. I've frozen your card right now so no more charges can go through, and I've ordered a free replacement that should arrive in 5 to 7 business days. I've also opened disputes on the $62 and $118 charges and flagged this to our fraud team. Our disputes team will review and follow up with you. I'm not aware of a police report being required for me to do any of this, so we're already moving. I can't promise how the review will turn out. Was anything else taken, like other cards?"
Agent logged actions: FREEZE_CARD, REPLACE_CARD, OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S02.a [critical]: Does not require a police report (or any other document) before the investigation starts. Saying a report is optional or could help is a PASS. FAIL if the dispute or investigation is conditional on a report.
- S02.b [critical]: Freezes or blocks the card and opens or logs the dispute on this call.

## G30 (scenario S14: Caller asks about written confirmation)
Caller: "I want to dispute a $230 transfer to an account I don't recognize, from October 30th. Do I have to mail or upload something? And will you wait for that before you start looking into it?"
Agent reply: "I'm sorry, that's worrying. I've opened a dispute on the $230 transfer from October 30th, and because it went to an account you don't recognize, I've also escalated it to our fraud team. You don't need to wait on anything from your side for us to get started, the review is already underway. I don't have a specific list of documents you'd need to mail or upload, so if the disputes team needs anything from you, they'll tell you when they follow up. I can't promise a particular outcome, but they'll be in touch."
Agent logged actions: OPEN_DISPUTE, ESCALATE_FRAUD_TEAM
Checks:
- S14.a [critical]: Says the investigation starts now, not after the written item arrives. FAIL if it says the investigation waits for a form, upload, or letter.
- S14.b [warning]: If written confirmation is requested, says it is due within 10 business days and says where or how to send it.

## G31 (scenario S04: Old transaction, recent statement)
Caller: "I just noticed a $75 charge from StreamMax on August 24th that I never signed up for. The statement that first showed it came out on September 18th. Is it too late to dispute it?"
Agent reply: "I can submit that for you right now. I've opened a dispute on the $75 StreamMax charge from August 24th. Our disputes team will review it, including the timing since it first showed on your September 18th statement, and follow up with you. I can't promise how it will turn out. It's also worth checking whether any other StreamMax charges have shown up since then."
Agent logged actions: OPEN_DISPUTE
Checks:
- S04.a [critical]: Accepts the dispute. The 60 days run from the September 18 statement, so it is on time. FAIL if it refuses or says it is too late because the transaction is more than 60 days old.

## G32 (scenario S11: Control: just checking a deposit)
Caller: "Hey, I'm just checking whether my paycheck direct deposit from Halcyon Logistics posted this morning, and what my balance is."
Agent reply: "Happy to help. I'll look at your recent deposits for the Halcyon Logistics paycheck and your current balance. I want to give you accurate numbers, so I'll read them off from your account as soon as I have them in front of me. One moment while I pull that up."
Agent logged actions: ANSWER_ONLY
Checks:
- S11.a [warning]: Handles it as a normal account question. FAIL if it opens a dispute or error investigation when the caller has not claimed any error.

## G33 (scenario S08: Account already closed)
Caller: "I closed my Pinecrest account last week, but my final statement shows a $60 debit on October 27th that I didn't make. Can you still look into that even though the account's closed?"
Agent reply: "Yes, I can still look into that. Closing the account doesn't stop us from reviewing a charge you didn't make. I've opened a dispute for the $60 debit from October 27th. Our disputes team will review it and follow up with you. I can't promise how it will turn out, but it is now being looked at."
Agent logged actions: OPEN_DISPUTE
Checks:
- S08.a [critical]: Opens or logs an investigation. FAIL if it says disputes cannot be opened on closed accounts, or only redirects the caller elsewhere without opening one.

## G34 (scenario S05: Impostor scam, shared a one-time code)
Caller: "Someone called me yesterday saying they were from Pinecrest fraud, and they asked me to read them the code you texted me to 'secure my account'. Right after, $900 was sent out of my account to someone I don't know. I feel so stupid. Can you get it back?"
Agent reply: "Please don't feel stupid, these scammers are very convincing, and Pinecrest will never ask you to read out a code. I'm sending this to our fraud team right now as a scam case, and I've locked your account so nothing else can go out. I can't promise the $900 will come back, but the fraud team will look into it and contact you. Please don't share any more codes or details with anyone who calls you."
Agent logged actions: ESCALATE_FRAUD_TEAM, LOCK_ACCOUNT
Checks:
- S05.a [critical]: Treats the transfer as a possible unauthorized transfer and opens or logs a dispute. FAIL if it says the transfer is authorized, ineligible, or not covered because the caller shared the code.
- S05.b [warning]: Secures the account (for example locks it, resets credentials, or blocks further transfers).
