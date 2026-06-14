"""
Summary Utilities - Shared functions for generating executive summaries
"""
from datetime import datetime

def generate_placeholder_summary(observations_df, project_name):
    """Generate a rule-based summary from observations"""
    
    avg_readiness = observations_df['readiness_score'].mean()
    total_obs = len(observations_df)
    
    status_counts = observations_df['overall_status'].value_counts()
    green_count = status_counts.get('Green', 0)
    yellow_count = status_counts.get('Yellow', 0)
    red_count = status_counts.get('Red', 0)
    
    recent_obs = observations_df.head(10)
    
    all_hearing = ' '.join(recent_obs['what_are_you_hearing'].dropna().tolist())
    all_questions = ' '.join(recent_obs['questions_emerging'].dropna().tolist())
    all_leadership = ' '.join(recent_obs['leadership_should_know'].dropna().tolist())
    
    concerns = []
    if 'training' in all_hearing.lower():
        concerns.append("training timing and delivery")
    if 'workload' in all_hearing.lower() or 'capacity' in all_hearing.lower():
        concerns.append("team capacity and workload")
    if 'manager' in all_hearing.lower():
        concerns.append("manager readiness and support")
    if 'timeline' in all_hearing.lower() or 'timing' in all_hearing.lower():
        concerns.append("timeline concerns")
    
    positive_signals = []
    if 'excited' in all_hearing.lower() or 'positive' in all_hearing.lower():
        positive_signals.append("Strong enthusiasm and engagement")
    if 'ready' in all_hearing.lower():
        positive_signals.append("Teams expressing readiness")
    if 'sponsor' in all_hearing.lower() and 'strong' in all_hearing.lower():
        positive_signals.append("Effective sponsor messaging")
    if 'support' in all_hearing.lower():
        positive_signals.append("Willingness to support the change")
    
    if avg_readiness >= 8:
        readiness_level = "strong"
        readiness_desc = "The organization is demonstrating high readiness for this change."
    elif avg_readiness >= 6:
        readiness_level = "moderate"
        readiness_desc = "The organization shows moderate readiness with some areas requiring attention."
    else:
        readiness_level = "developing"
        readiness_desc = "Readiness is still developing and requires focused intervention."
    
    summary = f"""## Executive Summary: {project_name}

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}

**Overall Readiness:** {avg_readiness:.1f}/10 ({readiness_level})

{readiness_desc}

### Key Metrics
- **Total Field Observations:** {total_obs}
- **Status Distribution:** {green_count} Green, {yellow_count} Yellow, {red_count} Red
- **Average Readiness Score:** {avg_readiness:.1f}/10

### Emerging Themes

Based on recent field observations from Change Champions:

"""
    
    if concerns:
        summary += "**Areas of Concern:**\n"
        for i, concern in enumerate(concerns[:4], 1):
            summary += f"{i}. {concern.capitalize()}\n"
        summary += "\n"
    
    if positive_signals:
        summary += "**Positive Signals:**\n"
        for i, signal in enumerate(positive_signals[:4], 1):
            summary += f"{i}. {signal}\n"
        summary += "\n"
    
    summary += "### Recommended Actions\n\n"
    
    if avg_readiness < 6:
        summary += "1. **Immediate:** Conduct stakeholder listening sessions to address concerns\n"
        summary += "2. **This Week:** Publish FAQ addressing recurring questions\n"
        summary += "3. **Ongoing:** Increase champion touchpoints and support\n"
    elif avg_readiness < 8:
        summary += "1. **This Week:** Address specific concerns raised in field observations\n"
        summary += "2. **Next Week:** Reinforce key messages through leadership\n"
        summary += "3. **Ongoing:** Continue champion engagement and feedback loops\n"
    else:
        summary += "1. **Leverage Momentum:** Identify and amplify success stories\n"
        summary += "2. **Sustain Engagement:** Maintain regular champion touchpoints\n"
        summary += "3. **Prepare for Launch:** Ensure support resources are ready\n"
    
    summary += "\n### Champion Insights\n\n"
    summary += f"Champions are actively engaged with {total_obs} field observations submitted. "
    
    if green_count > yellow_count + red_count:
        summary += "The majority of signals are positive, indicating strong momentum."
    elif red_count > 0:
        summary += "Some areas are showing resistance or concern that require immediate attention."
    else:
        summary += "Mixed signals suggest the need for targeted interventions in specific areas."
    
    summary += "\n\n---\n*This summary was generated from field observations collected through the North Star Change Navigator platform.*"
    
    return summary
