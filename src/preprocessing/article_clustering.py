import yaml
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering

from sklearn.manifold import TSNE
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend to avoid display issues
import matplotlib.pyplot as plt


# Load the config file
root_dir = Path(__file__).resolve().parent.parent
config_path = root_dir / "config" / "config.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Access paths from the config file
data_dir = root_dir / config['paths']['data_dir']
model_dir = root_dir / config['paths']['models_dir']
output_dir = root_dir / config['paths']['output_dir']


def cluster_articles(article_similarity_scores_path, method, output_file, num_cluster, plot_path=""):
    # Step 1: Load your data
    df = pd.read_csv(article_similarity_scores_path)

    # Step 2: Normalize the similarity metrics (Cosine Similarity, WMD, Semantic Similarity)
    similarity_columns = ['Cosine Similarity (TF-IDF)', 'Word Mover\'s Distance (WMD)', 'Semantic Similarity (BERT)']
    scaler = MinMaxScaler()
    df[similarity_columns] = scaler.fit_transform(df[similarity_columns])

    # Step 3: Invert Word Mover's Distance because lower WMD means higher similarity
    df['Inverse_WMD'] = 1 - df['Word Mover\'s Distance (WMD)']

    # Step 4: Create a Combined Similarity metric using your custom weights
    df['Combined_Similarity'] = (
        0.9 * df['Semantic Similarity (BERT)'] +
        0.0 * df['Cosine Similarity (TF-IDF)'] +
        0.0 * df['Inverse_WMD']
    )

    # Step 5: Create a similarity matrix
    unique_articles = pd.concat([df['Article 1'], df['Article 2']]).unique()
    similarity_matrix = pd.DataFrame(0, index=unique_articles, columns=unique_articles, dtype=float)

    for _, row in df.iterrows():
        similarity_matrix.loc[row['Article 1'], row['Article 2']] = row['Combined_Similarity']
        similarity_matrix.loc[row['Article 2'], row['Article 1']] = row['Combined_Similarity']

    # Convert the similarity matrix to a distance matrix (1 - similarity)
    distance_matrix = 1 - similarity_matrix.values

    if method == "kmeans":
        # # Step 6: Apply KMeans Clustering to group articles into 10 groups
        kmeans = KMeans(n_clusters=num_cluster, random_state=42)
        labels = kmeans.fit_predict(distance_matrix)  # Use 1 - similarity as "distance"
    elif method == "agglomerative":
        # or Apply Agglomerative Clustering
        agg_clustering = AgglomerativeClustering(n_clusters=num_cluster, affinity='precomputed', linkage='average')
        labels = agg_clustering.fit_predict(distance_matrix)
    else:
        print(f"method has to be either kmeans or agglomerative")
        return

    df_clusters = pd.DataFrame({
        'Article': unique_articles,  # Assuming 'unique_articles' is the list of article names
        'Cluster': labels  # These are the cluster labels from KMeans or other clustering algorithm
    })

    # Step 2: Save the DataFrame to a CSV file
    df_clusters.to_csv(output_file, index=False)
    print(f"Clustering results saved to {output_file}")

    if plot_path:
        # Step 7: Dimensionality Reduction using t-SNE (without init="pca")
        # t-SNE to reduce the dimensionality to 2D for visualization
        # Explicitly set init="random" to avoid pca initialization issues
        tsne = TSNE(n_components=2, metric='precomputed', init="random", random_state=42)
        tsne_results = tsne.fit_transform(1 - similarity_matrix.values)  # Use 1 - similarity as "distance"

        # Step 8: Visualizing the clusters in 2D
        plt.figure(figsize=(10, 8))
        plt.scatter(tsne_results[:, 0], tsne_results[:, 1], c=labels, cmap='tab10', s=50)
        plt.title('Article Clusters (t-SNE Visualization)')
        plt.xlabel('t-SNE Dimension 1')
        plt.ylabel('t-SNE Dimension 2')
        plt.colorbar(label='Cluster')

        # Save the figure to a file instead of displaying
        plt.savefig(plot_path)


if __name__ == '__main__':
    topic = "putin"
    source = "google_news2"
    num_cluster = 10

    article_similarity_scores_path = Path.joinpath(output_dir,
                                                   f"article_similarities/{topic}/{source}.csv")
    output_file = Path.joinpath(output_dir, f'article_clusters/{topic}/{source}.csv')

    cluster_articles(article_similarity_scores_path= article_similarity_scores_path, method="kmeans", output_file=output_file, num_cluster=num_cluster)