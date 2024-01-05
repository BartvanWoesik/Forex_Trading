import unittest
import requests
import json


class FlaskAPITestCase(unittest.TestCase):
    def setUp(self):
        # Set up the base URL for the Flask app
        self.base_url = "http://127.0.0.1:5000"

    def test_predict_endpoint(self):
        # Test the '/predict' endpoint

        # Sample input data for testing
        with open("deploy/testdf.json", "r") as file:
            input_data = json.load(file)

        url = f"{self.base_url}/predict"

        # Make a POST request to the endpoint with the sample input data
        response = requests.post(
            url,
            json=input_data,
        )

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the response contains the 'predictions' key
        self.assertIn("predictions", response.json())

        # Optionally, check the format or type of the response data
        predictions = response.json()["predictions"]
        self.assertIsInstance(predictions, list)

        print(predictions)


if __name__ == "__main__":
    unittest.main()
