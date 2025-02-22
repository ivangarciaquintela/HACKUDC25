from smolagents import Tool, ToolCallingAgent, HfApiModel
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..models.issue import Issue
from ..models.skill import Skill
import json

class IssueCreatorTool(Tool):
    name = "issue_creator"
    description = (
        "Creates a new technical issue/question in the database. "
        "The issue will be associated with a specific skill and user. "
        "You should extract the relevant information from the natural language input."
    )
    inputs = {
        "title": {
            "type": "string",
            "description": "The title of the issue - a concise summary of the problem"
        },
        "description": {
            "type": "string", 
            "description": "Detailed description of the issue, including any error messages, steps to reproduce, or specific questions"
        },
        "skill_name": {
            "type": "string",
            "description": "Name of the technical skill this issue relates to (e.g., Python, JavaScript, React)"
        },
        "user_id": {
            "type": "string",
            "description": "ID of the user creating the issue"
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, title: str, description: str, skill_name: str, user_id: str) -> str:
        db = SessionLocal()
        try:
            # Find the skill
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                return json.dumps({
                    "error": f"Skill '{skill_name}' not found"
                })

            # Create new issue
            new_issue = Issue(
                title=title,
                description=description,
                skill_id=skill.id,
                user_id=user_id
            )

            db.add(new_issue)
            db.commit()
            db.refresh(new_issue)

            return json.dumps({
                "success": True,
                "message": "Issue created successfully",
                "issue_id": str(new_issue.id)
            })

        except Exception as e:
            db.rollback()
            return json.dumps({
                "error": f"Failed to create issue: {str(e)}"
            })
        finally:
            db.close()

# Define issue creation specific prompts
issue_creation_prompts = {
    "system_prompt": """
    You are an AI assistant that helps users create technical issues and questions in a structured way.
    Your job is to analyze natural language descriptions and extract key information to create well-formatted issues.
    
    When processing a request, you should:
    1. Identify the main technical skill/technology being discussed
    2. Create a clear, concise title that summarizes the issue
    3. Structure the description to include relevant details
    4. Use the issue_creator tool to create the issue in the database
    
    Remember:
    - Titles should be brief but descriptive
    - Descriptions should be detailed and well-organized
    - Always identify the primary technical skill involved
    - Handle errors gracefully and provide clear feedback
    """,
    
    "task_planning": """
    To create this issue, I will:
    1. Analyze the user's description to identify the key components
    2. Extract or infer the technical skill involved
    3. Formulate a clear, concise title
    4. Structure the description for clarity
    5. Use the issue_creator tool to create the database entry
    
    Let me proceed with this plan.
    """,
    
    "execution": """
    I will now create the issue using the extracted information:
    {{ execution_plan }}
    """,
    
    "reflection": """
    Let me verify the issue creation:
    1. Is the title clear and descriptive?
    2. Is the description complete and well-structured?
    3. Have I correctly identified the technical skill?
    4. Is all required information included?
    """,
    
    "error": """
    An error occurred: {{ error }}
    Let me try to resolve this or provide clear feedback about what went wrong.
    """,
    
    "final_answer": """
    {{ answer }}
    """
}

# Initialize the issue creation agent with the tool
issue_creation_agent = ToolCallingAgent(
    tools=[IssueCreatorTool()],
    model=HfApiModel(token="***REMOVED***"),
    prompt_templates=issue_creation_prompts
) 