from sqlalchemy.orm import Session

from app.database.models import UserModel


class UserRepository:

    def create(
        self,
        db: Session,
        username: str,
        email: str,
        password_hash: str,
        role: str,
    ):

        db_user = UserModel(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        )

        db.add(db_user)

        db.commit()

        db.refresh(db_user)

        return db_user

    def get_by_username(self, db: Session, username: str):

        return (
            db.query(UserModel)
            .filter(UserModel.username == username)
            .first()
        )

    def get_by_email(self, db: Session, email: str):

        return (
            db.query(UserModel)
            .filter(UserModel.email == email)
            .first()
        )

    def get_by_id(self, db: Session, user_id: int):

        return (
            db.query(UserModel)
            .filter(UserModel.id == user_id)
            .first()
        )


user_repository = UserRepository()
