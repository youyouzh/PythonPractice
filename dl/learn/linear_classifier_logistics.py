# 线性分类器，使用 hardlim 硬限幅函数

import numpy as np
import matplotlib.pyplot as plt


def draw_scatter_by_label(data_set: np.ndarray):
    point_count = np.shape(data_set)[0]
    colors = ['blue', 'green', 'red', 'gray', 'pink', 'cyan']
    markers = ['o', 's', '8', 'D', 'p']
    for index in range(point_count):
        current_point = data_set[index][:2]
        label = data_set[index][2]
        plt.scatter(current_point[0], current_point[1], c=colors[int(label)], marker=markers[int(label)])


# logistics 梯度下降线性分类器
def linear_classifier_logistics(data_set: np.ndarray):
    # 构建 b+x 系数矩阵：b这里默认为1，第一列为 b 偏移，后面为输入的数据集
    coefficients = np.zeros(np.shape(data_set))
    coefficients[:, 0] = 1  # 第一列 b 默认为 1
    coefficients[:, 1:] = data_set[:, :-1]  # 第一列为 b ，后面为数据集

    step_length = 0.001   # 迭代步长
    step_times = 500      # 迭代次数
    weight = np.ones((np.shape(data_set)[1], 1))  # 初始化权重向量
    weights = []

    # 梯度下降迭代
    for step in range(step_times):
        gradient = coefficients.dot(weight)        # 计算梯度
        output = 1.0 / (1.0 + np.exp(-gradient))    # Logistics 函数
        errors = data_set[:, -1].reshape(-1, 1) - output              # 计算误差，注意shape(errors)=(n,1)，而不是(n,)
        weight = weight + step_length * coefficients.T.dot(errors)  # 修正误差，进行迭代
        weights.append(weight)
    print("weight: ", weight)
    return weights


# 随机梯度下降线性分类器
# 1.对数据集的每个行向量进行m次随机抽取
# 2.对抽取之后的行向量应用动态步长
# 3.进行梯度计算
# 4.求得行向量的权值，合并为矩阵的权值
def linear_classifier_logistics_random(data_set: np.ndarray):
    # 构建 b+x 系数矩阵：b这里默认为1，第一列为 b 偏移，后面为输入的数据集
    coefficients = np.zeros(np.shape(data_set))
    coefficients[:, 0] = 1  # 第一列 b 默认为 1
    coefficients[:, 1:] = data_set[:, :-1]  # 第一列为 b ，后面为数据集

    base_alpha = 0.0001  # 迭代步长
    step_times = 500  # 迭代次数
    data_count = np.shape(data_set)[0]  # 数据数量
    weight = np.ones(np.shape(data_set)[1])  # 初始化权重向量
    weights = []
    for j in range(step_times):
        data_indexes = [x for x in range(data_count)]  # 以导入数据的行数m为个数产生索引向量
        for i in range(data_count):
            alpha = 2 / (1.0 + j + i) + base_alpha  # 动态修改alpha步长从4->0.016
            random_index = int(np.random.uniform(0, len(data_indexes)))  # 生成0~m之间随机索引
            vector_sum = np.sum(coefficients[random_index] * weight.T)
            gradient = 1.0 / (1.0 + np.exp(-vector_sum))    # Logistics 函数
            errors = data_set[random_index, -1] - gradient  # 计算点积和的梯度
            weight = weight + alpha * errors * coefficients[random_index]
            del(data_indexes[random_index])  # 从数据集中删除选取的随机索引
        weights.append(weight)
    print("weight: ", weight)
    return weights


# 对超平面进行评估
def hyperplane_evaluation(weights: list):
    x = np.linspace(-7, 7, 100)
    for index in range(len(weights)):
        if index % 10 == 0 and index <= 100:
            weight = weights[index]
            y = -(float(weight[0]) + x * (float(weight[1]))) / float(weight[2])
            plt.plot(x, y)
            plt.annotate('hyperplane: %s' % index, xy=(x[99], y[99]))  # 分类超平面标注
    plt.show()


# 截距的变化评估
def ordinate_at_origin_evaluation(weights: list):
    plt.figure()
    axes_min = plt.subplot(211)
    axes_all = plt.subplot(212)
    steps = len(weights)
    weights = np.array(weights)
    x = np.linspace(0, steps, steps)
    axes_min.plot(x[:10], -weights[:10, 0] / weights[:10, 2], color='blue', linewidth=1, linestyle="-")
    axes_all.plot(x[:], -weights[:, 0] / weights[:, 2], color='blue', linewidth=1, linestyle="-")
    plt.show()


# 斜率的变化评估
def slope_evaluation(weights: list):
    plt.figure()
    axes_min = plt.subplot(211)
    axes_all = plt.subplot(212)
    steps = len(weights)
    weights = np.array(weights)
    x = np.linspace(0, steps, steps)
    axes_min.plot(x[:10], -weights[:10, 1] / weights[:10, 2], color='blue', linewidth=1, linestyle="-")
    axes_all.plot(x[:], -weights[:, 1] / weights[:, 2], color='blue', linewidth=1, linestyle="-")
    plt.show()


# 权重向量评估
def weight_variant_evaluation(weights: list):
    plt.figure()
    axes_0 = plt.subplot(311)
    axes_1 = plt.subplot(312)
    axes_2 = plt.subplot(313)
    steps = len(weights)
    weights = np.array(weights)
    x = np.linspace(0, steps, steps)
    # 输出3个权重分类的变化
    axes_0.plot(x[0:], weights[:, 0], color='blue', linewidth=1, linestyle="-")
    axes_0.set_ylabel('weight[0]')
    axes_1.plot(x[0:], weights[:, 1], color='blue', linewidth=1, linestyle="-")
    axes_1.set_ylabel('weight[1]')
    axes_2.plot(x[0:], weights[:, 2], color='blue', linewidth=1, linestyle="-")
    axes_2.set_ylabel('weight[2]')
    plt.show()


# 对测试集进行分类
def classifier(test_data: np.ndarray, weights: np.ndarray):
    probability = 1.0 / (1.0 + np.exp(-(np.sum(test_data.dot(weights)))))
    return 1.0 if probability > 0.5 else 0.0


def train():
    data_set_path = r"../data/point-linear-classifier.txt"
    data_set = np.loadtxt(data_set_path)
    weight = linear_classifier_logistics(data_set)

    # 绘制点和分割超平面
    draw_scatter_by_label(data_set)
    x = np.linspace(-7, 7, 100)
    y = -(float(weight[0]) + x * (float(weight[1]))) / float(weight[2])
    plt.plot(x, y)
    plt.show()


def evaluation():
    data_set_path = r"../data/point-linear-classifier.txt"
    data_set = np.loadtxt(data_set_path)
    weights = linear_classifier_logistics_random(data_set)

    # ordinate_at_origin_evaluation(weights)
    # slope_evaluation(weights)
    weight_variant_evaluation(weights)
    # draw_scatter_by_label(data_set)
    # hyperplane_evaluation(weights)


if __name__ == '__main__':
    # train()
    evaluation()
