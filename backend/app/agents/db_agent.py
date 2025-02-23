from smolagents import tool, ToolCallingAgent, HfApiModel
from sqlalchemy import text
import yaml
from ..database.database import SessionLocal

with open("app/agents/agent_prompts.yaml", "r") as f:
    prompt_templates = yaml.safe_load(f)

@tool
def sql_engine(query: str) -> str:
    """
    Allows you to perform SQL queries on the database. Returns a string representation of the result.
    The database has the following main tables:
    - users: User accounts with id (UUID), username, email, password_hash, created_at
    - skills: Technical skills with id (UUID), name, version, description, category
    - user_skills: Junction table linking users and skills, with proficiency_level (1-5), years_experience, last_used_date
    - guides: Learning guides with id (UUID), skill_id, user_id, title, guide_text, created_at, updated_at
    - issues: Technical issues/questions with id (UUID), skill_id, user_id, title, issue_description, created_at, updated_at
    - comments: Comments on issues with id (UUID), issue_id, user_id, comment_text, created_at

    Args:
        query: The query to perform. This should be correct SQL.
    """
    output = ""
    db = SessionLocal()
    try:
        rows = db.execute(text(query))
        for row in rows:
            output += "\n" + str(row)
    finally:
        db.close()
    return output

# Initialize the agent with the SQL tool
db_agent = ToolCallingAgent(
    tools=[sql_engine],
    model=HfApiModel(token=""),
    prompt_templates=prompt_templates
) 