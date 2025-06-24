"""
Instagram Next Post Recommender - Multi-Agent System
Analyzes your existing content and recommends specific next story + feed post
"""

import os
from autogen import ConversableAgent, GroupChat, GroupChatManager, LLMConfig
from Database import RAGDatabase
import json
from datetime import datetime, timedelta
import typer
from typing import Dict, List

class InstagramPostRecommender:
    def __init__(self):
        self.rag_db = RAGDatabase()
        
        # Configure LLM
        self.llm_config = LLMConfig(
            api_type="openai", 
            model="gpt-4o-mini",
            temperature=0.7
        )
        
        self._setup_agents()
        self._setup_group_chat()
    
    def _setup_agents(self):
        """Create specialized agents for story and feed recommendations"""
        
        # Story Strategist - Focuses on Instagram Stories
        story_agent_message = """You are an Instagram Stories Specialist.

Your role:
- Analyze story posting patterns and engagement
- Recommend specific story content (behind-scenes, polls, Q&A, quick tips, teasers)
- Suggest story sequences that drive engagement and feed traffic
- Focus on timely, authentic, and interactive story ideas
- Consider story highlights and save-worthy content

Always provide specific, actionable story recommendations with clear creative direction."""

        # Feed Post Strategist - Focuses on main feed content  
        feed_agent_message = """You are an Instagram Feed Content Specialist.

Your role:
- Analyze feed posting patterns, engagement, and content performance
- Recommend specific feed post content (satisfying videos, educational carousels, promotions, transformations)
- Suggest optimal posting timing based on historical data
- Focus on high-engagement, algorithm-friendly content
- Balance different content types for optimal feed strategy

Provide detailed feed post recommendations with hashtag strategies and caption directions."""

        # Content Coordinator - Ensures story and feed work together
        coordinator_message = """You are a Content Coordination Specialist.

Your role:
- Ensure story and feed recommendations work together strategically
- Create content synergy (story teases feed post, feed drives to story highlights)
- Balance immediate engagement (stories) with long-term reach (feed)
- Identify cross-promotion opportunities between story and feed
- Make final recommendations that maximize overall account growth

End with "FINAL RECOMMENDATION:" when you have the complete next-post strategy."""

        with self.llm_config:
            self.story_agent = ConversableAgent(
                name="story_specialist",
                system_message=story_agent_message,
                description="Analyzes and recommends Instagram Story content based on engagement patterns."
            )
            
            self.feed_agent = ConversableAgent(
                name="feed_specialist", 
                system_message=feed_agent_message,
                description="Analyzes and recommends Instagram feed posts based on performance data."
            )
            
            self.coordinator = ConversableAgent(
                name="content_coordinator",
                system_message=coordinator_message,
                description="Coordinates story and feed strategy for maximum synergy and engagement.",
                is_termination_msg=lambda x: "FINAL RECOMMENDATION:" in (x.get("content", "") or "").upper()
            )

    def _setup_group_chat(self):
        """Setup group chat for story + feed coordination"""
        self.groupchat = GroupChat(
            agents=[self.coordinator, self.story_agent, self.feed_agent],
            speaker_selection_method="auto",
            messages=[],
            max_round=8
        )
        
        with self.llm_config:
            self.manager = GroupChatManager(
                name="content_recommendation_manager",
                groupchat=self.groupchat,
                llm_config=self.llm_config
            )

    def get_next_post_recommendations(self, context: str = ""):
        """Get specific recommendations for next story and feed post"""
        
        # Get comprehensive account analysis
        analysis = self.rag_db.get_content_analysis()
        recent_posts = self.rag_db.get_recent_posts(10)
        high_performers = self.rag_db.get_high_engagement_posts(min_engagement=1000)
        
        if not analysis or analysis.get('total_posts', 0) == 0:
            return " No posts in database. Add your existing posts first to get recommendations."

        # Calculate content gaps and timing
        content_gaps = self._analyze_content_gaps(recent_posts)
        posting_rhythm = self._analyze_posting_rhythm(recent_posts)
        
        # Prepare briefing for agents
        briefing_data = {
            "account_overview": {
                "total_posts": analysis.get('total_posts', 0),
                "avg_engagement": analysis.get('avg_engagement', 0),
                "content_types": analysis.get('type_distribution', {}),
                "top_performing_type": max(
                    analysis.get('avg_engagement_by_type', {}).items(), 
                    key=lambda x: x[1], default=('satisfying_video', 0)
                )[0]
            },
            "recent_activity": [
                {
                    "type": post['type'],
                    "engagement": post['engagement'],
                    "days_ago": (datetime.now() - datetime.strptime(post['date_posted'], '%Y-%m-%d')).days,
                    "caption_preview": post['caption'][:80] + "..."
                } for post in recent_posts[:5]
            ],
            "top_performers": [
                {
                    "type": post['type'],
                    "engagement": post['engagement'],
                    "hashtags": post['hashtags'][:3],
                    "caption_preview": post['caption'][:60] + "..."
                } for post in high_performers[:3]
            ],
            "content_gaps": content_gaps,
            "posting_rhythm": posting_rhythm,
            "best_hashtags": list(analysis.get('best_performing_hashtags', {}).keys())[:5]
        }

        briefing = f"""
NEXT POST RECOMMENDATION BRIEFING
================================

Context: {context or 'Regular content planning'}

ACCOUNT DATA:
{json.dumps(briefing_data, indent=2)}

TASK: Recommend the NEXT specific story and feed post to maximize engagement.

Story Specialist: Analyze recent stories patterns and recommend next story content
Feed Specialist: Analyze feed performance and recommend next feed post  
Coordinator: Ensure both recommendations work together strategically

Focus on:
1. What specific content to post next (not general strategy)
2. Timing based on posting rhythm
3. How story and feed can work together
4. Actionable creative direction
"""

        # Start agent collaboration
        chat_result = self.coordinator.initiate_chat(
            recipient=self.manager,
            message=briefing
        )
        
        return self._extract_recommendations(chat_result)

    def _analyze_content_gaps(self, recent_posts: List[Dict]) -> Dict:
        """Identify what content types are missing recently"""
        if not recent_posts:
            return {"gap_analysis": "No recent posts to analyze"}
            
        recent_types = [post['type'] for post in recent_posts[:7]]  # Last 7 posts
        type_counts = {t: recent_types.count(t) for t in set(recent_types)}
        
        all_types = ['satisfying_video', 'promotion', 'educational', 'behind_scenes']
        missing_types = [t for t in all_types if t not in recent_types]
        
        return {
            "recent_content_mix": type_counts,
            "missing_content_types": missing_types,
            "overused_types": [t for t, count in type_counts.items() if count >= 3]
        }

    def _analyze_posting_rhythm(self, recent_posts: List[Dict]) -> Dict:
        """Analyze posting frequency and timing patterns"""
        if len(recent_posts) < 2:
            return {"rhythm": "Not enough posts to analyze rhythm"}
            
        dates = [datetime.strptime(post['date_posted'], '%Y-%m-%d') for post in recent_posts]
        dates.sort(reverse=True)  # Most recent first
        
        days_since_last = (datetime.now() - dates[0]).days
        
        # Calculate average gap between posts
        gaps = [(dates[i] - dates[i+1]).days for i in range(len(dates)-1)]
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        
        return {
            "days_since_last_post": days_since_last,
            "average_posting_frequency": f"Every {avg_gap:.1f} days",
            "posting_status": "overdue" if days_since_last > avg_gap * 1.5 else "on_schedule"
        }

    def _extract_recommendations(self, chat_result) -> str:
        """Extract and format final recommendations"""
        
        # Get all messages from the conversation
        all_messages = []
        if hasattr(chat_result, 'chat_history'):
            all_messages = chat_result.chat_history
        
        # Look for the coordinator's final recommendation
        final_recommendation = ""
        story_rec = ""
        feed_rec = ""
        
        for msg in reversed(all_messages):
            content = msg.get('content', '')
            name = msg.get('name', '')
            
            if name == 'content_coordinator' and 'FINAL RECOMMENDATION:' in content.upper():
                final_recommendation = content
                break
        
        # Also extract individual agent recommendations
        for msg in all_messages:
            content = msg.get('content', '')
            name = msg.get('name', '')
            
            if name == 'story_specialist' and len(content) > 100:
                story_rec = content[:500] + "..." if len(content) > 500 else content
            elif name == 'feed_specialist' and len(content) > 100:
                feed_rec = content[:500] + "..." if len(content) > 500 else content

        # Format the output
        output = "🎯 YOUR NEXT INSTAGRAM POSTS\n"
        output += "=" * 50 + "\n\n"
        
        if final_recommendation:
            output += " COORDINATED STRATEGY:\n"
            output += final_recommendation.replace('FINAL RECOMMENDATION:', '').strip()
            output += "\n\n"
        
        if story_rec:
            output += " STORY RECOMMENDATION:\n"
            output += story_rec + "\n\n"
            
        if feed_rec:
            output += " FEED POST RECOMMENDATION:\n" 
            output += feed_rec + "\n\n"
        
        output += " Ready to create your next posts!"
        
        return output

