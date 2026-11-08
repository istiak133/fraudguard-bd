"""Generate a synthetic, labelled SMS dataset (Banglish, Bangla, English).

label 1 = fraud/scam, 0 = legitimate. Templates are based on common scam patterns
seen in Bangladesh: PIN/OTP phishing, fake account-block threats, fake lottery,
"wrong cash-in, send it back", fake jobs/loans, phishing links.
Run: python -m ml.generate_dataset
"""
import csv
import random
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data" / "sms_dataset.csv"

PROVIDERS = ["bKash", "Nagad", "Rocket", "bkash", "BKASH", "বিকাশ", "নগদ"]
LINKS = ["bit.ly/bk-verify", "tinyurl.com/nagad-bonus", "http://bkash-offer.xyz", "www.bkash-update.top",
         "http://bit.ly/3xK9pQ", "https://nagad-reward.click", "t.me/bkash_help", "bkash-secure.info/login"]


def amount():
    return random.choice(["500", "1,000", "2,500", "5,000", "10,000", "15,000", "25,000", "50,000"])


def phone():
    return "01" + random.choice("356789") + "".join(random.choices("0123456789", k=8))


def trx():
    return "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=10))


def otp():
    return "".join(random.choices("0123456789", k=random.choice([4, 6])))


FRAUD = [
    lambda: f"Apnar {random.choice(PROVIDERS)} account 24 ghontar moddhe block hoye jabe. Ekhoni PIN diye verify korun: {random.choice(LINKS)}",
    lambda: f"Dear customer, your {random.choice(PROVIDERS)} account has been suspended. Verify now at {random.choice(LINKS)} to avoid closure.",
    lambda: f"অভিনন্দন! আপনি {random.choice(PROVIDERS)} লটারিতে {amount()} টাকা জিতেছেন। টাকা পেতে আপনার পিন নম্বর দিন।",
    lambda: f"Congratulations! You won Tk {amount()} {random.choice(PROVIDERS)} reward. Claim now: {random.choice(LINKS)}",
    lambda: f"Vai bhul kore apnar number e {amount()} tk pathiye felsi, please ferot pathan {phone()} number e. Allah apnar bhalo korbe",
    lambda: f"ভাই ভুল করে আপনার নাম্বারে {amount()} টাকা চলে গেছে, দয়া করে {phone()} নাম্বারে ফেরত দিন।",
    lambda: f"Cash In Tk {amount()} from {phone()} successful. Bhul kore gese, please call {phone()} and return the money.",
    lambda: f"Ami {random.choice(PROVIDERS)} head office theke bolchi. Apnar account update er jonno OTP code ta bolun.",
    lambda: f"আমি {random.choice(PROVIDERS)} কাস্টমার কেয়ার থেকে বলছি। আপনার অ্যাকাউন্ট আপডেট করতে ওটিপি কোডটি বলুন।",
    lambda: f"Your {random.choice(PROVIDERS)} OTP is {otp()}. Please share this code with our agent to receive your bonus.",
    lambda: f"Apni {random.choice(PROVIDERS)} theke {amount()} tk cashback peyechen! Claim korte ekhoni PIN din: {random.choice(LINKS)}",
    lambda: f"URGENT: Your {random.choice(PROVIDERS)} wallet will expire today. Update KYC at {random.choice(LINKS)} immediately.",
    lambda: f"Ghore bose din e {amount()} tk income! Registration fee matro 500 tk {random.choice(PROVIDERS)} korun {phone()} number e.",
    lambda: f"Sohoj kisti te {amount()} tk loan! Processing fee {random.choice(['300','500','1000'])} tk send korun {phone()} e. Ajkei loan paben.",
    lambda: f"আপনার {random.choice(PROVIDERS)} অ্যাকাউন্ট বন্ধ হয়ে যাবে। এখনই এই লিংকে ভেরিফাই করুন {random.choice(LINKS)}",
    lambda: f"{random.choice(PROVIDERS)} officer bolchi, apnar account e somossa hoyeche. Call korun {phone()} ekhoni, noile taka hariye jabe.",
    lambda: f"Last chance! {random.choice(PROVIDERS)} Eid bonus Tk {amount()}. Enter your PIN at {random.choice(LINKS)} to receive.",
    lambda: f"Apnar SIM e {amount()} tk prize esheche. Pete hole {random.choice(PROVIDERS)} PIN ar OTP pathan {phone()} number e.",
    lambda: f"Your account is locked due to suspicious activity. Send your password and PIN to {phone()} to unlock.",
    lambda: f"বিকাশ থেকে বলছি, আপনার একাউন্টে {amount()} টাকা বোনাস এসেছে। পেতে পিন নম্বর বলুন।",
    lambda: f"Mama ami bipode porsi, ei number e {amount()} tk pathao ekhoni {phone()}, pore bolbo. Kauke bolba na.",
    lambda: f"Free {random.choice(['10GB','25GB','50GB'])} internet! Click {random.choice(LINKS)} and login with your {random.choice(PROVIDERS)} PIN.",
]

