from requests import get
import numpy as np
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
import PyPDF2
import networkx as nx
import itertools
from collections import Counter

url = "https://en.wikipedia.org/wiki/List_of_Harry_Potter_characters"

response = get(url)
soup = bs(response.text)

list_items = soup.find("div", {"id" : "mw-content-text"}).find_all("li")
names = [i.text.split("–")[0].strip() for i in list_items if "–" in i.text]
names = names[:names.index("Winky")]

delete_list = ["Madam", "Sir", "Mr.", "Mrs.", "Lady", "The", "and", "Sr.", "/", "the"]

for delete_item in delete_list:
	names = [i.replace(delete_item, "") for i in names]


names = list(set(names))


harry = open('harry_1.pdf', 'rb')
harry = PyPDF2.PdfFileReader(harry)
number_of_pages = harry.getNumPages()
book = ""
for i in range(number_of_pages):
   page = harry.getPage(i)
   page_content = page.extractText()
   book += page_content

paragraphs = book.split("\n\n")




G = nx.Graph()
G.add_nodes_from(names)



names_ = []
for paragraph in paragraphs:
	temp_1 = []
	temp_2 = []
	for name in names:
		temp_1.append((np.sum([paragraph.count(i) for i in name.split()]), name))
		temp_2 = []
		for i in temp_1:
			if i[0] > 0:
				temp_2.append(i[1])
				G.add_edges_from([i for i in itertools.combinations(temp_2, 2)])
	names_.extend(temp_2)



size_ = Counter(names_)

remain = list(size_.keys())

remove = list(set(names) - set(remain))
G.remove_nodes_from(remove)



pos=nx.kamada_kawai_layout(G, scale = 500)
nx.draw(G,linewidths = 2,width = 0.2, edgecolors = "white", pos = pos, font_size = 8, edge_color = "b", with_labels = True, nodelist = list(size_.keys()), node_size = np.array(list(size_.values()))*1)
plt.show()
