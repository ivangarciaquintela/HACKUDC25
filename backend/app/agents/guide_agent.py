from smolagents import Tool, ToolCallingAgent, HfApiModel
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..models.guide import Guide
from ..models.skill import Skill
import json

class GuideCreatorTool(Tool):
    name = "guide_creator"
    description = (
        "Creates a new learning guide in the database. "
        "The guide will be associated with a specific skill and user. "
        "You should extract the relevant information from the natural language input. "
        "IMPORTANT: This tool should only be called ONCE. After a successful guide creation, return the response immediately."
    )
    inputs = {
        "title": {
            "type": "string",
            "description": "The title of the guide - a clear, descriptive title that indicates what will be learned"
        },
        "content": {
            "type": "string", 
            "description": "The main content of the guide, should be well-structured with clear explanations, examples, and steps"
        },
        "skill_name": {
            "type": "string",
            "description": "Name of the technical skill this guide teaches (e.g., Python, JavaScript, React)"
        },
        "user_id": {
            "type": "string",
            "description": "UUID of the user creating the guide"
        }
    }
    output_type = "string"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def forward(self, title: str, content: str, skill_name: str, user_id: str) -> str:
        db = SessionLocal()
        try:
            # Find the skill
            skill = db.query(Skill).filter(Skill.name == skill_name).first()
            if not skill:
                return json.dumps({
                    "error": f"Skill '{skill_name}' not found",
                    "stop": True  # Signal to stop processing
                })

            # Create new guide
            new_guide = Guide(
                title=title,
                content=content,
                skill_id=skill.id,
                user_id=user_id
            )

            db.add(new_guide)
            db.commit()
            db.refresh(new_guide)

            return json.dumps({
                "success": True,
                "message": "Guide created successfully",
                "guide_id": str(new_guide.id),
                "stop": True  # Signal to stop processing
            })

        except Exception as e:
            db.rollback()
            return json.dumps({
                "error": f"Failed to create guide: {str(e)}",
                "stop": True  # Signal to stop processing
            })
        finally:
            db.close()

# Define guide creation specific prompts
guide_creation_prompts = {
    "system_prompt": """
    You are an AI assistant that helps users create educational guides and tutorials in a structured way.
    Your job is to analyze natural language descriptions and convert them into well-organized learning guides.
    
    IMPORTANT: You should create exactly ONE guide per request. After successfully creating a guide or encountering an error,
    return the response immediately. Do not attempt to create multiple guides or modify an existing guide.
    
    When processing a request:
    1. Identify the main technical skill/technology being taught
    2. Create a clear, descriptive title for the guide
    3. Structure the content to include:
       - Introduction/Overview
       - Prerequisites (if any)
       - Step-by-step explanations
       - Code examples (if applicable)
       - Common pitfalls or tips
       - Practice exercises or challenges (optional)
    4. Use the guide_creator tool ONCE to create the guide in the database
    5. Return the response immediately after creation
    
    Remember:
    - Create only ONE guide per request
    - Return immediately after guide creation
    - Titles should be clear and indicate what will be learned
    - Content should be well-organized and easy to follow
    - Include practical examples and explanations
    - Use proper formatting for code snippets
    """,
    
    "task_planning": """
    To create this guide, I will:
    1. Analyze the user's input to identify the main topic and skill
    2. Create a descriptive title
    3. Structure the content in a logical learning sequence
    4. Create the guide using the guide_creator tool
    5. Return the response immediately
    
    Note: I will create exactly one guide and stop processing after creation.
    """,
    
    "execution": """
    Creating the guide with the following information:
    {{ execution_plan }}
    """,
    
    "reflection": """
    Guide creation attempt complete. If successful, I will stop here.
    If there was an error, I will provide clear feedback about what went wrong.
    """,
    
    "error": """
    An error occurred: {{ error }}
    Providing clear feedback about what went wrong and stopping.
    """,
    
    "final_answer": """
    {{ answer }}
    """
}

# Initialize the guide creation agent with the tool
guide_creation_agent = ToolCallingAgent(
    tools=[GuideCreatorTool()],
    model=HfApiModel(token=""),
    prompt_templates=guide_creation_prompts
) 