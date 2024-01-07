from ektelo.algorithm.privBayes import privBayesSelect
import numpy as np
from util import Dataset, Factor, FactoredInference, mechanism
from ektelo.matrix import Identity
import pandas as pd
import itertools
import argparse
import benchmarks
import os
import json
import sys
import matplotlib.pyplot as plt

"""
This file implements PrivBayes.

Zhang, Jun, Graham Cormode, Cecilia M. Procopiuc, Divesh Srivastava, and Xiaokui Xiao. "Privbayes: Private data release via bayesian networks." ACM Transactions on Database Systems (TODS) 42, no. 4 (2017): 25.
"""

def get_dataset_file(dataset_name):
    dataset_folder = '/privbayes-implementation/Privbayes/data/'
    csv_file = f'{dataset_folder}{dataset_name}.csv'
    
    # Check if the CSV file exists
    if os.path.isfile(csv_file):
        return csv_file
    else:
        print(f"{dataset_name}.csv not found.")
        sys.exit(1)



def preprocess(original_dataset):
    # Load your dataset
    data = pd.read_csv(original_dataset)

    # Extract file name from the path (without extension)
    file_name = os.path.splitext(os.path.basename(original_dataset))[0]

    # Output directory path
    output_directory = '/privbayes-implementation/Privbayes/data/preprocessed-output/'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Output file names
    processed_output_file = output_directory + f'preprocessed_{file_name}.csv'
    domain_output_file = output_directory + f'domain_{file_name}.json'
    domain_correlation_file = output_directory + f'domain_correlation_{file_name}.json'

    # Check if processed output file exists, if yes, remove it
    if os.path.isfile(processed_output_file):
        os.remove(processed_output_file)

    # Check if domain output file exists, if yes, remove it
    if os.path.isfile(domain_output_file):
        os.remove(domain_output_file)

    # Check if domain correlation file exists, if yes, remove it
    if os.path.isfile(domain_correlation_file):
        os.remove(domain_correlation_file)

    # Initialize an empty dictionary to store domain values for each column
    domain_values = {}
    domain_correlation_values = {}

    # Categorize columns and generate domain values
    processed_data = data.copy()
    for column in data.columns:
        # Create a mapping of unique categorical values to numeric labels
        unique_values = data[column].unique()
        value_mapping = {val: idx + 1 for idx, val in enumerate(unique_values)}

        # Map categorical values to numeric labels in the dataset
        processed_data[column] = processed_data[column].map(value_mapping)

        # Convert int64 values to native int before storing in domain_values
        unique_values = [val.item() if isinstance(val, np.int64) else val for val in unique_values]

        # Store the mapping information in the domain_values dictionary
        domain_values[column] = {str(idx + 1): val for idx, val in enumerate(unique_values)}
        domain_correlation_values[column] = len(unique_values)

    # Save the processed dataset with categorization to the output directory
    processed_data.to_csv(processed_output_file, index=False)

    # Save domain values as a JSON file in the output directory
    with open(domain_output_file, 'w') as json_file:
        json.dump(domain_correlation_values, json_file)

    # Save domain correlation values as a JSON file in the output directory
    with open(domain_correlation_file, 'w') as json_file:
        json.dump(domain_values, json_file)

    # Return the processed dataset file paths and file names
    return processed_output_file, domain_output_file, file_name, domain_correlation_file

def postprocess(processed_input_dataset, domain_correlation_file, file_name):
    # Load processed input dataset
    processed_data = pd.read_csv(processed_input_dataset)

    # Load domain correlation values
    with open(domain_correlation_file, 'r') as json_file:
        domain_correlation_values = json.load(json_file)

    # Function to convert processed data back to original form
    def convert_to_original(processed_data, domain_values, file_name):
        for col in processed_data.columns:
            if col in domain_values:
                # Map numerical representation back to original categorical values using domain_values
                processed_data[col] = processed_data[col].astype(str).map(domain_values[col])

        return processed_data

    # Use the function to convert processed data back to its original form
    postprocessed_synthetic_data = convert_to_original(processed_data, domain_correlation_values, file_name)
    output_directory = '/privbayes-implementation/Privbayes/data/postprocessed-output/'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        
    # Save the processed data after postprocessing
    output_file = f'/privbayes-implementation/Privbayes/data/postprocessed-output/final_synthetic_{file_name}.csv'  # Define the output file path
    postprocessed_synthetic_data.to_csv(output_file, index=False)
    print(f"\nProcessed data after postprocessing is saved to: {output_file}")
    #return postprocessed_synthetic_data

import itertools
import pandas as pd
import matplotlib.pyplot as plt

