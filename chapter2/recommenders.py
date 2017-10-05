from math import sqrt
import csv

# A dictionary of movie critics and their ratings of a small set of movies
critics = {
    'Lisa Rose': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'Superman Returns': 3.5,
        'You, Me and Dupree': 2.5,
        'The Night Listener': 3.0,
    },
    'Gene Seymour': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 3.5,
        'Just My Luck': 1.5,
        'Superman Returns': 5.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 3.5,
    },
    'Michael Phillips': {
        'Lady in the Water': 2.5,
        'Snakes on a Plane': 3.0,
        'Superman Returns': 3.5,
        'The Night Listener': 4.0,
    },
    'Claudia Puig': {
        'Snakes on a Plane': 3.5,
        'Just My Luck': 3.0,
        'The Night Listener': 4.5,
        'Superman Returns': 4.0,
        'You, Me and Dupree': 2.5,
    },
    'Mick LaSalle': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'Just My Luck': 2.0,
        'Superman Returns': 3.0,
        'The Night Listener': 3.0,
        'You, Me and Dupree': 2.0,
    },
    'Jack Matthews': {
        'Lady in the Water': 3.0,
        'Snakes on a Plane': 4.0,
        'The Night Listener': 3.0,
        'Superman Returns': 5.0,
        'You, Me and Dupree': 3.5,
    },
    'Toby': {'Snakes on a Plane': 4.5,
              'You, Me and Dupree': 1.0,
             'Superman Returns': 4.0},
}

def sim_distance(prefs, p1, p2):
    '''
    Returns a distance-based similarity score for person1 and person2.
    '''

    # Get the list of shared_items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    # If they have no ratings in common, return 0
    if len(si) == 0:
        return 0
    # Add up the squares of all the differences
    sum_of_squares = 0
    for item in si:
        sum_of_squares += pow(prefs[p1][item] - prefs[p2][item], 2)
    return 1 / (1 + sqrt(sum_of_squares))

def sim_pearson(prefs, p1, p2):
    '''
    Returns the pearson correlation coefficient for p1 and p2
    '''
    # Get the list of mutually rated items
    si = {}
    for item in prefs[p1].keys():
        if item in prefs[p2].keys():
            si[item] = 1
    # Find the number of elements
    n = float(len(si))
    # if they are no ratings in common, return 0
    if n == 0:
        return 0

    # Add up all the preferences and sum up the squares, then sum up the products
    sum1, sum2, sum1Sq, sum2Sq, pSum = 0.0, 0.0, 0.0, 0.0, 0.0
    for key in si.keys():
        if key in prefs[p1]:
            sum1 += prefs[p1][key]
            sum1Sq += pow(prefs[p1][key], 2)
        if key in prefs[p2]:
            sum2 += prefs[p2][key]
            sum2Sq += pow(prefs[p2][key], 2)
        if key in prefs[p1] and key in prefs[p2]:
            pSum += prefs[p2][key] * prefs[p1][key]

    # Calculate Pearson score
    num = (pSum/n) - (1.0 * sum1 * sum2 / pow(n, 2))

    den = sqrt(((sum1Sq / n) - float(pow(sum1, 2)) / float(pow(n, 2))) *
               ((sum2Sq / n) - float(pow(sum2, 2)) / float(pow(n, 2))))
    if den == 0:
        return 0

    r = num / den

    return r

def topMatches(
    prefs,
    person,
    n=5,
    similarity=sim_pearson,
):
    '''
    Returns the best matches for person from the prefs dictionary.
    Number of results and similarity function are optional params.
    '''

    scores = [(similarity(prefs, person, other), other) for other in prefs
              if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def transformPrefs(prefs):
    '''
    Transform the recommendations into a mapping where persons are described
    with interest scores for a given title e.g. {title: person} instead of
    {person: title}.
    '''

    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})
            # Flip item and person
            result[item][person] = prefs[person][item]
    return result

def calculateSimilarItems(prefs, n=10):
    '''
    Create a dictionary of items showing which other items they are
    most similar to.
    '''

    result = {}
    # Invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # Status updates for large datasets
        c += 1
        # Find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result

def getRecommendedItems(prefs, user):
    '''
    Generates the normalized and predicted movie ratings on the movies
    that the user has not watched.

    It does this by taking the sum(each movie sim)/sum(each movie rating * sim)
    for each movie

    Returns a list of movie rating predictions sorted by the highest rating first
    '''

    itemMatch = calculateSimilarItems(prefs, n=10)
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # Loop over items rated by this user
    for (item, rating) in userRatings.items():

        # Loop over items similar to this one
        for (similarity, item2) in itemMatch[item]:

            # Ignore if this user has already rated this item
            if item2 in userRatings:
                continue

            # Weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # Sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # Divide each total score by total weighting to get an average
    rankings = [(score / totalSim[item], item) for (item, score) in
                scores.items()]

    # Return the rankings from highest to lowest
    rankings.sort()
    rankings.reverse()
    return rankings

def loadMovieLens(path='C:\\Users\\cli\\Downloads\\ml-20m'):
    # Get movie titles
    movies = {}
    print(path)
    first = True
    with open(path + '\\movies.csv', encoding='utf8') as f:
        reader = csv.reader(f)
        for line in reader:
            if first:
                first = False
                continue
            (id, title) = line[0], line[1]
            movies[id] = title

    first = True
    # Load data
    prefs = {}
    with open(path + '\\ratings.csv', encoding='utf8') as f:
        reader = csv.reader(f)
        for line in reader:
            if first:
                first = False
                continue
            (user, movieid, rating, ts) = line[0], line[1], line[2], line[3]
            prefs.setdefault(user, {})
            prefs[user][movies[movieid]] = float(rating)

    return prefs

def getRecommendations(prefs, person, similarity=sim_pearson):
    '''
    Gets recommendations for a person by using a weighted average
    of every other user's rankings
    '''

    totals = {}
    simSums = {}
    for other in prefs:
    # Don't compare me to myself
        if other == person:
            continue
        sim = similarity(prefs, person, other)
        # Ignore scores of zero or lower
        if sim <= 0:
            continue
        for item in prefs[other]:
            # Only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # Similarity * Score
                totals.setdefault(item, 0)
                # The final score is calculated by multiplying each item by the
                #   similarity and adding these products together
                totals[item] += prefs[other][item] * sim
                # Sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim
    # Create the normalized list
    rankings = [(total / simSums[item], item) for (item, total) in
                totals.items()]
    # Return the sorted list
    rankings.sort()
    rankings.reverse()
    return rankings

prefs = loadMovieLens()
print(getRecommendations(prefs, '87'))

