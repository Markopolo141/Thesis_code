import json

f = open("directed_graph.json","r")
data = json.load(f)
f.close()

xmultiplier = 0.5*0.40
ymultiplier = 0.3*0.80
point_size = "0.8pt"
circle_size = "0.08"
scale_box_size = "0.25"
circle_outside_color = "black"
circle_color = "white"

f = open("directed_graph1.tex","w")

for i,j in data['edges']:
	f.write("\\draw[line width={}] ({},{}) -- ({},{});\n".format(
		point_size,
		data['nodes'][i][0]*xmultiplier,
		data['nodes'][i][1]*ymultiplier,
		data['nodes'][j][0]*xmultiplier,
		data['nodes'][j][1]*ymultiplier
	))
for i,pos in data['nodes'].items():
	f.write("\\draw[{},fill={}] ({},{}) circle ({});\n".format(circle_outside_color,circle_color,pos[0]*xmultiplier,pos[1]*ymultiplier,circle_size))
	#f.write("\\node (text) at ({},{}) {{\scalebox{{{}}}{{{}}}}};\n".format(pos[0]*xmultiplier,pos[1]*ymultiplier,scale_box_size,i))

f.close()
