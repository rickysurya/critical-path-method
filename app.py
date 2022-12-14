import streamlit as st 
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
from PIL import Image

st.title("Penjadwalan dengan Critical Path Method")

csv_data_input = st.file_uploader("Upload file csv disini", type="csv")
print(csv_data_input)
if (csv_data_input != None) :

    start = []
    graph = []
    atts = []
    path = []
    new = []
    stt = ""
    data = pd.read_csv(csv_data_input)
    last = data.iloc[-1, 0]
    last = chr(ord(last)+1)
    # -------------------------------------------
    for j in range(len(data)):
        for k in range(len(data.iloc[j, 1])):
            if data.iloc[j, 1][k] != '-':
                new.append(data.iloc[j, 1][k])
    # -------------------------------------------
    for j in range(len(data)):
        if not data.iloc[j, 0] in new:
            stt = stt+data.iloc[j, 0]
    # ------------------------------------------
    if data.shape[1] == 3:
        df = pd.DataFrame([[last, stt, 0]], columns=["ac", "pr", "du"])
    else:
        df = pd.DataFrame([[last, stt, 0, 0, 0]], columns=[
                          "ac", "pr", "b", "m", "a"])
    data = data.append(df)
    for i in range(len(data)):
        graph.append([])
        atts.append({})
    for j in range(len(data)):
        atts[j]["Name"] = data.iloc[j, 0]
        if data.shape[1] == 3:
            atts[j]["DU"] = data.iloc[j, 2]
        else:
            atts[j]["DU"] = (data.iloc[j, 4] + 4 *
                             data.iloc[j, 3] + data.iloc[j, 2]) / 6
        if(data.iloc[j, 1] == "-"):
            start.append(ord(data.iloc[j, 0])-65)
            continue
        for k in range(len(data.iloc[j, 1])):
            graph[ord(data.iloc[j, 1][k]) -
                  65].append(ord(data.iloc[j, 0])-65)
    level = [None] * (len(graph))
    def BFS(s, graph):
        visited = [False] * (len(graph))
        queue = []
        for i in s:
            queue.append(i)
            level[i] = 0
            visited[i] = True
        while queue:
            s = queue.pop(0)
            path.append(s)
            for i in graph[s]:
                if visited[i] == False:
                    queue.append(i)
                    level[i] = level[s] + 1
                    visited[i] = True
                else:
                    level[i] = max(level[s]+1, level[i])
    BFS(start, graph)
    levels = [None] * len(path)
    for i in range(len(path)):
        levels[i] = level[path[i]]
    path = [x for y, x in sorted(zip(levels, path))]
    
    for i in path:
        print(str(chr(i+65)), end=' ')
    for s in path:
        # print(str(chr(s+65)), " ", level[s])
        # -------------Forward--------------------
        if(data.iloc[s, 1] == "-"):
            atts[s]["ES"] = 0
        else:
            ls = []
            for k in range(len(data.iloc[s, 1])):
                ls.append(atts[ord(data.iloc[s, 1][k]) - 65]["EF"])
            atts[s]["ES"] = max(ls)
        atts[s]["EF"] = atts[s]["DU"] + atts[s]["ES"]
        # ---------------------------------
    for i in range(len(graph)):
        if(graph[i] == []):
            atts[i]["LF"] = atts[i]["EF"]
            atts[i]["LS"] = atts[i]["ES"]
    print()
    print("------------------------")
    # --------------------backward
    path.reverse()
    for i in path:
        if(data.iloc[i, 1] != "-"):
            for k in range(len(data.iloc[i, 1])):
                if "LF" in atts[ord(data.iloc[i, 1][k]) - 65].keys():
                    atts[ord(data.iloc[i, 1][k]) - 65]["LF"] = min(atts[i]
                                                                   ["LS"], atts[ord(data.iloc[i, 1][k]) - 65]["LF"])
                else:
                    atts[ord(data.iloc[i, 1][k]) -
                         65]["LF"] = atts[i]["LS"]
                atts[ord(data.iloc[i, 1][k]) - 65]["LS"] = atts[ord(data.iloc[i, 1]
                                                                    [k]) - 65]["LF"] - atts[ord(data.iloc[i, 1][k]) - 65]["DU"]
        atts[i]["SK"] = atts[i]["LF"] - atts[i]["EF"]
    # ----------------------------------------
    atts[-1]["Name"] = "End"
    for j in range(len(graph)):
        print(atts[j])

    gg = nx.DiGraph()
    for i in range(len(graph)):
        for j in graph[i]:
            gg.add_edge(atts[i]["Name"], atts[j]["Name"])

    temp = []
    for i in range(len(atts)):
        temp.append(atts[i]["Name"])
    temp = dict(zip(temp, atts))
    nx.set_node_attributes(gg, temp)

    fig, ax = plt.subplots(figsize=(15, 15))

    pos = nx.shell_layout(gg)
    # pos = nx.nx_agraph.pygraphviz_layout(gg, prog='dot')

    nx.draw(gg, pos=pos)
    nx.draw_networkx_edges(gg,pos=pos)

    crt = []
    notcrt = []
    for j, i in temp.items():
        if(i["LF"] == i["EF"]):
            crt.append(j)
        else:
            notcrt.append(j)
    nx.draw_networkx_nodes(gg, pos=pos,node_size=2000,
                           node_color='seagreen', ax=ax, nodelist=crt)
    nx.draw_networkx_nodes(gg, pos=pos, node_size=1000,
                           node_color='wheat', ax=ax, nodelist=notcrt)
    nx.draw_networkx_labels(gg, pos=pos, ax=ax, font_weight="bold",
                            font_color="black", font_size=16)

    def without(d, keys={"Name"}):
        return {x: d[x] for x in d if x not in keys}
    for node in gg.nodes:
        xy = pos[node]
        node_attr = gg.nodes[node]
        d = gg.nodes[node]
        d = without(d)
        text = '\n'.join(f'{k}: {v}' for k,
                         v in d.items())
        ax.annotate(text, xy=xy, xytext=(50, 5), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="lightgrey"),
                    arrowprops=dict(arrowstyle="wedge"))
    ax.axis('off')
    

    st.write("Jalur Kritis Aktivitas : ",*crt)
    plt.savefig('image.png')
    image = Image.open('./image.png')
    st.image(image)
    
