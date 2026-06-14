# 🧭 North Star Change Navigator

**Turning field observations into organizational intelligence.**

## Overview

North Star Change Navigator is a Streamlit-based MVP application designed to help organizations collect field observations from Change Champions and transform them into actionable change intelligence.

## Features

### 1. Portfolio View
- View all active change projects at a glance
- Track champion count, observation count, and average readiness scores
- Visual status indicators (Green/Yellow/Red)
- Portfolio-level metrics and summaries

### 2. Project Dashboard
- Detailed view of individual projects
- Readiness trend charts over time
- Observations by department
- Recent field observation themes
- Key project metrics

### 3. Submit Field Observation
- Quick 2-minute field report form
- Capture overall status (Green/Yellow/Red)
- Readiness score (1-10 scale)
- Three key questions:
  - What are you hearing?
  - What questions are emerging?
  - Anything leadership should know?

### 4. Champions Management
- View all champions by project
- Track champion participation rates
- Add new champions
- Monitor observation activity

### 5. AI Executive Summary
- Generate executive summaries from field observations
- Rule-based analysis (placeholder for future AI integration)
- Identify emerging themes and concerns
- Provide recommended actions
- Track positive signals and areas of concern

### 6. Admin / Seed Data
- Initialize database
- Load sample demo data
- View database statistics

## Quick Start

### Installation

1. Clone or navigate to the project directory:
```bash
cd change_navigator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Your browser should automatically open to `http://localhost:8501`

3. Navigate to **Admin / Seed Data** page and click **"Load Sample Data"** to populate the database with demo data

4. Explore the different pages using the sidebar navigation

## Sample Data

The application includes realistic sample data:
- **3 Projects:**
  - Enterprise Resource Planning (ERP) Upgrade
  - Hybrid Work Policy Rollout
  - Customer Portal Modernization

- **12 Champions** across various departments (Finance, Operations, IT, HR, Marketing, Sales, etc.)

- **30 Field Observations** with realistic change management themes:
  - Training timing concerns
  - Manager capacity issues
  - Approval workflow questions
  - Strong sponsor messaging
  - Change saturation
  - Readiness improvements

## Technical Stack

- **Python 3.8+**
- **Streamlit** - Web application framework
- **SQLite** - Lightweight database
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations

## Database Schema

### Projects
- id, project_name, sponsor_name, start_date, end_date, status

### Champions
- id, project_id, champion_name, department, email, role

### Observations
- id, project_id, champion_id, observation_date, overall_status, readiness_score, what_are_you_hearing, questions_emerging, leadership_should_know

### AI Summaries
- id, project_id, summary_date, summary_text

## File Structure

```
change_navigator/
├── app.py              # Main Streamlit application
├── database.py         # Database functions and queries
├── seed_data.py        # Sample data loader
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── change_navigator.db # SQLite database (created on first run)
```

## Usage Tips

### For Demos
1. Load sample data from Admin page
2. Start with Portfolio View to show all projects
3. Navigate to Project Dashboard to drill into specific projects
4. Show Submit Field Observation to demonstrate the champion experience
5. Generate AI Executive Summary to show intelligence output

### For Real Use
1. Initialize database from Admin page
2. Add your projects manually or modify seed_data.py
3. Add champions for each project
4. Have champions submit regular field observations
5. Generate executive summaries weekly or bi-weekly

## Future Enhancements

This MVP is designed to prove the core concept. Future versions could include:
- User authentication and role-based access
- Integration with live AI APIs (OpenAI, Anthropic, etc.)
- Automated email notifications and nudges
- Micro-learning content delivery
- Multi-tenant support for consulting firms
- Mobile-responsive design improvements
- Export to PDF/PowerPoint
- Integration with Microsoft Teams or Slack
- Advanced analytics and predictive insights

## Design Principles

- **Simple:** Easy to use, minimal learning curve
- **Field-focused:** Centered on champion observations
- **Lightweight:** No complex setup or dependencies
- **Professional:** Clean, dashboard-style interface
- **Demo-ready:** Works out of the box with sample data

## Support

For questions or issues, contact your project administrator.

## License

Internal use only.

---

**Built with ❤️ for Change Management Professionals**
