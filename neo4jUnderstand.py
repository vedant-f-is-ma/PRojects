from neo4j import GraphDatabase

# Connect to local Neo4j instance (change password accordingly)
uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password_here"

driver = GraphDatabase.driver(uri, auth=(username, password))

def find_friends(person_name):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Person)-[:FRIEND]->(friend)
            WHERE p.name = $name
            RETURN friend.name AS friend_name
            """,
            name=person_name
        )
        return [record["friend_name"] for record in result]

# Example usage
friends_of_alice = find_friends("Alice")
print("Alice's friends:", friends_of_alice)

driver.close()
