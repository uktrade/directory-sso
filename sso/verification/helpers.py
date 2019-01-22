from datetime import datetime


def check_verification_match(user, verification_code):
    if user.verificationcode.code == verification_code:
        user.verificationcode.date_verified = datetime.utcnow()
        user.verificationcode.save()
