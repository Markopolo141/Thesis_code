import json
import click

@click.command()
@click.argument('input_file', type=click.File('r'))
@click.argument('network_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
def run(input_file, network_file, output_file):
	network = json.load(network_file)
	lines = input_file.readlines()
	assert len(lines)>0, "empty file"
	assert len(lines)<2, "file has more than one line"
	l = lines[0]
	l = "[{}".format(l.split("[")[1])
	data = json.loads(l)
	for i in range(len(data)):
		output_file.write("{},{},{}\n".format(network['gen'][i][8]+network['gen'][i][9],network['gencost'][i][4],data[i]))
	print "written output"
	

if __name__ == '__main__':
    run()
