from XGeN.InfoExtract.TopicExtractor import TopicExtractor
from XGeN.QAGen.Loader import Loader

payload = {
    "input_text": """research work is precisely focusing on filling this gap by building patient-based simulators [21, 9, 12].
        When other segmentation techniques fail and when deep-learning techniques lack of labeled data,

        segmenting 3D organs with low contrast is still an open problem. Various approaches exist and state-
        of-the-art techniques are atlas-based models [10] and machine-learning based methods [20]. They

        rely on a consequent database that is not always available. In the following we will only focus on
        techniques efficient on a small amount of data.
        Considering that the image is defined on a regular grid of pixels in 2D (resp. voxels in 3D), the
        aim of the image segmentation is the computation of N sets of pixels (resp. voxels) such that each
        set corresponds to an area of the image (these sets are called classes). These areas are computed
        considering contours, shapes, or statistics of their pixels (resp. voxels).
        In the literature, two types of image segmentation methods can be distinguished, based on the
        discretization of the data. The first one is based on the natural regular grid definition of the image,
        in pixels or in voxels. The second one is based on the discretization of the boundary of the pixels
        sets. The first type has been widely used in the seminal segmentation approaches, especially with
        thresholding methods (see, e.g., [18] for a review of such techniques). One of the most known methods
        is Otsu’s method, based on histograms [15]. Avoiding the dependency of the pixel discretization, the
        freely deformable models are based on a discretization of the boundary of the pixel classes. Kass et
        al. [8] have introduced such models for image segmentation in a method called snakes, based on the
        energy minimization. The minimizer provides a trade-off between a regular shape and a data-driven
        one. The concept has been extended in 3 dimensions by Terzopoulos et al. [19].
        The level-set approaches have been introduced by Osher and Sethian [14] and popularized for
        image analysis and computer vision by Malladi et al. [11]. In these methods, the boundary of the
        shape of interest is defined as the level-set of a function, which is considered as the minimizer of
        an energy. For these approaches, two variants exist, which are variational approaches (see, e.g., [4])
        and a PDE approach [14]. These methods favor a regular level-set and are able to naturally tackle
        the issue of topology variations, whereas the free deformable models preserve the initial topology of
        the shape. While the preservation of the topology can be seen as an advantage, especially when the
        interest object is known (e.g., the lungs), the free-deformable approach has been extended to manage
        some changes of topology [13]. In this paper, we will focus on the free deformable model with fixed
        topology.
        In the following we will focus on the 2D formalization in Section 2, and the numerical computation
        of a solution in Section 3. It will be then extended to the 3D case in Section 5. The numerical results
        as well as the influence of the parameters will be studied in Section 4 (2D) and in Section 6 (3D).""",
    "topics_num": 10
}


# loader = Loader()
topicExtractor = TopicExtractor()


keywords = topicExtractor.extract_keywords(payload)
print(keywords)