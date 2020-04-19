from spider.pixiv.arrange.theme_color import *
from u_base import u_unittest


def test_train_main_color():
    illust_id = 35231457
    illust_path = get_illust_file_path(illust_id)
    clusters, label_count = rgb_kmeans(illust_path, True)
    print(clusters, label_count)
