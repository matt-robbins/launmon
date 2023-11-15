from matplotlib import pyplot as plt
from matplotlib.widgets import SpanSelector
import matplotlib
import numpy as np
from scipy import signal
import db

if __name__ == "__main__":

    matplotlib.use('TkAgg')
    db = db.LaundryDb()

    res = db.fetch("SELECT current FROM rawcurrent WHERE location = '4' ORDER BY time")
    c1 = np.array([c[0] for c in res])

    w = np.hanning(121)
    w = w / np.sum(w)
    c1f = signal.lfilter(w,1,c1)

    c1_subset = c1[c1f > 30]
    print(len(c1_subset))

    fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 6))
    
    ax1.plot(c1_subset)
    line2, = ax2.plot([], [])

    FileIx = 0

    class OnSelect(object):
        def __init__(self, data):
            self.FileIx = 0
            self.data = data
        def __call__(self, xmin,xmax):
            print(xmin,xmax)
            # Manipulate the data
            with open("train/file_%d" % (self.FileIx,), 'w') as f:
                lines = ["%.3f\n" % (x,) for x in self.data[int(xmin):int(xmax)]]
                f.writelines(lines)
            self.FileIx += 1

    cb = OnSelect(c1_subset)

    span = SpanSelector(
        ax1,
        cb,
        "horizontal",
        useblit=True,
        props=dict(alpha=0.5, facecolor="tab:blue"),
        interactive=True,
        drag_from_anywhere=True
    )

    plt.show()
    plt.ion()

        




    # matplotlib.use('TkAgg')
    # bow = sp.get_training_bow()

    # pca = PCA(n_components=3)
    # X = pca.fit_transform(bow["X"])

    # neigh = KNeighborsClassifier(n_neighbors=3)
    # neigh.fit(X,bow["Y"])

    # Yprime = neigh.predict(X)

    # print(sum(np.array(Yprime) == np.array(bow["Y"]))/len(bow["X"]))

    # labels = set(bow["Y"])
    # for l in labels:
    #     x = np.array(X)
    #     y = np.array(bow["Y"])
    #     lx = x[y==l]
    #     plt.scatter([p[0] for p in lx],[p[1] for p in lx], marker=".",alpha=0.3)
        

    # plt.show()
    # plt.ion()



        

