import pickle
import bilby
from kde import KernelDensityTransformed
from sklearn.preprocessing import QuantileTransformer, PowerTransformer
import pandas as pd
import numpy as np

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

def build_kde(posterior, parameters, log_weights=None):
    ''' Build KDEs for the posteriors

    Parameters
    posterior: Posterior parameters
    parameters: List of parameters
    log_weights: ln weights for each sample

    Returns
    kde
    '''
    if log_weights is None:
        sample_weight = None
    else:
        sample_weight = np.exp(log_weights-np.max(log_weights))
        sample_weight = sample_weight/np.sum(sample_weight)
    # Now build the kdes
    kde = KernelDensityTransformed(bandwidth='silverman', leaf_size=100, pt=QuantileTransformer(output_distribution='normal'))
    kde.fit(posterior[parameters], sample_weight=sample_weight)
    return kde


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

def add_chirp_mass_mass_ratio_to_samples(samples):
    ''' Add chirp mass and mass ratio to a set of samples

    Parameters
    samples: pandas DataFrame object containing samples

    Returns
    samples: pandas DataFrame object containing samples with chirp mass and mass ratio added

    Example:
    outdir='outdir'
    labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)
    kdes_15d, kdes_eff = build_kdes(posteriors, parameters_15d, parameters_eff)
    samples = kde_sample(kdes_15d[0], parameters_15d)
    samples = add_chirp_mass_mass_ratio_to_samples(samples)
    '''
    # Compute chirp mass, mass ratio
    samples['chirp_mass'] = bilby.gw.conversion.component_masses_to_chirp_mass(samples['mass_1'], samples['mass_2'])
    samples['mass_ratio'] = bilby.gw.conversion.component_masses_to_mass_ratio(samples['mass_1'], samples['mass_2'])
    return samples

def get_all_samples(samples, other_samples, i, parameters_eff, n_kdes):
    # First copy the samples over 
    samples_full = samples.copy()
    # Now rename the effective parameters to parameters_eff_i
    for j, parameter in enumerate(parameters_eff):
        samples_full['{}_{}'.format(parameter, i)] = samples_full[parameter]
        del samples_full[parameter]
    # Then add in the other effective parameters
    j0 = 0
    for j in range(n_kdes):
        if i == j:
            continue
        for parameter in parameters_eff:
            samples_full['{}_{}'.format(parameter, j)] = other_samples[j0][parameter]
        j0 = j0 + 1
    return samples_full

def get_this_and_other_kde(posterior_kdes, posterior_kdes_eff, priors, i):
    n_kdes = len(posterior_kdes)
    this_kde = posterior_kdes[i]
    this_kde_eff = posterior_kdes_eff[i]
    this_prior = priors[i]
    # Loop over all other kdes
    other_kdes = []
    other_kdes_eff = []
    other_priors = []
    for j in range(n_kdes):
        if i == j:
            continue
        other_kdes.append(posterior_kdes[j])
        other_kdes_eff.append(posterior_kdes_eff[j])
        other_priors.append(priors[j])
    return this_kde, other_kdes, this_kde_eff, other_kdes_eff, this_prior, other_priors

def get_log_kde_values(kde, kde_eff, prior, samples, parameters_15d, parameters_eff):
    # Evaluate the kdes at the samples
    log_pos = kde.score_samples(samples[parameters_15d])
    # Do the same for the effective parameters
    log_pos_eff = kde_eff.score_samples(samples[parameters_eff])
    # Evaluate the prior log probabilities
    samples = add_chirp_mass_mass_ratio_to_samples(samples)
    log_prior = prior.ln_prob(samples, axis=0)
    # Evaluate the prior log probabilities for the effective parameters
    prior_eff = bilby.core.prior.PriorDict()
    for parameter in parameters_eff:
        prior_eff[parameter] = prior[parameter]
    log_prior_eff = prior_eff.ln_prob(samples[parameters_eff], axis=0)
    return log_pos, log_pos_eff, log_prior, log_prior_eff
