from app import app
from ai.feature_extraction import extract_user_features


with app.app_context():

    features = extract_user_features()

    print("\nExtracted User Features\n")

    for user in features:
        print(user)