def comparedatasets(input_df, synthetic_df):
    original_columns = input_df.columns.tolist()
    synthetic_columns = synthetic_df.columns.tolist()
    print(original_columns)
    print(synthetic_columns)
    
    # Find common attributes between original and synthetic datasets
    common_attributes = set(original_columns) & set(synthetic_columns)
    
    # Generate attribute pairs for the common attributes
    attribute_pairs = list(itertools.combinations(common_attributes, 2))
    
    # Define a minimum threshold for co-occurrence counts
    min_threshold = 30  # Adjust this threshold as needed
    
    # Create subplots for co-occurrence graphs for each attribute pair
    fig, axs = plt.subplots(len(attribute_pairs), 2, figsize=(15, 5 * len(attribute_pairs)))
    
    for i, attribute_pair in enumerate(attribute_pairs):
        # Calculate the counts of occurrences for each unique pair of values in input_df
        input_attribute_counts = input_df.groupby(list(attribute_pair)).size().reset_index(name='Count')
    
        # Calculate the counts of occurrences for each unique pair of values in synthetic_df
        synthetic_attribute_counts = synthetic_df.groupby(list(attribute_pair)).size().reset_index(name='Count')
    
        # Filter insignificant co-occurrences based on the threshold
        input_attribute_counts = input_attribute_counts[input_attribute_counts['Count'] >= min_threshold]
        synthetic_attribute_counts = synthetic_attribute_counts[synthetic_attribute_counts['Count'] >= min_threshold]
    
        # Update the maximum counts within the current attribute pair for input and synthetic datasets
        max_input_count = input_attribute_counts['Count'].max() if not input_attribute_counts.empty else 0
        max_synthetic_count = synthetic_attribute_counts['Count'].max() if not synthetic_attribute_counts.empty else 0
    
        # Calculate the maximum count across both datasets for the current attribute pair
        max_count_pair = max(max_input_count, max_synthetic_count)
    
        # Adjust minimum limit for the y-axis
        min_limit = 0.1  # Set a small non-zero value to prevent setting the limits to zero
    
        # Plotting the counts of co-occurrences as bar plots for input_df and synthetic_df
        input_plot = axs[i, 0].bar(input_attribute_counts.apply(lambda x: f"{x[attribute_pair[0]]} - {x[attribute_pair[1]]}", axis=1), input_attribute_counts['Count'])
        axs[i, 0].set_xlabel(f"{attribute_pair[0]} - {attribute_pair[1]}")
        axs[i, 0].set_ylabel('Count')
        axs[i, 0].set_title(f"Co-occurrence of {attribute_pair[0]} and {attribute_pair[1]} in input_df")
        axs[i, 0].tick_params(axis='x', rotation=90)
        axs[i, 0].set_ylim(min_limit, max_count_pair * 1.1)  # Set y-axis limits based on the max count of both datasets
    
        synthetic_plot = axs[i, 1].bar(synthetic_attribute_counts.apply(lambda x: f"{x[attribute_pair[0]]} - {x[attribute_pair[1]]}", axis=1), synthetic_attribute_counts['Count'])
        axs[i, 1].set_xlabel(f"{attribute_pair[0]} - {attribute_pair[1]}")
        axs[i, 1].set_ylabel('Count')
        axs[i, 1].set_title(f"Co-occurrence of {attribute_pair[0]} and {attribute_pair[1]} in synthetic_df")
        axs[i, 1].tick_params(axis='x', rotation=90)
        axs[i, 1].set_ylim(min_limit, max_count_pair * 1.1)  # Set y-axis limits based on the max count of both datasets
    
    plt.tight_layout()
    plt.show()






def privbayes_measurements(data, eps=1.0, seed=0):
    
    domain = data.domain
    config = ''
    for a in domain:
        values = [str(i) for i in range(domain[a])]
        config += 'D ' + ' '.join(values) + ' \n'
    config = config.encode('utf-8')
    
    values = np.ascontiguousarray(data.df.values.astype(np.int32))
    print(values)
   
    ans = privBayesSelect.py_get_model(values, config, eps/2, 1.0, seed)
    
    ans = ans.decode('utf-8')[:-1]

    projections = []
    for m in ans.split('\n'):
        p = [domain.attrs[int(a)] for a in m.split(',')[::2]]
        projections.append(tuple(p))
  
    prng = np.random.RandomState(seed) 
    measurements = []
    delta = len(projections)
    for proj in projections:
        x = data.project(proj).datavector()
        I = Identity(x.size)
        y = I.dot(x) + prng.laplace(loc=0, scale=4*delta/eps, size=x.size)
        measurements.append( (I, y, 1.0, proj) )
     
    return measurements