def get_log_kde_values_list(kdes, kdes_eff, priors, samples, parameters_15d, parameters_eff):
    n_kdes = len(kdes)
    log_pos_list = []
    log_pos_eff_list = []
    log_prior_list = []
    log_prior_eff_list = []
    for i in range(n_kdes):
        log_pos, log_pos_eff, log_prior, log_prior_eff = get_log_kde_values(kdes[i], kdes_eff[i], priors[i], samples, parameters_15d, parameters_eff)
        log_pos_list.append(log_pos)
        log_pos_eff_list.append(log_pos_eff)
        log_prior_list.append(log_prior)
        log_prior_eff_list.append(log_prior_eff)
    # Sum the log probabilities at axis=0
    log_pos = np.sum(log_pos_list, axis=0)
    log_pos_eff = np.sum(log_pos_eff_list, axis=0)
    log_prior = np.sum(log_prior_list, axis=0)
    log_prior_eff = np.sum(log_prior_eff_list, axis=0)
    return log_pos, log_pos_eff, log_prior, log_prior_eff


def joint_kde_analysis(posterior_kdes, posterior_kdes_eff, priors, parameters_15d, parameters_eff, n_samples=100000):
    ''' Joint KDE analysis. 

    Parameters
    posterior_kdes: List of KDEs for the 15d parameters
    posterior_kdes_eff: List of KDEs for the effective parameters
    parameters_15d: List of 15d parameters
    parameters_eff: List of effective parameters
    n_samples: Number of samples to draw from the KDEs

    Returns
    joint_kde, samples, log_weights

    Example:
    outdir='outdir'
    labels = [ 'injection_1_image_0', 'injection_1_image_1', 'injection_1_image_2', 'injection_1_image_3']
    results, waveform_arguments, waveform_generators, priors, ifos, likelihoods, posteriors = load_all_results(outdir, labels)
    kdes_15d, kdes_eff = build_kdes(posteriors, parameters_15d, parameters_eff)
    joint_kde, joint_kde_eff, joint_kde_15d = joint_kde_analysis(kdes_15d, kdes_eff, parameters_15d, parameters_eff)
    '''
    n_kdes = len(posterior_kdes)
    samples_all = []
    log_weights_all = []
    for i in range(n_kdes):
        this_kde, other_kdes, this_kde_eff, other_kdes_eff, this_prior, other_priors = get_this_and_other_kde(posterior_kdes, posterior_kdes_eff, priors, i)
        # Sample from this kde
        samples = kde_sample(this_kde, parameters_15d, n_samples=n_samples)
        # Now sample from the other kdes with effective parameters only
        other_samples_eff = [kde_sample(kde, parameters_eff, n_samples=n_samples) for kde in other_kdes_eff]
        # Copy over the samples to other samples but replace the effective samples with the other_samples_eff
        other_samples = [samples.copy() for kde_eff in other_kdes_eff]
        for j in range(n_kdes-1):
            other_samples[j][parameters_eff] = other_samples_eff[j][parameters_eff]
        # Get the log posterior, log posterior effective, log prior, and log prior effective values
        log_pos_this, log_pos_this_eff, log_prior_this, log_prior_this_eff = get_log_kde_values(this_kde, this_kde_eff, this_prior, samples, parameters_15d, parameters_eff)
        log_pos_others, log_pos_others_eff, log_prior_others, log_prior_others_eff = get_log_kde_values_list(other_kdes, other_kdes_eff, other_priors, samples, parameters_15d, parameters_eff)
        # Now add up the log probabilities
        log_pos = log_pos_this + log_pos_others
        log_prior = log_prior_this + log_prior_others
        log_pos_eff = log_pos_this_eff + log_pos_others_eff
        log_prior_eff = log_prior_this_eff + log_prior_others_eff
        # Compute the weights
        log_weight = log_pos - log_prior # Add the log likelihoods 
        log_weight = log_weight + log_prior_this + log_prior_others_eff
        log_weight = log_weight - log_pos_this - log_pos_others_eff
        # Save the log weights
        log_weights_all.append(log_weight)
        # Define the full samples
        samples_full = get_all_samples(samples, other_samples, i, parameters_eff, n_kdes)
        samples_all.append(samples_full)
    # Now combine the samples and weights
    samples_all = np.concatenate(samples_all, axis=0)
    log_weights_all = np.concatenate(log_weights_all, axis=0)
    # Now build the joint KDE
    joint_kde = build_kde(samples_all, parameters_15d, log_weights=log_weights_all)
    return joint_kde, samples_all, log_weights_all

