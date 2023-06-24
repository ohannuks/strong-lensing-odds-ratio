import pickle
import bilby
from kde import KernelDensityTransformed
from sklearn.preprocessing import QuantileTransformer, PowerTransformer
import pandas as pd

def load_bilby_arguments(filename):
    ''' Load a pickle file containing a dictionary of arguments for bilby

    Parameters
    filename: Filename of the pickle file

    Returns
    waveform_arguments, waveform_generator, priors, ifos, likelihood
    '''
    with open(filename, 'rb') as f:
        waveform_arguments, waveform_generator, priors, ifos, likelihood = pickle.load(f)
    return waveform_arguments, waveform_generator, priors, ifos, likelihood

def load_all_results(outdir, labels):
    ''' Load all results from a directory

    Parameters
    outdir: Directory containing the results
    labels: List of labels for the results

    Returns
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors

    Example:
    outdir='outdir'
    labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)
    '''
    # Read in results
    results = []
    waveform_arguments = []
    waveform_generators = []
    priors = []
    ifos = []
    likelihoods = []
    posteriors = []
    for label in labels:
        result = bilby.read_in_result(outdir=outdir, label=label)
        filename = f"{outdir}/{label}_bilby_arguments.pkl"
        waveform_args, waveform_gen, prior, ifo, like = load_bilby_arguments(filename)
        results.append(result)
        waveform_arguments.append(waveform_args)
        waveform_generators.append(waveform_gen)
        priors.append(prior)
        ifos.append(ifo)
        likelihoods.append(like)
        posteriors.append(result.posterior)
    return results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors

def build_kdes(posteriors, parameters_15d, parameters_eff):
    ''' Build KDEs for the posteriors

    Parameters
    posteriors: List of posteriors
    parameters_15d: List of 15d parameters
    parameters_eff: List of effective parameters

    Returns
    kdes_15d, kdes_eff

    Example:
    outdir='outdir'
    labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)
    kdes_15d, kdes_eff = build_kdes(posteriors, parameters_15d, parameters_eff)
    '''
    # Now build the kdes
    posterior_kdes = []
    posterior_kdes_eff = []
    for i in range(4):
        posterior_kdes.append(KernelDensityTransformed(bandwidth='silverman', leaf_size=100, pt=QuantileTransformer(output_distribution='normal')))
        posterior_samples = posteriors[i][parameters_15d]
        posterior_kdes[i].fit(posterior_samples)
        posterior_kdes_eff.append(KernelDensityTransformed(bandwidth='silverman', leaf_size=100, pt=QuantileTransformer(output_distribution='normal')))
        posterior_samples_eff = posteriors[i][parameters_eff]
        posterior_kdes_eff[i].fit(posterior_samples_eff)
    return posterior_kdes, posterior_kdes_eff

def kde_sample(kde, parameters, n_samples=10000):
    ''' Sample from a KDE and build a pandas object

    Parameters
    kde: KDE to sample from
    parameters: List of parameters to sample

    Returns
    pandas DataFrame object

    Example:
    outdir='outdir'
    labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)
    kdes_15d, kdes_eff = build_kdes(posteriors, parameters_15d, parameters_eff)
    samples = kde_sample(kdes_15d[0], parameters_15d)
    '''
    samples = kde.sample(n_samples)
    df = pd.DataFrame(samples, columns=parameters)
    return df

def joint_kde_analysis(posterior_kdes, posterior_kdes_eff, parameters_15d, parameters_eff, n_samples=100000):
    ''' Joint KDE analysis. 

    Parameters
    posterior_kdes: List of KDEs for the 15d parameters
    posterior_kdes_eff: List of KDEs for the effective parameters
    parameters_15d: List of 15d parameters
    parameters_eff: List of effective parameters
    n_samples: Number of samples to draw from the KDEs

    Returns
    joint_kde, joint_kde_eff, joint_kde_15d

    Example:
    outdir='outdir'
    labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)
    kdes_15d, kdes_eff = build_kdes(posteriors, parameters_15d, parameters_eff)
    joint_kde, joint_kde_eff, joint_kde_15d = joint_kde_analysis(kdes_15d, kdes_eff, parameters_15d, parameters_eff)
    '''
    n_kdes = len(posterior_kdes)
    for i in range(n_kdes):
        this_kde = posterior_kdes[i]
        this_kde_eff = posterior_kdes_eff[i]
        # Loop over all other kdes
        other_kdes = []
        other_kdes_eff = []
        for j in range(n_kdes):
            if i == j:
                continue
            other_kdes.append(posterior_kdes[j])
            other_kdes_eff.append(posterior_kdes_eff[j])
        # Sample from this kde
        samples = kde_sample(this_kde, parameters_15d, n_samples=n_samples)
        # Now sample from the other kdes with effective parameters only
        other_samples_eff = [kde_sample(kde, parameters_eff, n_samples=n_samples) for kde in other_kdes_eff]
        # Copy over the samples to other samples but replace the effective samples with the other_samples_eff
        other_samples = [samples.copy() for kde_eff in other_kdes_eff]
        for j in range(n_kdes-1):
            other_samples[j][parameters_eff] = other_samples_eff[j][parameters_eff]
        


