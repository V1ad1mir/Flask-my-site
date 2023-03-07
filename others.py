def calculate_percent_visited(num_countries_visited):
    total_countries = 195 # Total number of countries in the world
    percent_visited = (num_countries_visited / total_countries) * 100
    return round(percent_visited, 2) # round to 2 decimal places

def get_user_with_largest_countries_list():
    users = User.query.all()
    max_user = None
    max_count = 0 
    for user in users:
        country_count = len(user.visited_countries)
        if country_count > max_count:
            max_user = user
            max_count = country_count
    return max_user