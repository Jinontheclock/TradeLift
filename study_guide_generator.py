import json
import os
import re
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')

def load_scraped_data():
    # Load the scraped data from the JSON file.
    with open('outputs/study_guide.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_key_points(text, num_points=5):
    task = f"""
    Extract {num_points} key important points from the following text. 
    Format each point as a bullet point starting with •.
    Focus on certification requirements, important concepts, and critical information.
    """
    
    result = process_with_openai(text, task)
    if result:
        # Extract bullet points
        points = [line.strip() for line in result.split('\n') if line.strip().startswith('•')]
        return points[:num_points]

def generate_practice_questions(content):
    """Generate practice questions using OpenAI."""
    task = """
    Generate 5 practice questions based on the following content.
    Include a mix of:
    - Knowledge verification questions
    - Conceptual understanding questions
    - Application-based questions
    Format each question on a new line starting with a number and a dot (e.g., "1. What is...")
    """
    
    result = process_with_openai(content, task)
    if result:
        # Extract numbered questions
        questions = [line.strip() for line in result.split('\n') 
                    if line.strip() and re.match(r'^\d+\.', line.strip())]
        return questions[:5]
    
    # Fallback to basic questions if OpenAI fails
    return [
        "1. What are the main requirements for certification?",
        "2. What steps are involved in the certification process?",
        "3. What resources are available for exam preparation?",
        "4. What are the key responsibilities in this trade?",
        "5. What are the important safety considerations?"
    ]

def process_with_openai(content, task):
    """Process content using OpenAI API."""
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": f"You are a professional study guide creator. {task}"},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return None

def filter_relevant_content(data, topic):
    """Filter content relevant to the user's topic."""
    topic_words = topic.lower().split()
    relevant_content = []
    
    for item in data:
        if not item.get('content'):
            continue
        
        # Calculate relevance score
        score = 0
        content_lower = item['content'].lower()
        title_lower = item['title'].lower()
        
        for word in topic_words:
            if word in title_lower:
                score += 2  # Title matches are more important
            if word in content_lower:
                score += 1
                
        if score > 0:
            relevant_content.append({
                'title': item['title'],
                'content': item['content'],
                'source': item['url'],
                'score': score
            })
    
    # Sort by relevance score
    relevant_content.sort(key=lambda x: x['score'], reverse=True)
    return relevant_content[:5]  # Return top 5 most relevant items

def create_study_guide(topic):
    """Create a structured study guide based on user input."""
    data = load_scraped_data()
    relevant_content = filter_relevant_content(data, topic)
    
    if not relevant_content:
        return "No relevant content found for this topic."
        
    # Combine relevant content
    all_content = "\n\n".join(f"Title: {item['title']}\n\n{item['content']}" 
                             for item in relevant_content)
    
    # Generate overview using OpenAI
    overview_task = f"""
    Create a concise overview of {topic} based on the following content.
    Focus on what the certification entails, its importance, and general requirements.
    Write 2-3 paragraphs.
    """
    overview = process_with_openai(all_content, overview_task) or f"This study guide covers key aspects of {topic}."
    
    # Create structured study guide
    study_material = f"""
===========================================
STUDY GUIDE: {topic.upper()}
===========================================
Generated on: {datetime.now().strftime('%B %d, %Y')}

TABLE OF CONTENTS:
1. Overview
2. Key Points
3. Detailed Content
4. Practice Questions
5. References

-------------------------------------------
1. OVERVIEW
-------------------------------------------
{overview}

-------------------------------------------
2. KEY POINTS
-------------------------------------------
"""
    
    # Add key points from all relevant content
    all_key_points = []
    for item in relevant_content:
        points = extract_key_points(item['content'])
        all_key_points.extend(points)
    
    for i, point in enumerate(all_key_points[:10], 1):
        study_material += f"• {point}\n"
    
    study_material += "\n-------------------------------------------\n"
    study_material += "3. DETAILED CONTENT\n"
    study_material += "-------------------------------------------\n"
    
    # Add detailed content sections
    for item in relevant_content:
        study_material += f"\nTopic: {item['title']}\n"
        study_material += "-" * len(f"Topic: {item['title']}") + "\n"
        study_material += f"{item['content'][:500]}...\n"  # Truncate long content
    
    study_material += "\n-------------------------------------------\n"
    study_material += "4. PRACTICE QUESTIONS\n"
    study_material += "-------------------------------------------\n"
    
    # Generate practice questions from content
    all_content = " ".join(item['content'] for item in relevant_content)
    questions = generate_practice_questions(all_content)
    for i, question in enumerate(questions, 1):
        study_material += f"{i}. {question}\n"
    
    study_material += "\n-------------------------------------------\n"
    study_material += "5. REFERENCES\n"
    study_material += "-------------------------------------------\n"
    
    for item in relevant_content:
        study_material += f"• {item['title']}\n  Source: {item['source']}\n"
    
    # Save to file
    output_file = f"outputs/{topic.replace(' ', '_')}_study_guide.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(study_material)
    
    return f"Study guide created and saved to {output_file}"

def main():
    """Run the study guide generator."""
    # Create outputs directory if it doesn't exist
    os.makedirs('outputs', exist_ok=True)
    
    print("\nTrade Study Guide Generator")
    print("=" * 30)
    print("This tool creates study guides from scraped trade certification content.")
    print("Enter a topic like 'red seal certification' or 'electrical certification'")
    
    while True:
        try:
            # Get user input
            topic = input("\nEnter a study guide topic (or 'quit' to exit): ").strip()
            
            if not topic:
                continue
                
            if topic.lower() == 'quit':
                print("\nGoodbye!")
                break
            
            # Generate study guide
            print("\nGenerating study guide...")
            result = create_study_guide(topic)
            print(result)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            continue

if __name__ == '__main__':
    main()