# Simplified CLI focused on recommendations
app = typer.Typer(help="Get your next Instagram story and feed post recommendations")

@app.command("next")
def get_next_recommendations(
    context: str = typer.Option("", help="Current situation or goals (e.g., 'launching new service', 'slow engagement lately')")
):
    """Get AI recommendations for your next Instagram story and feed post"""
    
    if not os.getenv('OPENAI_API_KEY'):
        typer.echo(" Please set OPENAI_API_KEY environment variable")
        typer.echo(" Or use the basic version: python cli.py generate-prompt")
        return
    
    typer.echo("Analyzing your content patterns...")
    typer.echo("AI agents collaborating on your next posts...")
    
    system = InstagramPostRecommender()
    recommendations = system.get_next_post_recommendations(context)
    
    typer.echo("\n" + recommendations)

@app.command("add")
def add_existing_post(
    caption: str = typer.Argument(..., help="Your post caption/description"),
    post_type: str = typer.Argument(..., help="Type: satisfying_video, promotion, educational, behind_scenes"),
    engagement: int = typer.Argument(..., help="Total engagement (likes + comments + saves)"),
    hashtags: str = typer.Option("", help="Comma-separated hashtags"),
    days_ago: int = typer.Option(0, help="How many days ago was this posted?")
):
    """Add one of your existing posts to build the recommendation database"""
    
    rag_db = RAGDatabase()
    
    hashtag_list = [tag.strip() for tag in hashtags.split(",") if tag.strip()]
    post_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    post_data = {
        "caption": caption,
        "type": post_type,
        "engagement": engagement, 
        "hashtags": hashtag_list,
        "date_posted": post_date
    }
    
    post_id = rag_db.add_post(post_data)
    typer.echo(f"Added: '{caption[:50]}...' ({engagement} engagement, {days_ago} days ago)")
    
    # Give quick recommendation tip
    total_posts = rag_db.get_post_count()
    if total_posts >= 3:
        typer.echo(f"You now have {total_posts} posts. Try: python app.py next")

