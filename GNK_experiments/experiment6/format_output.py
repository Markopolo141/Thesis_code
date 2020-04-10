import json
import click

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
def run(input_file, output_file):
	#data = json.load(f)
	lines = input_file.readlines()
	for l in lines:
		l = "[{}".format(l.split("[")[1])
		data = json.loads(l)
		for i in range(len(data)):
			output_file.write("({},{})".format(i,data[i]))
		output_file.write("\n")
	print "written output"
	

if __name__ == '__main__':
    run()
