from strands import tool
from datetime import datetime

@tool(name="get_todays_date", description="Retrieves today's date for accuracy")
def get_todays_date() -> str:
    today = datetime.today().strftime('%Y-%m-%d')
    print(f'> get_todays_date today={today}')
    return today
