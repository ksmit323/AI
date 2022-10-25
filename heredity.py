import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Probability of passing a gene depending on how many genes the parent has
    pass_gene = {
        1: 0.5,
        2: 1 - PROBS["mutation"],
        0: PROBS["mutation"]
    }

    # Dict to track parents' genes
    parents = {
        "mother":{},
        "father":{}
    }

    # Fill in dict with parent info
    for person in people:
        mother = people[person]["mother"]
        father = people[person]["father"]
        if mother != None and mother not in parents["mother"]:
            parents["mother"][mother] = 0
            parents["father"][father] = 0

            # Find how many genes mother has
            if mother in one_gene:
                parents["mother"][mother] = 1
            elif mother in two_genes:
                parents["mother"][mother] = 2
            else:
                parents["mother"][mother] = 0

            # Find how many genes father has
            if father in one_gene:
                parents["father"][father] = 1
            elif father in two_genes:
                parents["father"][father] = 2
            else:
                parents["father"][father] = 0

    # Initialize variable to track total probability of each case
    prob = 1

    # Calculate total probability under all conditions
    for person in people:
        name = people[person]

        if name["mother"] != None:

            # Probability of inheriting from mother
            from_mother = pass_gene[parents["mother"][name["mother"]]]
            not_from_mother = 1 - from_mother

            # Probability of inheriting from father
            from_father = pass_gene[parents["father"][name["father"]]]
            not_from_father = 1 - from_father

        # Probability everyone has one copy
        if person in one_gene:
            if name["mother"] == None:
                prob *= PROBS["gene"][1]
            else:
                prob *= (from_mother * not_from_father + not_from_mother * from_father)

            # Probability have/not have trait
            if person in have_trait:
                prob *= PROBS["trait"][1][True]
            else:
                prob *= PROBS["trait"][1][False]

        # Probability everyone has two copies
        elif person in two_genes:
            if name["mother"] == None:
                prob *= PROBS["gene"][2]
            else:
                prob *= from_mother * from_father

            # Probability have/not have trait
            if person in have_trait:
                prob *= PROBS["trait"][2][True]
            else:
                prob *= PROBS["trait"][2][False]

        # Probability everyone has zero copies
        else:
            if name["mother"] == None:
                prob *= PROBS["gene"][0]
            else:
                prob *= not_from_mother * not_from_father

            # Probability have/not have trait
            if person in have_trait:
                prob *= PROBS["trait"][0][True]
            else:
                prob *= PROBS["trait"][0][False]

    return prob


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:

        # Add probabilities to one_gene and have_trait
        if person in one_gene:
            probabilities[person]["gene"][1] += p
            if person in have_trait:
                probabilities[person]["trait"][True] += p
            else:
                probabilities[person]["trait"][False] += p

        # Add probabilities to two_genes and have_trait
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
            if person in have_trait:
                probabilities[person]["trait"][True] += p
            else:
                probabilities[person]["trait"][False] += p

        # Add probabilities to zero genes and have_trait
        else:
            probabilities[person]["gene"][0] += p
            if person in have_trait:
                probabilities[person]["trait"][True] += p
            else:
                probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for name in probabilities:

        # Normalization factor
        norm = 1 / (probabilities[name]["trait"][True] + probabilities[name]["trait"][False])

        # Normalize traits
        probabilities[name]["trait"][True] *= norm
        probabilities[name]["trait"][False] *= norm

        # Normalize genes
        for i in range(3):
            probabilities[name]["gene"][i] *= norm


if __name__ == "__main__":
    main()
