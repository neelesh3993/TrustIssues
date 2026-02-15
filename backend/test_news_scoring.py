#!/usr/bin/env python3
"""Test credibility scoring for news articles vs Quora"""
from app.routes.analyze import (
    _calculate_ai_likelihood,
    _calculate_manipulation_risk,
    _calculate_credibility_integrated,
    _get_source_credibility_penalty
)

# Sample news article
news_sample = """
Reuters reports that renewable energy capacity increased by 15% in 2024. 
According to the International Energy Agency, global solar installations grew significantly. 
The report cites data from energy ministries across 50 countries. 
This trend reflects growing investment in clean energy infrastructure worldwide.
"""

# Sample Quora answer
quora_sample = """
I think the best way to learn programming is to start with Python. From my perspective, 
Python is one of the most beginner-friendly languages. In my experience, people who start 
with Python tend to have an easier time learning concepts. Maybe you could also try JavaScript 
if you prefer web development. Honestly, I would say that spending at least 2 hours a day on 
coding practice is crucial. In my opinion, this is probably the fastest way to become proficient.
"""

print("=" * 70)
print("CREDIBILITY SCORING COMPARISON")
print("=" * 70)

print("\n📰 NEWS ARTICLE (Reuters):")
print("-" * 70)
ai_score_news = _calculate_ai_likelihood(news_sample)
manip_score_news = _calculate_manipulation_risk(news_sample)
source_penalty_news = _get_source_credibility_penalty(
    "https://www.reuters.com/article")

credibility_news = _calculate_credibility_integrated(
    [], ai_score_news, manip_score_news, source_penalty_news)

print(f"   AI-Generated Likelihood:    {ai_score_news:6.1f}%")
print(f"   Manipulation Risk:          {manip_score_news:6.1f}%")
print(f"   Source Penalty Factor:      {source_penalty_news:6.2f}x")
print(f"   Final Credibility Score:    {credibility_news:6.1f}%")

print("\n💬 QUORA ANSWER:")
print("-" * 70)
ai_score_quora = _calculate_ai_likelihood(quora_sample)
manip_score_quora = _calculate_manipulation_risk(quora_sample)
source_penalty_quora = _get_source_credibility_penalty(
    "https://www.quora.com/Best-way-to-learn")

credibility_quora = _calculate_credibility_integrated(
    [], ai_score_quora, manip_score_quora, source_penalty_quora)

print(f"   AI-Generated Likelihood:    {ai_score_quora:6.1f}%")
print(f"   Manipulation Risk:          {manip_score_quora:6.1f}%")
print(f"   Source Penalty Factor:      {source_penalty_quora:6.2f}x")
print(f"   Final Credibility Score:    {credibility_quora:6.1f}%")

print("\n📊 COMPARISON:")
print("-" * 70)
print(
    f"   Credibility Ratio (News/Quora):  {credibility_news/max(credibility_quora, 0.1):6.2f}x")
print(
    f"   Difference:                      {credibility_news - credibility_quora:6.1f}%")
print(f"\n✓ Assessment:")
print(
    f"   News properly scored higher? {'✓' if credibility_news > credibility_quora else '✗'}")
print(
    f"   News credibility acceptable? {'✓' if credibility_news >= 60 else '✗'} (got {credibility_news:.1f}%)")
print(
    f"   Quora credibility low enough? {'✓' if credibility_quora <= 20 else '✗'} (got {credibility_quora:.1f}%)")
