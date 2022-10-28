import numpy as np
import scipy.spatial.distance as dis
import matplotlib.pyplot as plt
from dl.learn.KMeans import k_means


# 首先将所有点看作一个簇，然后将该簇一分为二，之后选择最大限度降低簇类代价函数（误差平方和）的簇划分为两个簇
# 依次类推，知道簇的数目等于用户给定的数目为止
# 聚类的误差平方和月小，表示数据点越接近于他们的质心
def bi_k_means(data_set, cluster_count):
    point_count = np.shape(data_set)[0]  # 数据集中的待分类点个数

    # 初始化每个点的聚类和距离，列1：数据集归类的聚类中心（0,1,2,3），列2:数据集行向量到聚类中心的距离
    point_cluster_distances = np.zeros((point_count, 2), dtype=float)

    # 初始化第一个聚类中心: 每一列的均值（每个维度的中心）
    first_cluster = np.mean(data_set, axis=0)
    cluster_centers = [first_cluster]
    # 以第一个聚类中心，更新每个点的聚类点和距离，使用平方便于计算方差
    for index in range(point_count):
        point_cluster_distances[index, 1] = dis.euclidean(cluster_centers[0], data_set[index, :]) ** 2

    # 初始化最优化分割相关数据
    best_point_cluster_distance = point_cluster_distances.copy()
    best_cluster_to_split = 0
    best_new_clusters = cluster_centers

    # 依次生成 cluster_count 个聚类中心
    while len(cluster_centers) < cluster_count:
        min_sum_square = np.inf    # 初始化最小误差平方和，核心参数，这个值越小就说明聚类的效果越好

        # -->1. 计算每个聚类距离的最小误差平方和，以此确定最优分割点、新聚类中心、聚类距离
        for index in range(len(cluster_centers)):  # 遍历现有的所有聚类中心点
            # 提取当前聚类的所有点
            current_cluster_points = data_set[np.nonzero(point_cluster_distances[:, 0].T == index)[0], :]
            # 应用标准kMeans算法(k=2)，将当前聚类划分出两个子聚类中心，以及对应的聚类距离表
            split_clusters, point_split_cluster_distances = k_means(current_cluster_points, 2)
            # 计算划分出来的子聚类的距离平方和
            sum_split_cluster_distance_square = sum(point_split_cluster_distances[:, 1])
            # 计算其他聚类的距离平方和
            sum_other_cluster_distance_square = sum(point_cluster_distances[np.nonzero(point_cluster_distances[:, 0].T
                                                                                       != index)[0], 1])

            # 如果分割聚类点和其他聚类点的最小误差和更小，则使用该子分割
            if sum_split_cluster_distance_square + sum_other_cluster_distance_square < min_sum_square:
                min_sum_square = sum_split_cluster_distance_square + sum_other_cluster_distance_square  # 更新最小平方和
                best_cluster_to_split = index        # 确定聚类中心的最优分隔点
                best_new_clusters = split_clusters   # 用新的聚类中心更新最优聚类中心
                best_point_cluster_distance = point_split_cluster_distances.copy()  # 深拷贝聚类距离表为最优聚类距离表

        # -->2. 重新计算每个点到新聚类中心的距离
        # 聚类中心更新到最新
        best_point_cluster_distance[np.nonzero(best_point_cluster_distance[:, 0].T == 1)[0], 0] = len(cluster_centers)
        # 用最优分割点指定聚类中心索引
        best_point_cluster_distance[np.nonzero(best_point_cluster_distance[:, 0].T == 0)[0], 0] = best_cluster_to_split

        # -->3. 用最优分隔点来重构聚类中心
        cluster_centers[best_cluster_to_split] = best_new_clusters[0, :]
        cluster_centers.append(best_new_clusters[1, :])
        point_cluster_distances[np.nonzero(point_cluster_distances[:, 0].T == best_cluster_to_split)[0], :] \
            = best_point_cluster_distance

    return np.array(cluster_centers), point_cluster_distances


def train(cluster_count=4):
    data_set_path = r"../data/point-set-bi-kmeans.txt"
    data_set = np.loadtxt(data_set_path, dtype=float, delimiter='\t')[:, 1:]
    cluster_centers, point_cluster_distances = bi_k_means(data_set, cluster_count)
    colors = ['blue', 'green', 'red', 'gray', 'pink', 'cyan']

    cluster_point_distance_1 = point_cluster_distances[:, :1]
    for index in range(len(cluster_point_distance_1)):
        plt.scatter(data_set[index, 0], data_set[index, 1], c=colors[int(cluster_point_distance_1[index])], marker='o')

    plt.scatter(cluster_centers.T[0], cluster_centers.T[1], s=60, c='black', marker='D')
    plt.show()


if __name__ == '__main__':
    train(4)
