#!/usr/bin/env python3
"""
Basic tests for the network stability monitoring application.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime
import pytz

# Set up environment for testing
os.environ['MOCK_PING'] = 'true'
os.environ['DATA_DIR'] = tempfile.mkdtemp()

from app import app, ping_host, save_ping_result, get_today_filename, cleanup_old_files


class TestNetworkStabilityApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_ping_mock_mode(self):
        """Test ping function in mock mode."""
        result = ping_host('8.8.8.8')
        # Should return a float (mock response time) or None (mock failure)
        self.assertTrue(result is None or isinstance(result, float))
    
    def test_save_and_load_ping_result(self):
        """Test saving and loading ping results."""
        tz = pytz.timezone('UTC')
        timestamp = datetime.now(tz)
        response_time = 50.5
        
        # Save a ping result
        save_ping_result(response_time, timestamp)
        
        # Check if file was created and contains data
        filename = get_today_filename()
        self.assertTrue(os.path.exists(filename))
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['response_time'], response_time)
        self.assertTrue(data[0]['success'])
    
    def test_web_routes(self):
        """Test web application routes."""
        # Test main page
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Network Stability Monitor', response.data)
        
        # Test API endpoints
        response = self.app.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_pings', data)
        
        response = self.app.get('/api/data')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
    
    def test_today_filename_generation(self):
        """Test that filename generation includes date."""
        filename = get_today_filename()
        today = datetime.now().strftime('%Y-%m-%d')
        self.assertIn(today, filename)
        self.assertTrue(filename.endswith('.json'))


if __name__ == '__main__':
    unittest.main()