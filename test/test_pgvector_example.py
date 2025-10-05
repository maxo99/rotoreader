# """Example test demonstrating pgvector testcontainers usage."""
import pytest
from sqlalchemy import text

from rotoreader.adapters.postgres_client import PostgresClient





# @pytest.mark.integration
# @pytest.mark.vector
# def test_vector_operations(postgres_client: PostgresClient):
#     """Test basic vector operations with pgvector."""
#     with postgres_client.engine.connect() as conn:
#         # Create a test table with vector column
#         conn.execute(text("""
#             CREATE TABLE IF NOT EXISTS test_embeddings (
#                 id SERIAL PRIMARY KEY,
#                 content TEXT,
#                 embedding vector(3)
#             )
#         """))

#         # Insert test data with vectors
#         conn.execute(text("""
#             INSERT INTO test_embeddings (content, embedding) VALUES
#             ('test document 1', '[1,2,3]'),
#             ('test document 2', '[4,5,6]'),
#             ('test document 3', '[7,8,9]')
#         """))

#         # Test vector similarity search
#         result = conn.execute(text("""
#             SELECT content, embedding <-> '[1,2,3]' as distance
#             FROM test_embeddings
#             ORDER BY distance
#             LIMIT 2
#         """))

#         rows = list(result)
#         assert len(rows) == 2
#         assert rows[0][0] == "test document 1"  # Closest match
#         assert rows[0][1] == 0.0  # Exact match distance

#         conn.commit()


# @pytest.mark.integration
# def test_database_isolation(postgres_client: PostgresClient):
#     """Test that database state is properly isolated between tests."""
#     with postgres_client.engine.connect() as conn:
#         # This test should not see data from previous tests
#         result = conn.execute(text("""
#             SELECT COUNT(*) FROM information_schema.tables
#             WHERE table_schema = 'public'
#             AND table_name = 'test_embeddings'
#         """))
#         count = result.scalar()
#         # Table should not exist due to cleanup between tests
#         assert count == 0


# @pytest.mark.unit
# def test_example_unit_test():
#     """Example unit test that doesn't require database."""
#     # This test runs fast without any containers
#     assert 1 + 1 == 2