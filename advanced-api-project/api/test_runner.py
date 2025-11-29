"""
Custom test runner configuration for the Advanced API Project.
"""

from django.test.runner import DiscoverRunner

class CustomTestRunner(DiscoverRunner):
    """
    Custom test runner with additional configuration options.
    """
    
    def setup_test_environment(self, **kwargs):
        """
        Set up the test environment.
        """
        super().setup_test_environment(**kwargs)
        # Additional test environment setup can go here
    
    def teardown_test_environment(self, **kwargs):
        """
        Tear down the test environment.
        """
        super().teardown_test_environment(**kwargs)
        # Additional test environment teardown can go here