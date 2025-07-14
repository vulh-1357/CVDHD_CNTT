CONSTRAINT_NAME_QUERY = "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE"

CONSTRAINT_FILE_NAME_QUERY = "CREATE CONSTRAINT document_name_unique IF NOT EXISTS FOR (d:DOCUMENT) REQUIRE d.file_name IS UNIQUE"

CONSTRAINT_UID_DESCRIPTION_QUERY = "CREATE CONSTRAINT description_uid_unique IF NOT EXISTS FOR (d:DESCRIPTION) REQUIRE d.uid IS UNIQUE"

CONSTRAINT_UID_RELATIONSHIP_QUERY = "CREATE CONSTRAINT relationship_uid_unique IF NOT EXISTS FOR (r:RELATIONSHIP) REQUIRE r.uid IS UNIQUE"

CONSTRAINT_UID_CHUNK_QUERY = "CREATE CONSTRAINT chunk_uid_unique IF NOT EXISTS FOR (c:Chunk) REQUIRE c.uid IS UNIQUE"

CREATE_ENTITY_QUERY = """
MERGE (d1:DOCUMENT {file_name: $file_name})
MERGE (c:Chunk {uid: $chunk_uid})
SET c.text = $chunk_text, c.embeddings = $chunk_embeddings
MERGE (d1)-[:CONTAINED]->(c)
MERGE (e:Entity {name: $name})
SET e.type = $type
MERGE (c)-[:MENTIONED]->(e)
MERGE (d:DESCRIPTION {uid: $uid})
MERGE (e)-[:DESCRIBED]->(d)
SET d.text = $description, 
d.embeddings = $embeddings
"""

CREATE_RELATIONSHIP_QUERY = """
MATCH (source:Entity {name: $source_name}), (target:Entity {name: $target_name})
MERGE (r:RELATIONSHIP {uid: $uid1})
MERGE (source)-[:RELATED]->(r)
MERGE (r)-[:RELATED]->(target)
MERGE (d:DESCRIPTION {uid: $uid2})
MERGE (r)-[:DESCRIBED]->(d)
SET d.text = $description, d.score = $score, d.embeddings = $embeddings
"""