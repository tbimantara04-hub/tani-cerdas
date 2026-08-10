import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from rag_logic import ask_chatbot

def test_query(query):
    print(f"\n--- Testing Query: {query} ---")
    answer, tools = ask_chatbot(query, llm_mode="api")
    print(f"Tools used: {tools}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    # Test 1: Combined query (Weather + Price)
    test_query("Berapa harga cabai rawit merah sekarang dan bagaimana cuaca di Malang?")

    # Test 2: Technical query (Hama/PDF)
    test_query("Bagaimana cara mengatasi hama wereng pada padi?")

    # Test 3: Personal query (Profile)
    # Note: This requires farmer_profile.json to exist or it will say it's empty
    test_query("Berdasarkan lahan saya, apakah cocok untuk memupuk besok?")

    # Test 4: Update profile
    test_query("Saya sekarang menanam jagung di lahan 2 hektar di Kediri")