LEGIT = [
    lambda: f"Cash In Tk {amount()} from {phone()} successful. Fee Tk 0.00. Balance Tk {amount()}. TrxID {trx()} at 08/11/2026 14:{random.randint(10,59)}",
    lambda: f"You have received Tk {amount()} from {phone()}. Ref {random.choice(['rent','bazar','gift','salary'])}. Balance Tk {amount()}. TrxID {trx()}",
    lambda: f"Send Money Tk {amount()} to {phone()} successful. Fee Tk 5.00. Balance Tk {amount()}. TrxID {trx()}",
    lambda: f"Payment Tk {amount()} to Daraz successful. Balance Tk {amount()}. TrxID {trx()}",
    lambda: f"Your {random.choice(PROVIDERS)} verification code is {otp()}. Never share this code with anyone. {random.choice(PROVIDERS)} never asks for your PIN or OTP.",
    lambda: f"আপনার ভেরিফিকেশন কোড {otp()}। এই কোড কাউকে দিবেন না।",
    lambda: f"Mobile recharge Tk {random.choice(['20','50','100','200'])} to {phone()} successful. Balance Tk {amount()}. TrxID {trx()}",
    lambda: f"Ami ashtesi 10 minute e, tumi ready thako.",
    lambda: f"Bhai kal meeting ta 11 tay, office e chole ashben.",
    lambda: f"Ammu bolse ajke rate bazar korte hobe, tumi ashar shomoy dim niye esho.",
    lambda: f"আজকে সন্ধ্যায় বাসায় আসবে? সবাই আসছে।",
    lambda: f"Your Daraz order #{random.randint(100000,999999)} has been shipped and will arrive in 2-3 days.",
    lambda: f"Dear customer, your electricity bill of Tk {amount()} is due on 15 Nov. Pay via the official app.",
    lambda: f"Tomar taka pathiye diyechi, check kore dekho to peyecho kina.",
    lambda: f"{random.choice(PROVIDERS)}: Get 10% cashback on payments at Shwapno this week. T&C apply. Dial *247# for details.",
    lambda: f"Apnar Grameenphone internet pack {random.choice(['5GB','10GB'])} activated. Validity 7 days.",
    lambda: f"Reminder: your doctor appointment is tomorrow at 5 PM. Please arrive 10 minutes early.",
    lambda: f"Happy birthday bhai! Onek onek shubhokamona.",
    lambda: f"Class cancel ajke, kal extra class hobe 9 tay.",
    lambda: f"Bill Payment Tk {amount()} to DESCO successful. Balance Tk {amount()}. TrxID {trx()}",
    lambda: f"আপনার {random.choice(['ডিপিডিসি','ওয়াসা'])} বিল {amount()} টাকা সফলভাবে পরিশোধ হয়েছে।",
    lambda: f"Bhaiya rent ta {random.choice(PROVIDERS)} kore diyechi, {amount()} tk. Check koren.",
    lambda: f"Assalamualaikum, apnar parcel ta {random.choice(['delivery hoyeche','pathiye diyechi','kal paben'])}? Amake janaben.",
    lambda: f"{random.choice(['Assalamualaikum','Salam','Hi','Hello'])} {random.choice(['bhai','apu','vaia','mama'])}, {random.choice(['kemon achen','ki obostha','free thakle call diyen','kal dekha hobe'])}?",
    lambda: f"Apnar order ti {random.choice(['Pathao','RedX','Steadfast','Sundarban'])} courier e pathano hoyeche. Tracking ID {trx()}.",
    lambda: f"{random.choice(['Ami','Amra'])} {random.choice(['bazar e','office e','class e','rastay'])} achi, {random.choice(['pore call dicchi','5 min e ashchi','ektu wait koro'])}.",
    lambda: f"Kal {random.choice(['dawat','biye','meeting','exam'])} ache, {random.choice(['bhule jeo na','time moto esho','sobaike bolo'])}.",
    lambda: f"আসসালামু আলাইকুম, {random.choice(['কেমন আছেন','কাল দেখা হবে','ফ্রি হলে ফোন দিয়েন','পার্সেল পেয়েছেন'])}?",
    lambda: f"Dear student, your {random.choice(['mid','final','quiz'])} exam result has been published. Check the university portal.",
    lambda: f"Your ride with {random.choice(['Pathao','Uber','Obhai'])} is arriving in {random.randint(2,9)} minutes. Driver: {random.choice(['Rafiq','Jamal','Sumon'])}.",
    lambda: f"Thank you for shopping at {random.choice(['Shwapno','Agora','Meena Bazar'])}. You earned {random.randint(10,99)} points.",
    lambda: f"Apu ami pouche gesi, chinta korben na. Rate kotha bolbo.",
    lambda: f"Bhai apnar delivery ta ajke dite parbo na, kal shokale dibo inshallah.",
    lambda: f"Package delivered successfully. Thank you for choosing {random.choice(['Daraz','Chaldal','Foodpanda'])}.",
]


def main(n_per_class: int = 1200) -> None:
    rows = [(random.choice(FRAUD)(), 1) for _ in range(n_per_class)]
    rows += [(random.choice(LEGIT)(), 0) for _ in range(n_per_class)]
    rows = list({text: (text, label) for text, label in rows}.values())  # drop exact duplicates
    random.shuffle(rows)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label"])
        w.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
