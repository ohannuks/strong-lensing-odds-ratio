from sklearn.preprocessing import QuantileTransformer, PowerTransformer
from sklearn.neighbors import KernelDensity

class KernelDensityTransformed(KernelDensity):
    def __init__( self, *, bandwidth='scott', algorithm="auto", kernel="gaussian", metric="euclidean", atol=0, rtol=0, breadth_first=True, leaf_size=40, metric_params=None, pt=QuantileTransformer(output_distribution='normal')):
        # Call the parent init with the same arguments
        super(KernelDensityTransformed, self).__init__(bandwidth=bandwidth, algorithm=algorithm, kernel=kernel, metric=metric, atol=atol, rtol=rtol, breadth_first=breadth_first, leaf_size=leaf_size, metric_params=metric_params)
        # Define the transformation
        self.pt = pt
    def fit(self, X, y=None, sample_weight=None):
        # Get the data
        data = X
        # Transform data
        data_transformed = self.pt.fit_transform(data)
        # Call the parent fit
        return super(KernelDensityTransformed, self).fit(data_transformed, y=y, sample_weight=sample_weight)
    def sample(self, n_samples=1, random_state=None):
        data_kde_transformed = super(KernelDensityTransformed, self).sample(n_samples=n_samples, random_state=random_state)
        data_kde = self.pt.inverse_transform(data_kde_transformed)
        return data_kde
    def score_samples(self, X):
        # Get the data
        data = X
        # Transform data
        data_transformed = self.pt.fit_transform(data)
        # Call the parent score_samples
        return super(KernelDensityTransformed, self).score_samples(data_transformed)


