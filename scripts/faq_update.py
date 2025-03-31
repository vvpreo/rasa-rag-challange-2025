#! .venv/bin/python
import yaml

from scripts.apptools import query_openrouter, query_openrouter_fast

# Load FAQ data
faq_file = "store/faq.yml"
output_file = "store/faq_tagged.yml"

if __name__ == '__main__':
    with open(faq_file, "r", encoding="utf-8") as f:
        faq_data = yaml.safe_load(f)

    tags = faq_data.get("tags", {})
    faq_items = faq_data.get("faq", [])

    # Process each FAQ item
    tagged_faq = []
    for item in faq_items:
        question = item["question"]
        answer = item["answer"]

        # Construct system and user prompts
        system_prompt = [
            "You are an AI classifier. Your task is to categorize FAQ questions into relevant topics.",
            f"Available categories: {tags}",
            "Return only a list of the most relevant category codes."
            "RETURN TEMPLATE: tagcode1,tagcode2,tagcode3,..."
        ]
        user_prompt = [str(item)]

        # Query OpenRouter for classification
        relevant_tags = query_openrouter_fast(
            model="openai/chatgpt-4o-latest",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            # dry_run=True,
        )
        relevant_tags = relevant_tags.strip().split(",")  # Convert response to list

        print(f"\n\n{item['question']}")
        print(relevant_tags)


        # Append modified entry with tags
        tagged_faq.append({
            "question": question,
            "answer": answer,
            "tags": relevant_tags
        })

    # Save updated FAQ with tags
    output_data = {
        "tags": tags,
        "faq": tagged_faq
    }

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(output_data, f, allow_unicode=True, default_flow_style=False)

    print(f"Tagged FAQ file saved: {output_file}")
