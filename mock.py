import random

def generate_mock_open_rate(subject_line, factors):
    # Base open rate
    open_rate = 0.2

    # Count the number of active factors
    active_factors = sum(factors.values())

    # Adjust based on factors
    if factors['personalization']:
        open_rate += 0.05
    if factors['joining_fees']:
        open_rate += 0.03
    if factors['cashback']:
        open_rate += 0.04
    if factors['first_year_free']:
        open_rate += 0.06
    if factors['urgency']:
        open_rate += 0.02

    # Penalize for too many factors
    if active_factors > 3:
        open_rate -= 0.05 * (active_factors - 3)

    # Penalize for long subject lines
    words = subject_line.split()
    if len(words) > 10:
        open_rate -= 0.02 * (len(words) - 10)

    # Add some randomness
    open_rate += random.uniform(-0.05, 0.05)

    # Ensure open_rate is between 0 and 1
    open_rate = max(0, min(1, open_rate))

    return open_rate

def simulate_email_opens(subject_line, factors, num_emails=1000):
    open_rate = generate_mock_open_rate(subject_line, factors)
    opens = sum(random.random() < open_rate for _ in range(num_emails))
    return opens, num_emails

# Example usage
if __name__ == "__main__":
    test_subject = "Get cashback and free first year! Limited time offer!"
    test_factors = {
        'personalization': 0,
        'joining_fees': 0,
        'cashback': 1,
        'first_year_free': 1,
        'urgency': 1
    }
    opens, total = simulate_email_opens(test_subject, test_factors)
    print(f"Subject: {test_subject}")
    print(f"Factors: {test_factors}")
    print(f"Opens: {opens}/{total} ({opens/total:.2%})")