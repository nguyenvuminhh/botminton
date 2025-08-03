from datetime import date

def format_to_dd_mm(dt: date) -> str:
    """Format a date to 'dd/mm' (day/month) format."""
    return f"{dt.day:02d}/{dt.month:02d}"

if __name__ == "__main__":
    # Example usage
    today = date.today()
    print(format_to_dd_mm(today))