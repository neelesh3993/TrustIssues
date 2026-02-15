#!/usr/bin/env python3
"""Test improved credibility scoring for Quora answers"""
from app.routes.analyze import (
    _calculate_ai_likelihood,
    _calculate_manipulation_risk,
    _calculate_credibility_integrated,
    _get_source_credibility_penalty
)

# Sample Quora answer
quora_sample = """
I think the best way to learn programming is to start with Python. From my perspective, 
Python is one of the most beginner-friendly languages. In my experience, people who start 
with Python tend to have an easier time learning concepts. Maybe you could also try JavaScript 
if you prefer web development. Honestly, I would say that spending at least 2 hours a day on 
coding practice is crucial. In my opinion, this is probably the fastest way to become proficient. 
Some people claim you can learn it in 3 months, but I doubt that.
"""

print("=" * 70)
print("QUORA ANSWER CREDIBILITY ANALYSIS")
print("=" * 70)

# Calculate individual scores
ai_score = _calculate_ai_likelihood(quora_sample)
manip_score = _calculate_manipulation_risk(quora_sample)
source_penalty = _get_source_credibility_penalty(
    "https://www.quora.com/Best-way-to-learn")

# Calculate with no verification results
credibility = _calculate_credibility_integrated(
    [], ai_score, manip_score, source_penalty)

print(f"\n📊 Individual Scores:")
print(f"   AI-Generated Likelihood:    {ai_score:6.1f}% (expected ~60%)")
print(f"   Manipulation Risk:          {manip_score:6.1f}% (expected ~70%)")
print(
    f"   Source Penalty Factor:      {source_penalty:6.2f}x (0.25 = 75% penalty)")
print(f"\n🎯 Final Credibility Score:     {credibility:6.1f}% (expected ~20%)")

print(f"\n✓ Expected Output Summary:")
print(f"   AI-Generated Content:       60/100 (Moderate)")
print(f"   Credibility:                20/100 (Very Low)")
print(f"   Manipulation Risk:          70/100 (Relatively High)")

print(f"\n📈 Improvement Check:")
print(
    f"   Credibility improving?       {'✓' if credibility < 50 else '✗'} (was 70%, now {credibility:.1f}%)")
print(
    f"   Manipulation improving?      {'✓' if manip_score > 40 else '✗'} (was 15%, now {manip_score:.1f}%)")
