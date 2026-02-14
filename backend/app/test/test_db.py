from app.database.cache import check_cache, store_cache


def run_test():
    test_text = "The sky is blue"
    fake_response = {
        "credibility_score": 90,
        "summary": "Test response"
    }

    print("Checking cache (should be empty):")
    print(check_cache(test_text))

    print("\nStoring test data...")
    store_cache(test_text, fake_response)

    print("\nChecking cache again:")
    print(check_cache(test_text))


if __name__ == "__main__":
    run_test()
