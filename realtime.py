from datetime import datetime


# -----------------------------------
# Get Current Date
# -----------------------------------

def get_date():

    now = datetime.now()

    return now.strftime("%d %B %Y")


# -----------------------------------
# Get Current Day
# -----------------------------------

def get_day():

    now = datetime.now()

    return now.strftime("%A")


# -----------------------------------
# Get Current Time
# -----------------------------------

def get_time():

    now = datetime.now()

    return now.strftime("%I:%M %p")


# -----------------------------------
# Test
# -----------------------------------

if __name__ == "__main__":

    print("Date:", get_date())
    print("Day:", get_day())
    print("Time:", get_time())
