import numpy as np
import scipy.spatial.distance as dis
import matplotlib.pyplot as plt


__all__ = ['k_means']


# KMeans主函数
def k_means(data_set, cluster_count):
    point_count = np.shape(data_set)[0]  # 数据集中的待分类点个数

    # 列1：数据集归类的聚类中心（0,1,2,3），列2:数据集行向量到聚类中心的距离
    point_cluster_distances = np.zeros((point_count, 2), dtype=float)
    cluster_centers = data_set[:cluster_count, :]  # 取前4个点作为初始聚类中心

    iteration_flag = True  # 迭代结束标识
    iteration_count = 0  # 迭代次数

    while iteration_flag:
        iteration_flag = False
        iteration_count += 1

        # 遍历数据集中的所有点，计算每个点与聚类中心的最小欧式距离
        for index in range(point_count):
            # 遍历当前点到所有聚类中心的距离，获取最短距离的聚类中心
            current_point_to_cluster_distances = [dis.euclidean(data_set[index, :],
                                                                cluster_centers[j, :]) for j in range(cluster_count)]
            min_distance = min(current_point_to_cluster_distances)
            min_distance_cluster_index = current_point_to_cluster_distances.index(min_distance)

            # 找到了一个新聚类中心，重置标志位为True，继续迭代，如果没有找到新的聚类中心，说明迭代已经收敛，不再迭代
            if point_cluster_distances[index, 0] != min_distance_cluster_index:
                iteration_flag = True

            # 更新当前点找到的聚类中心以及距离
            point_cluster_distances[index, :] = min_distance_cluster_index, min_distance ** 2

        # 重新计算已经得到的各个聚类的质心
        for index in range(cluster_count):
            # 当前聚类的所有距离下标
            current_cluster_distance_indexes = np.nonzero(point_cluster_distances[:, 0].T == index)[0]
            # 当前聚类的所有点
            current_cluster_points = data_set[current_cluster_distance_indexes]
            cluster_centers[index, :] = np.mean(current_cluster_points, axis=0)

    print('cluster_centers: \n', cluster_centers)
    return cluster_centers, point_cluster_distances


def train(cluster_count=4):
    data_set_path = r"../data/point-set-kmeans.txt"
    # data_set_path = r"../data/point-set-bi-kmeans.txt"  # 错误的聚类
    data_set = np.loadtxt(data_set_path, dtype=float, delimiter='\t')
    cluster_centers, point_cluster_distances = k_means(data_set, cluster_count)
    cluster_point_distance_1 = point_cluster_distances[:, :1]
    colors = ['blue', 'green', 'red', 'gray', 'pink', 'cyan']

    for index in range(len(cluster_point_distance_1)):
        plt.scatter(data_set[index, 0], data_set[index, 1], c=colors[int(cluster_point_distance_1[index])], marker='o')

    plt.scatter(cluster_centers.T[0], cluster_centers.T[1], s=60, c='black', marker='D')
    plt.show()


if __name__ == '__main__':
    train()  # 5个点时效果很差
