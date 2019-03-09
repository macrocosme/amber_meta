from matplotlib import pyplot as plt
from pandas.plotting import scatter_matrix
import seaborn as sns
sns.set(style="ticks")

"""
.. module:: amber_plot
   :platform: Unix, Windows
   :synopsis: Module to plot single radio pulse results

.. moduleauthor:: D. Vohl <vohl@astron.nl>


"""

def plot(df, column1='DM', column2='SNR', output_name='../plot.pdf'):
    plt.clf()
    plt.plot(df[column1], df[column2])
    plt.xlabel = column1
    plt.ylabel = column2
    plt.savefig(output_name)

def scatter(df, column1='DM', column2='SNR', output_name='../scatter.pdf'):
    plt.clf()
    plt.scatter(df[column1], df[column2])
    plt.xlabel = column1
    plt.ylabel = column2
    plt.savefig(output_name)

def bar(df, column1='DM', column2='SNR', output_name='../bar.pdf'):
    plt.clf()
    plt.bar(df[column1], df[column2])
    plt.xlabel = column1
    plt.ylabel = column2
    plt.savefig(output_name)

def corr(df, output_name='../corr.pdf'):
    plt.clf()
    plt.matshow(df.corr())
    plt.savefig(output_name)

def pairplot(df, output_name='../pairplot.pdf'):
    plt.clf()
    sns.pairplot(df)
    plt.tight_layout()
    plt.savefig(output_name)

def plot_corr(df,size=10, output_name='corr.pdf'):
    """Function plots a graphical correlation matrix for each pair of columns in the dataframe.

    Input:
        df: pandas DataFrame
        size: vertical and horizontal size of the plot"""
    plt.clf()
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(size, size))
    ax.matshow(corr)
    plt.xticks(range(len(corr.columns)), corr.columns)
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.savefig(output_name)
