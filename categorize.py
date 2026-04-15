def categorize(issue):

    issue=issue.lower()

    if "hostel" in issue:
        return "Hostel"

    elif "canteen" in issue:
        return "Canteen"

    elif "security" in issue:
        return "Security"

    elif "safety" in issue:
        return "Women Safety"

    else:
        return "Other"