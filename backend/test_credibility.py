#!/usr/bin/env python3
"""Test the new integrated credibility calculation"""
from app.routes.analyze import _calculate_credibility_integrated

# Test 1: Current output values
print("Test 1 - Current output (AI=34%, Manip=1%):")
score1 = _calculate_credibility_integrated([], 34, 1)
print(f"  Result: {score1:.1f}% (was 46%)\n")

# Test 2: Expected values with empty verification
print("Test 2 - Expected values (AI=20%, Manip=30%) - no verification:")
score2 = _calculate_credibility_integrated([], 20, 30)
print(f"  Result: {score2:.1f}%\n")

# Test 3: Good verification with low AI/manipulation
print("Test 3 - Good verification (AI=20%, Manip=30%):")
good_results = [
    {'status': 'verified', 'sources': [
        {'name': 'Reuters'}, {'name': 'New York Times'}]},
    {'status': 'verified', 'sources': [{'name': 'AP News'}]}
]
score3 = _calculate_credibility_integrated(good_results, 20, 30)
print(f"  Result: {score3:.1f}%\n")

# Test 4: High AI generation and manipulation (low credibility scenario)
print("Test 4 - High AI (80%) and High Manipulation (70%):")
score4 = _calculate_credibility_integrated([], 80, 70)
print(f"  Result: {score4:.1f}%\n")

# Test 5: Perfect scenario
print("Test 5 - Perfect scenario (AI=10%, Manip=10%, good verification):")
perfect_results = [
    {'status': 'verified', 'sources': [
        {'name': 'Reuters'}, {'name': 'AP News'}, {'name': 'BBC'}]},
    {'status': 'verified', 'sources': [
        {'name': 'New York Times'}, {'name': 'Guardian'}]},
    {'status': 'verified', 'sources': [{'name': 'Reuters'}, {'name': 'CNN'}]}
]
score5 = _calculate_credibility_integrated(perfect_results, 10, 10)
print(f"  Result: {score5:.1f}%")
