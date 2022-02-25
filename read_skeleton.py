import numpy as np

def main(infile):
    # Define Lists
    verts = []
    edges = []

    with open(infile) as file:
        iterlines = iter(file)
        next(iterlines)
        for line in iterlines:
            comp = line.split(" ")
            if comp[0] == "v":
                verts.append([float(comp[i]) for i in range(1, len(comp))])
            elif comp[0] == "e":
                edges.append([int(comp[i]) for i in range(1, len(comp))])
            else:
                raise ValueError("Line prefix unexpected.")
    file.close()

    verts = np.array(verts)
    edges = np.array(edges)

    return verts, edges

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Read MCF Skeletonization file.')
    parser.add_argument('infile', help='Input .cg text file (output from StarLab)')

    args = parser.parse_args()
    main(args.infile)