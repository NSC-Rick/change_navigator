import database as db
from datetime import datetime, timedelta
import random

def seed_sample_data():
    """Seed the database with realistic sample data"""
    
    db.clear_all_data()
    
    projects = [
        {
            "project_name": "Enterprise Resource Planning (ERP) Upgrade",
            "project_description": "Comprehensive upgrade to modernize financial systems, streamline operations, and improve reporting capabilities across the organization.",
            "sponsor_name": "Sarah Chen, CFO",
            "project_manager": "David Kim",
            "change_lead": "Maria Santos",
            "start_date": "2024-01-15",
            "go_live_date": "2024-10-01",
            "end_date": "2024-12-31",
            "status": "Active"
        },
        {
            "project_name": "Hybrid Work Policy Rollout",
            "project_description": "Implementation of new flexible work arrangements to support employee wellbeing while maintaining productivity and collaboration.",
            "sponsor_name": "Michael Torres, CHRO",
            "project_manager": "Lisa Anderson",
            "change_lead": "James Wilson",
            "start_date": "2024-03-01",
            "go_live_date": "2024-07-01",
            "end_date": "2024-09-30",
            "status": "Go-Live"
        },
        {
            "project_name": "Customer Portal Modernization",
            "project_description": "Complete redesign of customer-facing portal to improve user experience, self-service capabilities, and mobile accessibility.",
            "sponsor_name": "Jennifer Wu, CTO",
            "project_manager": "Robert Chen",
            "change_lead": "Amanda Martinez",
            "start_date": "2024-02-01",
            "go_live_date": "2024-09-15",
            "end_date": "2024-11-15",
            "status": "Active"
        }
    ]
    
    project_ids = []
    for project in projects:
        project_id = db.add_project(**project)
        project_ids.append(project_id)
    
    champions_data = [
        {"project_id": project_ids[0], "champion_name": "Alex Martinez", "department": "Finance", "location": "Boston", "email": "alex.martinez@company.com", "role": "Senior Analyst", "business_unit": "Corporate Services", "manager": "Sarah Chen", "region": "Northeast"},
        {"project_id": project_ids[0], "champion_name": "Priya Patel", "department": "Operations", "location": "Chicago", "email": "priya.patel@company.com", "role": "Operations Manager", "business_unit": "Operations", "manager": "Michael Torres", "region": "Midwest"},
        {"project_id": project_ids[0], "champion_name": "James Kim", "department": "IT", "location": "Dallas", "email": "james.kim@company.com", "role": "Systems Administrator", "business_unit": "Technology", "manager": "Jennifer Wu", "region": "South"},
        {"project_id": project_ids[0], "champion_name": "Maria Rodriguez", "department": "Procurement", "location": "Boston", "email": "maria.rodriguez@company.com", "role": "Procurement Lead", "business_unit": "Corporate Services", "manager": "Sarah Chen", "region": "Northeast"},
        
        {"project_id": project_ids[1], "champion_name": "David Thompson", "department": "Human Resources", "location": "Chicago", "email": "david.thompson@company.com", "role": "HR Business Partner", "business_unit": "Corporate Services", "manager": "Michael Torres", "region": "Midwest"},
        {"project_id": project_ids[1], "champion_name": "Lisa Chen", "department": "Marketing", "location": "Dallas", "email": "lisa.chen@company.com", "role": "Marketing Director", "business_unit": "Commercial", "manager": "Jennifer Wu", "region": "South"},
        {"project_id": project_ids[1], "champion_name": "Robert Johnson", "department": "Sales", "location": "Boston", "email": "robert.johnson@company.com", "role": "Regional Sales Manager", "business_unit": "Commercial", "manager": "Sarah Chen", "region": "Northeast"},
        {"project_id": project_ids[1], "champion_name": "Emily Davis", "department": "Legal", "location": "Chicago", "email": "emily.davis@company.com", "role": "Compliance Officer", "business_unit": "Corporate Services", "manager": "Michael Torres", "region": "Midwest"},
        
        {"project_id": project_ids[2], "champion_name": "Kevin Lee", "department": "Customer Service", "location": "Dallas", "email": "kevin.lee@company.com", "role": "CS Team Lead", "business_unit": "Commercial", "manager": "Jennifer Wu", "region": "South"},
        {"project_id": project_ids[2], "champion_name": "Amanda White", "department": "Product", "location": "Boston", "email": "amanda.white@company.com", "role": "Product Manager", "business_unit": "Technology", "manager": "Sarah Chen", "region": "Northeast"},
        {"project_id": project_ids[2], "champion_name": "Carlos Santos", "department": "IT", "location": "Chicago", "email": "carlos.santos@company.com", "role": "Developer", "business_unit": "Technology", "manager": "Michael Torres", "region": "Midwest"},
        {"project_id": project_ids[2], "champion_name": "Rachel Green", "department": "Customer Service", "location": "Dallas", "email": "rachel.green@company.com", "role": "Support Specialist", "business_unit": "Commercial", "manager": "Jennifer Wu", "region": "South"},
    ]
    
    champion_ids = {}
    for champion in champions_data:
        champion_id = db.add_champion(**champion)
        champion_ids[champion["champion_name"]] = champion_id
    
    observations = [
        {
            "project_id": project_ids[0],
            "champion_name": "Alex Martinez",
            "overall_status": "Yellow",
            "readiness_score": 6,
            "what_are_you_hearing": "Team is concerned about training timing. Many feel it's too close to quarter-end close. Finance team is already stretched thin with regular duties.",
            "questions_emerging": "Can we push training to early next quarter? Will there be hands-on practice time or just presentations?",
            "leadership_should_know": "Finance manager workload is a real concern. May need to adjust timeline or provide temporary support."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "Priya Patel",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Operations team is excited about the new approval workflows. They see this as a major efficiency gain. Strong sponsor messaging from CFO has helped.",
            "questions_emerging": "How will legacy data migration work? Will we have parallel systems during transition?",
            "leadership_should_know": "Operations is ready to go. They're actually asking to be early adopters."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "James Kim",
            "overall_status": "Yellow",
            "readiness_score": 7,
            "what_are_you_hearing": "IT team understands the technical changes but worried about support volume during go-live. Current ticket queue is already high.",
            "questions_emerging": "Will there be dedicated ERP support staff or will this fall on general IT helpdesk? What's the escalation path?",
            "leadership_should_know": "Need to clarify support model. IT is willing but needs resources."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "Maria Rodriguez",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Procurement team has been asking for better vendor management tools for years. They're very supportive and engaged.",
            "questions_emerging": "Can we get early access to test with a few key vendors? Want to make sure integrations work smoothly.",
            "leadership_should_know": "Procurement is a strong ally. Consider them for pilot group."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "Alex Martinez",
            "overall_status": "Yellow",
            "readiness_score": 7,
            "what_are_you_hearing": "Follow-up: After discussing with team, they're more comfortable if training is recorded so they can review later. Still concerned about timing but willing to make it work.",
            "questions_emerging": "Will training materials be available on-demand? Can we get a sandbox environment to practice?",
            "leadership_should_know": "Flexibility on training format would help. Team is coming around."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "Priya Patel",
            "overall_status": "Green",
            "readiness_score": 9,
            "what_are_you_hearing": "Operations did a walkthrough of the new system. Team is impressed. They're already identifying additional use cases beyond the original scope.",
            "questions_emerging": "Can we document best practices as we go? Want to capture lessons learned for other departments.",
            "leadership_should_know": "Operations could be great advocates. Consider having them present at all-hands."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "James Kim",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "IT got clarity on support model. Dedicated ERP support team will be available for first 90 days. This addresses our main concern.",
            "questions_emerging": "What happens after 90 days? Will we transition to BAU support or extend dedicated team?",
            "leadership_should_know": "IT is now green light. Support plan made the difference."
        },
        {
            "project_id": project_ids[0],
            "champion_name": "Maria Rodriguez",
            "overall_status": "Green",
            "readiness_score": 9,
            "what_are_you_hearing": "Procurement completed pilot testing with three vendors. System works great. Vendors also appreciate the improved portal.",
            "questions_emerging": "Should we communicate the change to all vendors or just as they encounter it?",
            "leadership_should_know": "Pilot was a success. Procurement is ready for full rollout."
        },
        
        {
            "project_id": project_ids[1],
            "champion_name": "David Thompson",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "HR team is getting positive feedback on the hybrid policy. Employees appreciate the flexibility. Managers are asking good questions about expectations.",
            "questions_emerging": "How do we handle performance reviews for hybrid workers? Are there metrics we should track?",
            "leadership_should_know": "Overall sentiment is positive. Need to develop manager guidance on hybrid team management."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Lisa Chen",
            "overall_status": "Yellow",
            "readiness_score": 6,
            "what_are_you_hearing": "Marketing team is split. Creative team loves remote flexibility. Events team needs to be on-site more often and feels the policy doesn't fit their reality.",
            "questions_emerging": "Can departments customize the policy based on role requirements? One-size-fits-all may not work.",
            "leadership_should_know": "May need role-based flexibility within the framework. Events team feels overlooked."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Robert Johnson",
            "overall_status": "Red",
            "readiness_score": 4,
            "what_are_you_hearing": "Sales team is frustrated. They're already mostly remote but new policy adds bureaucracy with required office days. Feels like a step backward.",
            "questions_emerging": "Why are we applying office requirements to roles that have always been field-based? Can we exempt sales?",
            "leadership_should_know": "Sales is actively resistant. This could impact morale and retention. Need to address quickly."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Emily Davis",
            "overall_status": "Yellow",
            "readiness_score": 7,
            "what_are_you_hearing": "Legal team wants more clarity on compliance implications. Concerned about data security with increased remote work.",
            "questions_emerging": "What are the security protocols? Do we need updated policies for remote document handling?",
            "leadership_should_know": "Legal needs security framework documentation. Valid compliance concerns."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "David Thompson",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "HR published manager toolkit. Getting great feedback. Managers feel more equipped to handle hybrid teams now.",
            "questions_emerging": "Can we do a manager roundtable to share best practices?",
            "leadership_should_know": "Manager toolkit was well-received. Consider ongoing manager community of practice."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Lisa Chen",
            "overall_status": "Green",
            "readiness_score": 7,
            "what_are_you_hearing": "After clarification that teams can customize within guidelines, Marketing is more positive. Events team will have different requirements than Creative.",
            "questions_emerging": "How do we document team-specific arrangements? Want to ensure consistency.",
            "leadership_should_know": "Flexibility within framework is working. Marketing is back on board."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Robert Johnson",
            "overall_status": "Yellow",
            "readiness_score": 6,
            "what_are_you_hearing": "Sales leadership met with CHRO. Some progress. Field sales will be exempt from office requirements. Inside sales still has questions.",
            "questions_emerging": "What's the definition of field vs inside sales for policy purposes?",
            "leadership_should_know": "Sales is moving from red to yellow. Still need clear role definitions."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Emily Davis",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Legal received security protocols document. Concerns addressed. IT has implemented additional safeguards for remote work.",
            "questions_emerging": "Should we require annual security training refresh?",
            "leadership_should_know": "Legal is satisfied with security measures. Recommend annual training."
        },
        
        {
            "project_id": project_ids[2],
            "champion_name": "Kevin Lee",
            "overall_status": "Green",
            "readiness_score": 9,
            "what_are_you_hearing": "Customer Service team tested the new portal. It's so much easier to navigate. Customers are going to love this. Team is excited to launch.",
            "questions_emerging": "When can we start promoting it to customers? Should we do a soft launch first?",
            "leadership_should_know": "CS team is enthusiastic. They see this as a game-changer for customer experience."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Amanda White",
            "overall_status": "Yellow",
            "readiness_score": 7,
            "what_are_you_hearing": "Product team loves the new features but concerned about customer communication. Need clear messaging about what's changing and why.",
            "questions_emerging": "Do we have a communication plan? What if customers resist the change?",
            "leadership_should_know": "Product is supportive but wants strong change communication strategy."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Carlos Santos",
            "overall_status": "Yellow",
            "readiness_score": 6,
            "what_are_you_hearing": "Development team is behind schedule on mobile optimization. Desktop version is ready but mobile needs another sprint.",
            "questions_emerging": "Should we launch desktop-only first or wait for mobile? What percentage of users are mobile-first?",
            "leadership_should_know": "Technical delay on mobile. Need decision on phased vs simultaneous launch."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Rachel Green",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Support team completed training on new portal. They're comfortable with the changes and ready to help customers navigate.",
            "questions_emerging": "Will we have extra support coverage during launch week in case of high volume?",
            "leadership_should_know": "Support team is prepared. Recommend extra coverage for launch week."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Kevin Lee",
            "overall_status": "Green",
            "readiness_score": 9,
            "what_are_you_hearing": "CS created video tutorials for common customer tasks. These will help with adoption. Team went above and beyond.",
            "questions_emerging": "Can we embed these videos in the portal itself for just-in-time help?",
            "leadership_should_know": "CS team created excellent training content. Consider embedding in portal."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Amanda White",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Product finalized communication plan. Email campaign, in-app notifications, and FAQ ready to go. Messaging focuses on benefits.",
            "questions_emerging": "Should we do a beta group with select customers first?",
            "leadership_should_know": "Communication plan is solid. Beta group could reduce risk."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Carlos Santos",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Development team completed mobile optimization. All platforms are ready. Final testing in progress.",
            "questions_emerging": "What's the rollback plan if we discover critical issues post-launch?",
            "leadership_should_know": "Mobile is complete. Recommend documenting rollback procedures."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Rachel Green",
            "overall_status": "Green",
            "readiness_score": 9,
            "what_are_you_hearing": "Support team is staffed up for launch week. Extra coverage approved. Team is confident and ready.",
            "questions_emerging": "How long should we maintain elevated support levels?",
            "leadership_should_know": "Support is fully prepared. Monitor volume to determine when to scale back."
        },
        
        {
            "project_id": project_ids[0],
            "champion_name": "Alex Martinez",
            "overall_status": "Green",
            "readiness_score": 8,
            "what_are_you_hearing": "Finance team completed training. Sandbox practice time was valuable. Team feels ready for go-live.",
            "questions_emerging": "Will we have a go-live checklist? Want to make sure nothing is missed.",
            "leadership_should_know": "Finance has turned the corner. Training approach worked well."
        },
        {
            "project_id": project_ids[1],
            "champion_name": "Robert Johnson",
            "overall_status": "Green",
            "readiness_score": 7,
            "what_are_you_hearing": "Sales team received role clarity. Field sales exempt, inside sales has flexibility. Team is satisfied with the outcome.",
            "questions_emerging": "Can we get this documented in the official policy?",
            "leadership_should_know": "Sales issue is resolved. Recommend updating policy documentation."
        },
        {
            "project_id": project_ids[2],
            "champion_name": "Kevin Lee",
            "overall_status": "Green",
            "readiness_score": 10,
            "what_are_you_hearing": "Beta launch with 50 customers was a huge success. Feedback is overwhelmingly positive. Customers love the new interface.",
            "questions_emerging": "Can we accelerate the full launch timeline?",
            "leadership_should_know": "Beta exceeded expectations. Team recommends moving forward with full launch."
        },
    ]
    
    base_date = datetime.now() - timedelta(days=45)
    
    for i, obs in enumerate(observations):
        observation_date = base_date + timedelta(days=i * 1.5)
        
        champion_id = champion_ids[obs["champion_name"]]
        
        db.add_observation(
            project_id=obs["project_id"],
            champion_id=champion_id,
            overall_status=obs["overall_status"],
            readiness_score=obs["readiness_score"],
            what_are_you_hearing=obs["what_are_you_hearing"],
            questions_emerging=obs["questions_emerging"],
            leadership_should_know=obs["leadership_should_know"]
        )
    
    print("✅ Sample data loaded successfully!")
    print(f"   - {len(projects)} projects")
    print(f"   - {len(champions_data)} champions")
    print(f"   - {len(observations)} observations")

if __name__ == "__main__":
    db.init_database()
    seed_sample_data()
