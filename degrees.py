import csv
import sys
import os
from collections import deque

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    while True:
        metodo = input("Seleccione metodo: \n 1- bfs \n 2- dfs \n ")
        if (metodo == '1' or metodo == 'bfs'):
            metodo= 'bfs'
            break
        
        if(metodo == '2' or metodo == 'dfs'):
            metodo= 'dfs'
            break

    os.system('cls' if os.name == 'nt' else 'clear')
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target,metodo)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source,target,metodo):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    if metodo == 'bfs':
        # Inicializamos una cola para BFS
        queue = deque()
        # Creamos un set para llevar un registro de las personas visitadas    
        visited = set()
        # Inicializamos la cola con la persona de origen y un camino vacío
        queue.append((source, []))

        while queue:
            person, path = queue.popleft()
            # Marcamos la persona actual como visitada
            visited.add(person)

            if person == target:
                return path  #Exito

            # Exploramos a los vecinos (personas que compartieron películas)
            neighbors = neighbors_for_person(person)
            for movie_id, neighbor in neighbors:
                if neighbor not in visited:
                    # Creamos un nuevo camino extendiendo el camino actual
                    new_path = path + [(movie_id, neighbor)]
                    queue.append((neighbor, new_path))

        #No exito
        return None
    
    if metodo == 'dfs': 
        # Pila para realizar una búsqueda en profundidad (DFS)
        stack = []
        # Conjunto para llevar un registro de las personas visitadas
        visited = set()
        # Inicializamos la pila con la persona de origen y un camino vacío
        stack.append((source, []))

        while stack:
            person, path = stack.pop()
            # Marcamos la persona actual como visitada
            visited.add(person)

            # Verificamos si la persona actual es el objetivo
            if person == target:
                return path  # Devolvemos el camino desde la fuente hasta el objetivo

            # Exploramos a los vecinos (personas que compartieron películas)
            neighbors = neighbors_for_person(person)
            for movie_id, neighbor in neighbors:
                if neighbor not in visited:
                    # Creamos un nuevo camino extendiendo el camino actual
                    new_path = path + [(movie_id, neighbor)]
                    stack.append((neighbor, new_path))

        # Si no se encuentra un camino, devolvemos None
        return None

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
