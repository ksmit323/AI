import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Initialize empty dictionary
    prob_dist = {}

    # Make set with all outgoing links from page
    links = corpus[page]

    # Determine how many outgoing links page has
    links_len = len(corpus[page])

    # Probability of (1 - DF) split equally between all pages
    rand_page = (1 - damping_factor) / len(corpus)

    #Loop over corpus to find probability distribution for each page
    for p in corpus:

        if p == page:

            # if the page has no outgoing links, every page has equal probability
            if links_len == 0:
                n = len(corpus)
                for p in corpus:
                    prob_dist[p] = 1 / n
                return prob_dist

            # If the current page has links, it has a probability of (1 - DF) split between all pages
            else:
                prob_dist[p] = rand_page

        # All other pages have probability DF plus any edges
        else:

            # If page has any incoming links, add to probability
            if p in links:
                prob_dist[p] = rand_page + damping_factor / links_len
            else:
                prob_dist[p] = rand_page

    return prob_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize dictionary that will be returned
    prob_dist = {}

    # Initialize list for all pages
    page_list = []

    # Loop over corpus keys to fill in empty dict and list
    for key in corpus.keys():

        # Fill in dictionary with page names and a default value of zero
        prob_dist[key] = 0

        # Make a list to select the first page at random
        page_list.append(key)

    # Simulate samples an 'n' number of times
    for i in range(n):

        # The first sample is generated at random
        if i == 0:
            page = random.choice(page_list)
            prob_dist[page] += 1

        # Create dictionary for current state using transition model
        new_state = transition_model(corpus, page, damping_factor)

        # Select from the keys at random based on their probability
        prob_value = []
        random_selection = []
        for key in page_list:
            prob_value.append(new_state[key])
        random_selection = random.choices(page_list, weights=prob_value) # Function returns a list
        page = random_selection[0]

        # Update the key-value count
        prob_dist[page] += 1

    # Change values in dict to be proportional to sample size
    for key in prob_dist:
        prob_dist[key] /= n

    return dict(sorted(prob_dist.items()))


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Total number of pages in the corpus
    N = len(corpus)

    # Fill dict with page names and a starting value of 1/N
    PR = {}
    for page in corpus.keys():
        PR[page] = 1/N

    # Initialized arrays needed to satisfy while loop
    PR_old = []
    PR_new = []
    PR_diff = [1]

    count = 0

    # Continue to loop until PageRank value converge so all PageRanks differ no less than 0.001 from old to new
    while(max(PR_diff) > 0.001):

        # Update old PageRank to take on the newest values
        PR_old = PR_new

        # Use copy of PR dict as to not alter while iterating
        PR_copy = PR.copy()

        # Calculate new PageRank for each page in the corpus
        for page in corpus:

            # Calculate the total sum of all current PageRanks, PR_i, that link to the page
            sum_PR_i = 0
            for key in corpus:

                # If page has no outgoing links, treat it exactly like it has links to every page
                if len(corpus[key]) == 0:
                    sum_PR_i += PR_copy[key] / N

                # Otherwise, find all incoming links to the page to sum up
                else:
                    if page in corpus[key]:
                        sum_PR_i += PR_copy[key] / len(corpus[key])

            # Update PR dict with new PageRank value
            PR[page] = (1-damping_factor)/N + damping_factor * sum_PR_i

        # Update PR_new matrix
        PR_new = []
        for key in PR:
            PR_new.append(PR[key])

        # Calculate the difference in PR change and store in a list without negative numbers
        if len(PR_old) > 0:
            PR_diff = []
            for i in range(len(PR_new)):
                x = abs(PR_new[i] - PR_old[i])
                PR_diff.append(round(x, 4))

    return dict(sorted(PR.items()))


if __name__ == "__main__":
    main()
