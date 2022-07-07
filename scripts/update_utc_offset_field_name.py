import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

def main():
    load_dotenv()
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    DATABASE_URL = os.getenv("DATABASE_URL")

    cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(
        credential = cred,
        options = {
            "databaseURL" : DATABASE_URL
        }
    )

    ref = db.reference("/Users")
    users = ref.get()

    for user_id in users:
        ref = db.reference(f"/Users/{user_id}")
        data = ref.get()
        ref.update({"utc_offset": data["utcOffset"]})

        ref = db.reference(f"/Users/{user_id}/utcOffset")
        ref.set({})


if __name__ == "__main__":
    main()
