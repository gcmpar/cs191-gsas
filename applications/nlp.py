from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(course_desc, target_desc, all_taken_descs):
    """
    Computes the cosine similarity percentage between a taken course's description
    and a prerequisite target course's description, fitted on the corpus of all taken descriptions.
    """
    if not course_desc or not target_desc:
        return 0.0

    corpus = [desc for desc in all_taken_descs if desc] + [target_desc]
    if not corpus:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words='english').fit(corpus)
        vectors = vectorizer.transform([course_desc, target_desc])
        
        similarity_matrix = cosine_similarity(vectors[0], vectors[1])
        return round(similarity_matrix[0, 0] * 100, 2)
    except ValueError:
        return 0.0

def compute_similarity_batch(taken_courses, target_course):
    """
    Computes similarity for a list of taken courses against a target course.
    Returns a list of similarity percentages in the same order.
    """
    if not target_course or not target_course.description:
        return [0.0] * len(taken_courses)
        
    taken_descriptions = [c.description for c in taken_courses if c.description]
    corpus = taken_descriptions + [target_course.description]
    
    if not corpus:
        return [0.0] * len(taken_courses)
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english').fit(corpus)
        taken_vectors = vectorizer.transform([c.description or "" for c in taken_courses])
        prereq_vector = vectorizer.transform([target_course.description])
        
        similarity_matrix = cosine_similarity(prereq_vector, taken_vectors)
        return [round(score * 100, 2) for score in similarity_matrix[0]]
    except ValueError:
        return [0.0] * len(taken_courses)
