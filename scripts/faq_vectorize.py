#! .venv/bin/python

import yaml

from scripts.apptools import get_embedding

# Load existing tagged FAQ data
faq_file = "store/faq_tagged.yml"
output_file = "store/faq_vectorized.yml"

if __name__ == '__main__':

    with open(faq_file, "r", encoding="utf-8") as f:
        faq_data = yaml.safe_load(f)

    # Generate vectors for tags
    for tag in faq_data["tags"]:
        tag["vector"] = get_embedding(tag["description"])

    # Generate vectors for FAQ questions and answers
    for faq in faq_data["faq"]:
        faq["question_vectors"] = get_embedding(faq["question"])
        faq["answer_vectors"] = get_embedding(faq["answer"])

    # Save updated data
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(faq_data, f, allow_unicode=True)

    print(f"Vectorized FAQ data saved to {output_file}")
