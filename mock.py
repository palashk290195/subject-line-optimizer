import random

def generate_mock_ctr(subject_line, factors, audience):
    base_ctr = 0.02  # 2% base click-through rate

    age = audience.split()[1]
    gender = audience.split()[0]

    # Adjust base CTR for age and gender
    if age == "18-30":
        base_ctr *= 1.2
    elif age == "50+":
        base_ctr *= 0.8

    if gender == "Female":
        base_ctr *= 1.1

    # Count active factors
    active_factors = sum(factors.values())

    # Adjust based on factors
    if factors['personalization']:
        if gender == "Female" or age == "50+":
            base_ctr *= 1.3
        else:
            base_ctr *= 1.1

    if factors['joining_fees']:
        if age == "50+" or (gender == "Female" and age == "30-50"):
            base_ctr *= 1.2
        elif age == "18-30":
            base_ctr *= 0.9
        else:
            base_ctr *= 1.1

    if factors['cashback']:
        if age == "18-30":
            base_ctr *= 1.3
        elif age == "50+":
            base_ctr *= 1.1
        else:
            base_ctr *= 1.2

    if factors['first_year_free']:
        if age == "30-50":
            base_ctr *= 1.3
        else:
            base_ctr *= 1.2

    if factors['urgency']:
        if age == "18-30":
            base_ctr *= 1.2
        elif age == "50+":
            base_ctr *= 0.9  # Negative impact for older segment
        else:
            base_ctr *= 1.1

    # Penalize for more than 3 factors, except for Female 30-50
    if active_factors > 3 and not (gender == "Female" and age == "30-50"):
        base_ctr *= 0.9 ** (active_factors - 3)

    # Specific negative impacts
    if gender == "Male" and age == "50+" and factors['urgency']:
        base_ctr *= 0.85  # Strong negative impact of urgency on older males

    if gender == "Female" and age == "18-30" and factors['joining_fees']:
        base_ctr *= 0.95  # Slight negative impact of mentioning joining fees for young females

    # Penalize for long subject lines
    words = subject_line.split()
    if len(words) > 10:
        base_ctr *= 0.95 ** (len(words) - 10)

    # Add some randomness
    base_ctr *= random.uniform(0.9, 1.1)

    # Ensure CTR is between 0 and 1
    return max(0, min(1, base_ctr))

def simulate_email_campaign(subject_line, factors, audience, num_emails):
    ctr = generate_mock_ctr(subject_line, factors, audience)
    clicks = int(num_emails * ctr)
    return clicks, num_emails