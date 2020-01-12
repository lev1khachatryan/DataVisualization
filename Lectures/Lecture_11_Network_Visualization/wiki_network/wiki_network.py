from operator import itemgetter
import networkx as nx
import wikipedia
import matplotlib.pyplot as plt

START = "Armenia"

F = nx.DiGraph()

to_scrape_list = [(0, START)]
to_scrape_set = set(to_scrape_list)
done_set = set()

layer, page = to_scrape_list[0]

while layer < 2:
    del to_scrape_list[0]
    done_set.add(page)
    print(layer, page) # Show progress
    
    try:
        wiki = wikipedia.page(page)
    except KeyboardInterrupt:
        raise
    except:
        layer, page = to_scrape_list[0]
        print("Could not load", page)
        continue

    for link in wiki.links:
        link = link.title()
        if not link.startswith("List Of") or not link.startswith("Economy Of"):
            if link not in to_scrape_set and link not in done_set:
                to_scrape_list.append((layer + 1, link))
                to_scrape_set.add(link)
            F.add_edge(page, link)
    layer, page = to_scrape_list[0]

    
    
core = [node for node, deg in F.degree() if deg >= 300]
G = nx.subgraph(F, core)
print("{} nodes, {} edges".format(len(G), nx.number_of_edges(G)))

nx.write_graphml(G, "wiki.graphml")

G = nx.read_graphml("wiki.graphml")

top_indegree = sorted(G.in_degree(),reverse=True, key=itemgetter(1))[:100]
print("\n".join(map(lambda t: "{} {}".format(*reversed(t)), top_indegree)))


size_ = list(G.in_degree())
size_ = [j for i,j in size_]


nx.draw(G,linewidths = 2,width = 0.2, edgecolors = "white", font_size = 8, edge_color = "b", with_labels = True)
plt.savefig("wiki.png", dpi = 900)