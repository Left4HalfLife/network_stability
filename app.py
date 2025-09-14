#!/usr/bin/env python3
"""
Network Stability Monitoring Flask Application

Monitors internet connectivity by pinging 8.8.8.8 every minute and displays
the results in a web-based graph interface.
"""

import os
import json
import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, jsonify
import pytz

# Configuration
TIMEZONE = os.getenv('TIMEZONE', 'UTC')
CLEANUP_DAYS = int(os.getenv('CLEANUP_DAYS', '30'))
DATA_DIR = os.getenv('DATA_DIR', './data')
PING_INTERVAL = 60  # seconds
PING_TARGET = '8.8.8.8'

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Ensure data directory exists
Path(DATA_DIR).mkdir(exist_ok=True)


def get_today_filename():
    """Get filename for today's data based on configured timezone."""
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).strftime('%Y-%m-%d')
    return os.path.join(DATA_DIR, f'ping_data_{today}.json')


def cleanup_old_files():
    """Remove data files older than CLEANUP_DAYS."""
    try:
        cutoff_date = datetime.now() - timedelta(days=CLEANUP_DAYS)
        data_path = Path(DATA_DIR)
        
        for file_path in data_path.glob('ping_data_*.json'):
            try:
                # Extract date from filename
                date_str = file_path.stem.replace('ping_data_', '')
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                if file_date < cutoff_date:
                    file_path.unlink()
                    app.logger.info(f"Cleaned up old file: {file_path}")
            except ValueError:
                # Skip files that don't match expected format
                continue
    except Exception as e:
        app.logger.error(f"Error during cleanup: {e}")


def ping_host(host):
    """
    Ping a host and return the response time in milliseconds.
    Returns None if ping fails.
    """
    # Check if we're in mock mode for testing environments
    mock_mode = os.getenv('MOCK_PING', 'false').lower() == 'true'
    
    if mock_mode:
        # Generate mock data for testing
        import random
        if random.random() < 0.95:  # 95% success rate
            return round(random.uniform(10, 100), 2)
        else:
            return None
    
    try:
        # Use ping command with 1 packet and 5 second timeout
        result = subprocess.run(
            ['ping', '-c', '1', '-W', '5', host],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extract time from ping output
            output = result.stdout
            for line in output.split('\n'):
                if 'time=' in line:
                    time_part = line.split('time=')[1].split()[0]
                    return float(time_part)
        return None
    except Exception as e:
        app.logger.error(f"Ping error: {e}")
        return None


def save_ping_result(response_time, timestamp):
    """Save ping result to today's data file."""
    filename = get_today_filename()
    
    # Load existing data or create new
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []
    
    # Add new entry
    entry = {
        'timestamp': timestamp.isoformat(),
        'response_time': response_time,
        'success': response_time is not None
    }
    data.append(entry)
    
    # Save updated data
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def ping_worker():
    """Background worker to ping every minute."""
    app.logger.info("Starting ping worker")
    
    while True:
        try:
            tz = pytz.timezone(TIMEZONE)
            timestamp = datetime.now(tz)
            response_time = ping_host(PING_TARGET)
            
            save_ping_result(response_time, timestamp)
            
            status = f"OK ({response_time}ms)" if response_time else "FAILED"
            app.logger.info(f"Ping {PING_TARGET}: {status}")
            
            # Cleanup old files once per day (at first ping of the day)
            if timestamp.hour == 0 and timestamp.minute < 2:
                cleanup_old_files()
                
        except Exception as e:
            app.logger.error(f"Error in ping worker: {e}")
        
        time.sleep(PING_INTERVAL)


@app.route('/')
def index():
    """Main page displaying the network stability graph."""
    return render_template('index.html', 
                         timezone=TIMEZONE, 
                         cleanup_days=CLEANUP_DAYS,
                         target=PING_TARGET)


@app.route('/api/data')
def get_data():
    """API endpoint to get today's ping data."""
    filename = get_today_filename()
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify([])


@app.route('/api/stats')
def get_stats():
    """API endpoint to get basic statistics."""
    filename = get_today_filename()
    
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        if not data:
            return jsonify({
                'total_pings': 0,
                'successful_pings': 0,
                'failed_pings': 0,
                'success_rate': 0,
                'avg_response_time': 0
            })
        
        successful = [entry for entry in data if entry['success']]
        failed = [entry for entry in data if not entry['success']]
        
        avg_response_time = 0
        if successful:
            avg_response_time = sum(entry['response_time'] for entry in successful) / len(successful)
        
        stats = {
            'total_pings': len(data),
            'successful_pings': len(successful),
            'failed_pings': len(failed),
            'success_rate': (len(successful) / len(data)) * 100 if data else 0,
            'avg_response_time': round(avg_response_time, 2)
        }
        
        return jsonify(stats)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({
            'total_pings': 0,
            'successful_pings': 0,
            'failed_pings': 0,
            'success_rate': 0,
            'avg_response_time': 0
        })


if __name__ == '__main__':
    # Start ping worker in background thread
    ping_thread = threading.Thread(target=ping_worker, daemon=True)
    ping_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)