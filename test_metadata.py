"""
Test script to verify metadata collection in response data
"""

import time
import random

# Sample data to test
test_emotion = "행복한"
test_choices = ["행복한", "슬픈", "화난", "놀란", "역겨움"]
test_stimulus_id = "1ekLwSmsQtA5KG9UKRz2cbtujMHCB8cAo"

# Simulate metadata collection
stimulus_timestamp = int(time.time() * 1000)
print(f"Stimulus timestamp (ms): {stimulus_timestamp}")

# Simulate user response after 2.5 seconds
time.sleep(2.5)
reaction_time = 2.5  # seconds
response_timestamp = int(time.time() * 1000)

# Create response data with metadata
response_data = {
    'trial_number': 1,
    'experiment_type': 1,
    'stimulus_id': test_stimulus_id,
    'correct_emotion': test_emotion,
    'choices': ', '.join(test_choices),
    'selected_emotion': test_emotion,
    'is_correct': True,
    'reaction_time': reaction_time,
    'reaction_time_ms': int(reaction_time * 1000),
    'stimulus_timestamp': stimulus_timestamp,
    'response_timestamp': response_timestamp,
    'is_practice': False
}

print("\nResponse data with metadata:")
for key, value in response_data.items():
    print(f"  {key}: {value}")

print("\nTimestamp difference (response - stimulus):", response_timestamp - stimulus_timestamp, "ms")
print("This should be approximately equal to reaction_time_ms:", response_data['reaction_time_ms'], "ms")