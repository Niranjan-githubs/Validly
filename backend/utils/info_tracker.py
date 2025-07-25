# Rule-based info tracker for startup summary extraction from chat history
REQUIRED_FIELDS = [
    "title", "target_users", "problem", "solution", "business_model",
    "monetization", "competition", "differentiator", "tech_requirements",
    "risks", "vision"
]

def extract_info_from_message(message, info_dict):
    text = message.lower()
    if not info_dict["title"] and ("idea" in text or "building" in text or "app" in text):
        info_dict["title"] = message
    if not info_dict["target_users"] and ("user" in text or "market" in text or "customer" in text):
        info_dict["target_users"] = message
    if not info_dict["problem"] and ("problem" in text or "pain" in text or "challenge" in text):
        info_dict["problem"] = message
    if not info_dict["solution"] and ("solution" in text or "how" in text or "approach" in text):
        info_dict["solution"] = message
    if not info_dict["business_model"] and ("business model" in text or "revenue" in text or "monetization" in text):
        info_dict["business_model"] = message
    if not info_dict["competition"] and ("competitor" in text or "competition" in text):
        info_dict["competition"] = message
    if not info_dict["differentiator"] and ("different" in text or "unique" in text or "advantage" in text):
        info_dict["differentiator"] = message
    if not info_dict["tech_requirements"] and ("tech" in text or "integration" in text or "infrastructure" in text):
        info_dict["tech_requirements"] = message
    if not info_dict["risks"] and ("risk" in text or "concern" in text or "challenge" in text):
        info_dict["risks"] = message
    if not info_dict["vision"] and ("vision" in text or "goal" in text or "future" in text):
        info_dict["vision"] = message
    return info_dict

def is_summary_ready(info_dict, min_fields=7):
    filled = [k for k, v in info_dict.items() if v]
    return len(filled) >= min_fields

def process_conversation(conversation, min_fields=7):
    info_dict = {field: None for field in REQUIRED_FIELDS}
    for msg in conversation:
        if msg.get("role") == "user":
            info_dict = extract_info_from_message(msg.get("content", ""), info_dict)
        if is_summary_ready(info_dict, min_fields=min_fields):
            break
    return info_dict

def extract_startup_info(messages, min_fields=7):
    info_dict = {field: None for field in REQUIRED_FIELDS}
    for msg in messages:
        info_dict = extract_info_from_message(msg, info_dict)
    is_ready = is_summary_ready(info_dict, min_fields=min_fields)
    return info_dict, is_ready 