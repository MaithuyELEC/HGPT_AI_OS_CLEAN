from hgpt_ai_os.database import DatabaseEngine, create_tables
from hgpt_ai_os.database.repository import Repository


def print_users(repo):
    print("\n===== USERS =====")
    for user in repo.get_users():
        print(dict(user))


def main():
    engine = DatabaseEngine()

    create_tables(engine)

    repo = Repository(engine)

    # CREATE
    # repo.create_user(
#     username="admin",
#     fullname="Mai Thuy",
#     role="Chief Engineer"
# )

    print_users(repo)

    # READ
    user = repo.get_user(1)
    print("\nREAD:")
    print(dict(user))

    # UPDATE
    repo.update_user(
        1,
        "Mai Thuy ELEC",
        "AI Chief Engineer"
    )

    print("\nAFTER UPDATE")
    print_users(repo)

    # DELETE (tạm thời comment)
    # repo.delete_user(1)
    # print("\nAFTER DELETE")
    # print_users(repo)

    engine.close()


if __name__ == "__main__":
    main()