@app.command("quick-setup")
def quick_setup():
    """Add sample posts to test the system immediately"""
    
    typer.echo(" Setting up sample window cleaning business posts...")
    
    rag_db = RAGDatabase()
    
    # Sample posts with realistic data
    samples = [
        ("Epic storefront transformation! 3 hours of work for this amazing result ", "satisfying_video", 3200, "#windowcleaning,#satisfying,#transformation,#commercial", 2),
        ("Pro tip Tuesday: Always start from the top and work your way down for streak-free results", "educational", 1800, "#protip,#windowcleaning,#technique,#professional", 5),
        (" March Special: 25% off first-time residential customers! Book this week only", "promotion", 950, "#deal,#residential,#windowcleaning,#march", 7),
        ("5 AM start at the downtown office complex. Early bird gets the crystal clear windows!", "behind_scenes", 2100, "#earlybird,#commercial,#windowcleaning,#downtown", 10),
        ("Before and After: This restaurant window hadn't been cleaned in 6 months!", "satisfying_video", 4100, "#beforeafter,#restaurant,#windowcleaning,#satisfying", 12),
        ("Why we use distilled water: It prevents mineral spots and gives that perfect finish", "educational", 1400, "#education,#windowcleaning,#water,#professional", 15)
    ]
    
    for caption, post_type, engagement, hashtags, days_ago in samples:
        post_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        hashtag_list = [tag.strip() for tag in hashtags.split(",")]
        
        post_data = {
            "caption": caption,
            "type": post_type,
            "engagement": engagement,
            "hashtags": hashtag_list,
            "date_posted": post_date
        }
        rag_db.add_post(post_data)
    
    typer.echo(f"Added {len(samples)} sample posts!")
    typer.echo("Now try: python app.py next")
    typer.echo("Or add your real posts with: python app.py add")

if __name__ == "__main__":
    app()
