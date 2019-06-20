import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

random_state = 1

# Get X, y arrays from dataframe
df = pd.read_csv('data.csv')
y = np.array(df['diagnosis'] == 'M').astype(int)
X = np.array(df)[:, 2:-1]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=random_state)

def fit_and_score_clfs(clfs, X=X, y=y, test_size=0.5):
    '''
        Given a dict of classifiers, return a dict of scores obtained by fitting each classifier
        on the set (X, y) with the given test_proportion

        clfs: dict of classifiers
                key: name of clf
                value: clf object
    '''
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    scores = dict()
    for name, clf in clfs.items():
        clf.fit(X_train, y_train)
        scores[name] = clf.score(X_test, y_test)

    return scores

def plot_test_size_influence_over_score(clfs, min_proportion=.1, max_proportion=.9, N=10, X=X, y=y):
    '''
        Plot the influence of test_size over scores obtained with the given classifiers on the given dataset (X, y)
        
        clfs: dict of classifiers
                key: name of clf
                value: clf object
    '''
    scores_dict = {name:list() for name in clfs.keys()}
    prop_list = np.linspace(min_proportion, max_proportion, N)

    for test_size in prop_list:
        print(test_size)
        new_scores = fit_and_score_clfs(clfs, X=X, y=y, test_size=test_size)
        for name, score in scores_dict.items():
            score.append(new_scores[name])


    for name, scores_list in scores_dict.items():
        plt.plot(prop_list, scores_list, label=name)

    plt.legend()
    plt.xlabel('Test proportion')
    plt.ylabel('Score')
    plt.show()

def find_optimal_dimension(data, explained_proportion, show=False):
    '''
        Return how many dimensions to keep to explain a given proportion of the data.
        Informative purpose only since this feature is already implemented in sklearn.
        Use PCA(n_components=explained_proportion) instead.

        data : array of shape (n_samples, n_features)
        explained_proportion : float in [0, 1]
    '''
    pca = PCA()

    # Important : Normalize data to have homogenous features
    pipeline = Pipeline([('scaling', StandardScaler()), ('pca', pca)])
    data = pipeline.fit_transform(data)

    # Determine how many components to keep
    explained_ratio = np.cumsum(pca.explained_variance_ratio_)
    for k in range(len(explained_ratio)):
        if explained_ratio[k] >= explained_proportion:
            p=k+1
            break
    print('Keeping {} components to explain {}% of the variance'.format(p, 100*explained_proportion))

    if show:
        eigen_values = pca.explained_variance_
        plt.plot(range(len(eigen_values)), eigen_values)
        plt.axvline(p, c='orange')
        plt.xlabel('Eigenvalue index')
        plt.ylabel('Eigenvalue')
        plt.title('Keeping {} components to explain {}% of the variance'.format(p, 100*explained_proportion))
        plt.show()        

    return p

def apply_PCA(data, explained_proportion=None):
    '''
        Given a data array, normalize the data, apply PCA and reduce the dimension to
        explain the given proportion of variance.

        data : array of shape (n_samples, n_features)
        explained_proportion : float in [0, 1]
    '''
    pca = PCA(n_components=explained_proportion)

    # Important : Normalize data to have homogenous features
    pipeline = Pipeline([('scaling', StandardScaler()), ('pca', pca)])
    data = pipeline.fit_transform(data)
    return data

if __name__ == '__main__':

    clfs = {
        'RandomForestClassifier': RandomForestClassifier(n_estimators=100, random_state=random_state),
        'LogisticRegression': LogisticRegression(solver='lbfgs', random_state=random_state),
        'LinearSVC': LinearSVC(max_iter= 1000, random_state=random_state),
        'GradientBoostingClassifier': GradientBoostingClassifier(random_state=random_state)
    }

    print('Scores on raw data :')
    print(fit_and_score_clfs(clfs, X=X))

    explained_proportion = .99
    opt_dim = find_optimal_dimension(X, explained_proportion, show=True)
    X_PCA = apply_PCA(X, explained_proportion=explained_proportion)

    print('Scores on PCA data reduced to {} dimensions to explain {}% of the variance :'.format(X_PCA.shape[1], explained_proportion))
    print(fit_and_score_clfs(clfs, X=X_PCA))
