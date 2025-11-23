#!/usr/bin/env python3
"""Test module for GithubOrgClient.

"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient.

    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct value."""
        test_payload = {"name": org_name}
        mock_get_json.return_value = test_payload
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, test_payload)

    def test_public_repos_url(self):
        """Test GithubOrgClient._public_repos_url returns correct value."""
        test_payload = {
            "repos_url": "https://api.github.com/orgs/google/repos"}
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_payload
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test GithubOrgClient.public_repos returns correct list."""
        test_payload = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
            {"name": "repo3"},
        ]
        test_url = "https://api.github.com/orgs/google/repos"
        mock_get_json.return_value = test_payload
        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_repos_url:
            mock_repos_url.return_value = test_url
            client = GithubOrgClient("google")
            result = client.public_repos()
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(result, expected_repos)
            mock_get_json.assert_called_once_with(test_url)
            mock_repos_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license returns correct value."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(("org_payload", "repos_payload", "expected_repos",
                      "apache2_repos"), TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test class for GithubOrgClient.

    """
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        def get_payload(url):
            """Return payload based on URL."""
            if url == "https://api.github.com/orgs/google":
                return cls.org_payload
            elif url == cls.org_payload["repos_url"]:
                return cls.repos_payload
            return None

        cls.get_patcher = patch('utils.requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Side effect for requests.get."""
            mock_response = Mock()
            mock_response.json.return_value = get_payload(url)
            return mock_response

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test GithubOrgClient.public_repos returns expected repos."""
        client = GithubOrgClient("google")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test GithubOrgClient.public_repos with license filter."""
        client = GithubOrgClient("google")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)
