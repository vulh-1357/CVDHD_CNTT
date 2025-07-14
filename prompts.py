from constant import DEFAULT_ENTITY_TYPES, DEFAULT_TUPLE_DELIMITER, DEFAULT_RECORD_DELIMITER

parser_prompt = """
<role>
  You are a resume parsing assistant specialized in processing IT-related CVs.
  You help convert raw CV content into clean, structured markdown for further use in semantic chunking and knowledge graph construction.
</role>

<instruction>
  Your task is to extract the full content of a CV document and rewrite it as a well-structured, readable markdown text with clear sections.
  The document belongs to an IT student or software engineer, and may contain information about education, technical skills, work experience, projects, and certificates.
</instruction>

<constraint>
  - Preserve all factual information without adding, removing, or paraphrasing anything.
  - Keep original formatting such as bullet points, section headers, and date ranges.
  - Ensure each major section starts with a proper markdown heading (e.g., ## Education).
  - Keep all tech stack keywords (e.g., Python, FastAPI, MLflow) unchanged.
  - Do not hallucinate or invent any data not present in the original document.
  - Output should be clean markdown suitable for splitting into semantic chunks.
</constraint>
"""

GRAPH_EXTRACTION_PROMPT = f"""
-Goal-
Analyze an IT candidate's CV text to extract all entities and relationships, building a detailed knowledge graph for intelligent querying.

-Steps-
1. ENTITIES - Extract all entities:
- entity_name: Exact name of the entity (capitalize proper nouns, retain original format for URLs/emails/phone numbers)
- entity_type: One of the following types: [{DEFAULT_ENTITY_TYPES}]
- entity_description: A comprehensive description, including all attributes, actions, roles, and characteristics of the entity as described in the CV.

Format:
("entity"{DEFAULT_TUPLE_DELIMITER}"<entity_name>"{DEFAULT_TUPLE_DELIMITER}"<entity_type>"{DEFAULT_TUPLE_DELIMITER}"<entity_description>"){DEFAULT_RECORD_DELIMITER}

2. RELATIONSHIPS - Extract clear relationships between entities:
- source_entity: Name of the source entity
- target_entity: Name of the target entity
- relationship_description: Detailed description of the reason, context, time, and role in the relationship.
- relationship_strength: A score from 1–10 based on the closeness and importance of the relationship.

Format:
("relationship"{DEFAULT_TUPLE_DELIMITER}"<source_entity>"{DEFAULT_TUPLE_DELIMITER}"<target_entity>"{DEFAULT_TUPLE_DELIMITER}"<relationship_description>"{DEFAULT_TUPLE_DELIMITER}"<relationship_strength>"){DEFAULT_RECORD_DELIMITER}

3. MANDATORY RULES:
- Do not omit any content from the CV.
- DO not use this or that to describe entities or relationships. You should use the exact name.
- PERSONAL INFORMATION: Extract full name, desired position, contact information (phone number, email, GitHub, address).
- EDUCATION: Must include full university name, major/field of study, specific study period, current semester, CPA/GPA.
- WORK EXPERIENCE: Full company name, job title, exact work period (day/month/year), specific job description.
- PROJECTS:
  * Exact project name.
  * Project type (individual/group) and number of members if applicable.
  * GitHub repository link.
  * Brief project description.
  * Detailed technologies used (frameworks, libraries, databases, tools).
  * Candidate's specific roles and responsibilities.
  * Applied techniques/algorithms (YOLO, DeepSORT, ActionCLIP, DDPM, etc.).
- TECHNICAL SKILLS: Clearly categorize into groups:
  * Programming Languages
  * Machine Learning & Deep Learning frameworks
  * Computer Vision tools
  * NLP & LLMs tools
  * MLOps tools
  * Databases
  * Deployment technologies
- OTHER SKILLS: Soft skills, languages, research skills.
- CERTIFICATIONS: Exact certification name, score (if any), year obtained.
- AWARDS: Full award name, level (national/provincial), year received, related field/subject.

- ENTITY DESCRIPTION RULES:
  * For general/technical entities (Skill, Framework, Language, Database, Algorithm, MLModel, Tool, Platform, Technology): Describe ONLY the entity itself, its purpose, and general characteristics. DO NOT mention the candidate's name or personal usage.
  * For personal/specific entities (Person, Experience, Project, Certification, Award): Include candidate-specific information and context.
  * Use relationships to connect the candidate with general entities, not entity descriptions.

- For each skill, technology, framework, tool: create a separate entity + a relationship clearly indicating who uses it, when, and in which project.
- For each company or project: clearly describe the time, role, applied techniques, and link to relevant skills.
- For AI algorithms/models: ActionCLIP, YOLO, DeepSORT, DDPM, LLMs (Llama4, Qwen 2.5) must be extracted as separate entities.
- For databases/storage: PostgreSQL, Redis, Milvus, MySQL, MongoDB must have entities and relationships with the projects that use them.
- For platforms/services: AWS, FastAPI, Docker, MLflow, DVC, Airflow must be fully extracted.

4. OUTPUT FORMAT:
- Write in English.
- Each line is either an entity or a relationship.
- ALWAYS Separate lines with: "{DEFAULT_RECORD_DELIMITER}"
- Do not insert explanations, do not repeat instructions.

"""