def privbayes_inference(domain, measurements, total, file_name):
    file_name = file_name
    synthetic = pd.DataFrame()
    #print(measurements[0])
    _, y, _, proj = measurements[0]
    y = np.maximum(y, 0)
    y /= y.sum()
    col = proj[0]
    synthetic[col] = np.random.choice(domain[col], total, True, y)
    print("Below Attributes are being measured for Inference")
    
    for _, y, _, proj in measurements[1:]:
        # find the CPT
        col, dep = proj[0], proj[1:]
        print(col)
        y = np.maximum(y, 0)
        dom = domain.project(proj)
        cpt = Factor(dom, y.reshape(dom.shape))
        marg = cpt.project(dep)
        cpt /= marg
        values_array = cpt.project(proj).values
        cpt2 = np.moveaxis(cpt.project(proj).values, 0, -1)
       
        
        # sample current column
        synthetic[col] = 0
        rng = itertools.product(*[range(domain[a]) for a in dep])
        for v in rng:
            idx = (synthetic.loc[:,dep].values == np.array(v)).all(axis=1)
            p = cpt2[v].flatten()
            if p.sum() == 0:
                p = np.ones(p.size) / p.size
            n = domain[col]
            N = idx.sum()
            if N > 0:
                synthetic.loc[idx,col] = np.random.choice(n, N, True, p)
    
    
    output_folder = '/privbayes-implementation/Privbayes/data/synthetic-output/'  # Define the output folder path
    output_filename = f"preprocessed_synthetic_{file_name}.csv"  # Define the output filename

    # Combine output folder path and output filename
    output_path = os.path.join(output_folder, output_filename)

    # Check if the output folder exists, create if not
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Check if the file already exists, remove it
    if os.path.exists(output_path):
        os.remove(output_path)

    # Save synthetic dataset as CSV file in the specified output path
    synthetic.to_csv(output_path, index=False)
    print(f"Synthetic Dataset is created and saved at : {output_path}")
    return Dataset(synthetic, domain)

def default_params():
    """
    Return default parameters to run this program

    :returns: a dictionary of default parameter settings for each command line argument
    """
    params = {}
    params['dataset'] = 'adult'
    params['iters'] = 10000
    params['epsilon'] = 1.0
    params['seed'] = 0

    return params

if __name__ == '__main__':
    dataset_name = input("Enter the dataset name: ").strip()
    
    if not dataset_name:
        print("No dataset name entered. Exiting.")
        sys.exit(1)
    
    original_dataset = get_dataset_file(dataset_name)
    print("=============DATA PRE-PROCESSING=============")
    processed_data, data_domain, file_name, domain_correlation_file  = preprocess(original_dataset)
    print("=============DATA PRE-PROCESSING COMPLETED=============")
    description = ''
    formatter = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(description=description, formatter_class=formatter)
    parser.add_argument('--dataset', choices=['adult'], help='dataset to use')
    parser.add_argument('--iters', type=int, help='number of optimization iterations')
    parser.add_argument('--epsilon', type=float, help='privacy  parameter')
    parser.add_argument('--seed', type=int, help='random seed')

    parser.set_defaults(**default_params())
    args = parser.parse_args()

    data, workload = benchmarks.adult_benchmark(processed_data, data_domain)
    
    total = data.df.shape[0]

    measurements = privbayes_measurements(data, 1.0, args.seed) 
    #print("est function is being run now...")
    est = privbayes_inference(data.domain, measurements, total=total, file_name=file_name)

    elim_order = [m[3][0] for m in measurements][::-1]

    projections = [m[3] for m in measurements]
    est2, _, _ = mechanism.run(data, projections, eps=args.epsilon, frequency=50, seed=args.seed, iters=args.iters)

    def err(true, est):

        return np.sum(np.abs(true - est)) / true.sum()

    err_pb = []
    err_pgm = []
    for p, W in workload:
        true = W.dot(data.project(p).datavector())
        pb = W.dot(est.project(p).datavector())
        pgm = W.dot(est2.project(p).datavector())
        err_pb.append(err(true, pb))
        err_pgm.append(err(true, pgm))

    print('Error of PrivBayes    : %.3f' % np.mean(err_pb))
    print('Error of PrivBayes+PGM: %.3f' % np.mean(err_pgm))

    print("Postprocessing the generated synthetic file..!!")
    postprocess(synthetic_df, domain_correlation_file, file_name)
    print("done..!")

    
    print("\n Now comes the comparing the original and synthetic datasets part..!!")
    synthetic_df = f'/privbayes-implementation/Privbayes/data/synthetic-output/preprocessed_synthetic_{file_name}.csv'
    input_df = f'/privbayes-implementation/Privbayes/data/preprocessed-output/preprocessed_{file_name}.csv'
    original_dataset = f'/privbayes-implementation/Privbayes/data/{file_name}.csv'
    final_synthetic_data = f'/privbayes-implementation/Privbayes/data/postprocessed-output/final_synthetic_{file_name}.csv'
    
    # Load the original dataset before preprocessing and display its head
    original_data_before_preprocess = pd.read_csv(original_dataset)
    print("\nHead of the original dataset before preprocessing:")
    print(original_data_before_preprocess.head())

    # Load the preprocessed dataset and display its head
    preprocessed_data = pd.read_csv(input_df)
    print("\nHead of the preprocessed dataset:")
    print(preprocessed_data.head())

    # Load the synthetic dataset and display its head
    synthetic_data = pd.read_csv(synthetic_df)
    print("\nHead of the synthetic dataset:")
    print(synthetic_data.head())

    # Display the head of the original synthetic dataset (postprocessed synthetic dataset)
    final_synthetic_dataset = pd.read_csv(final_synthetic_data)
    print("\nHead of the final synthetic dataset generated (postprocessed synthetic dataset):")
    print(final_synthetic_dataset.head())

    print("Now comes comparing the datasets, via a 2way occurance check..??")
    
    comparedatasets(original_data_before_preprocess, final_synthetic_dataset)
    print("End")
