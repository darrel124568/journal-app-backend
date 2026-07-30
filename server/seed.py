from faker import Faker

from config import app
from models import JournalEntry, User, db


fake = Faker()


def seed_database(user_count=10, entries_per_user=5):
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = []
        entries = []
        for _ in range(user_count):
            user = User(username=fake.unique.user_name())
            user.password_hash = "password123"
            users.append(user)

        db.session.add_all(users)
        db.session.flush()

        for user in users:
            for _ in range(entries_per_user):
                entries.append(
                    JournalEntry(
                        title=fake.sentence(nb_words=6),
                        content=fake.paragraph(nb_sentences=4),
                        year_created=fake.date_between(start_date="-2y", end_date="today"),
                        user_id=user.id,
                    )
                )

        db.session.add_all(entries)
        db.session.commit()


if __name__ == "__main__":
    seed_database()
