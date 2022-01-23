import graph
import numpy as np
from matplotlib import pyplot as plt

class MRF:
    def __init__(self):
        self.g = graph.Graph()

    def im2graph(self, im):
        """
        Transform the image pixels into a Linked List
        This is a sparse representation of the image
        Each pixel is linked only to its 8-neighbors
        """
        h,w = im.shape
        self.output = np.zeros((h,w), dtype=np.uint8)
        border = np.ones_like(im, dtype=np.uint8)

        border[1:-1, 1:-1] = 0

        all_nodes = []
        unary_term_0 = []
        unary_term_1 = []

        binary_term = 0.5
        cursor = 2

        for i in range(h):
            for j in range(w):

                # Unary Term
                U0 = cost(1-im[i,j])
                U1 = cost(im[i,j])

                all_nodes.append(cursor)
                unary_term_0.append(U0)
                unary_term_1.append(U1)

                capacity = [U0, U1]
                neighbors = [0, 1]

                if not border[i,j]:
                    neighbors.extend([cursor-w-1, cursor-w, cursor-w+1, cursor-1, cursor+1, cursor+w-1, cursor+w, cursor+w+1])
                else:
                    neighbors.extend(border_neighbors(cursor, i, j, h, w))

                
                capacity.extend([binary_term for n in neighbors[2:]])

                self.g.add_node(cursor, neighbors, capacity)
                cursor += 1

        self.g.add_node(0, all_nodes, unary_term_0)
        self.g.add_node(1, all_nodes, unary_term_1)

    def solve(self):
        self.g.mincut_maxflow()

    def graph2im(self):
        """
        Rebuild the output image from the linked list representation
        1) Start at the sink
        2) Any pixel with a residual path to the sink is labeled 1
        3) Traverse the linked list until the flow is blocked (no residuals)
        4) Remaining pixels are labeled 0
        """
        nodes = self.g.nodes

        coordx, coordy = np.meshgrid(np.arange(self.output.shape[0]), np.arange(self.output.shape[1]))
        visited = np.zeros_like(coordy)
        coordy = coordy.flatten()
        coordx = coordx.flatten()

        queue = [1]
        
        while queue:
            node = nodes[queue.pop(0)]
            for n_i in range(len(node.neighbors)):
                n = node.neighbors[n_i]

                if n > 1:
                    edge = node.edges[n]
                    
                    i = coordy[n-2]
                    j = coordx[n-2]

                    if not visited[i,j]:
                        queue.append(n)
                        if edge.flow < edge.c:
                            self.output[i,j] = 1

                    visited[i,j] |= 1

        return self.output

def border_neighbors(cursor, i, j, h, w):
    """
    Utility function for pixels that don't have an 8-neighborhood
    """
    if i == 0:
        if j == 0:
            l = [cursor+1, cursor+w, cursor+w+1]
        elif j == w-1:
            l = [cursor-1, cursor+w, cursor+w-1]
        else:
            l = [cursor-1, cursor+1, cursor+w-1, cursor+w, cursor+w+1]

    elif i == h-1:
        if j == 0:
            l = [cursor-w-1, cursor-w+1, cursor+1]
        elif j == w-1:
            l = [cursor-w-1, cursor-w, cursor-1]
        else:
            l = [cursor-w-1, cursor-w, cursor-w+1, cursor-1, cursor+1]

    elif j == 0:
        l = [cursor-w, cursor-w+1, cursor+1, cursor+w, cursor+w+1]

    else:
        l = [cursor-w-1, cursor-w, cursor-1, cursor+w-1, cursor+w]

    return l

def test_image(noise_level=0.3):
    """
    Generate a sample image
    """
    test_im = np.zeros((50, 50), dtype=np.float32)
    cx1 = test_im.shape[1]//4
    cx2 = cx1*3
    cy = test_im.shape[0]//2
    w = 5
    
    test_im[cy-w:cy+w+1, cx1-w:cx1+w+1] = 1
    test_im[cy-w:cy+w+1, cx2-w:cx2+w+1] = 1

    test_im += np.random.normal(loc=0, scale=noise_level, size=test_im.shape)
    test_im = (test_im - test_im.min()) / (test_im.max() - test_im.min())
    return test_im

def likelihood(x, noise_var=0.09):
    return np.exp(-((x)**2)/(2*noise_var))

def cost(x):
    p = likelihood(x)
    return -np.log(p)

if __name__ == "__main__":
    m = MRF()
    im = test_image()
    m.im2graph(im)
    m.solve()
    output = m.graph2im()

    plt.subplot(121)
    plt.title('Input Image')
    plt.imshow(im, cmap='gray')
    plt.axis('off')
    plt.subplot(122)
    plt.title('MRF Segmentation')
    plt.imshow(output, cmap='gray')
    plt.axis('off')
    plt.show()