from data_collection.mastodon_api import search_mastodon_account, get_mastodon_posts


def main() -> None:
    handle = input("Enter Mastodon handle (e.g. xgh@mastodon.social): ").strip()

    account = search_mastodon_account(handle)

    if account is None:
        print("No Mastodon account found.")
        return

    print("\n=== Mastodon Profile ===")
    print(account)

    posts = get_mastodon_posts(account["id"], limit=5)

    print("\n=== Recent Posts ===")
    if not posts:
        print("No recent posts found.")
    else:
        for post in posts:
            print("-", post[:120])


if __name__ == "__main__":
    main()