#!/usr/bin/env python3
import rosbag
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import rospy
import sensor_msgs.point_cloud2 as pc2
import pandas as pd

# detastructure
# https://docs.ros.org/en/melodic/api/sensor_msgs/html/msg/PointCloud2.html

def main():
    ###### param ######
    # レコードファイルのパス
    bag_filepath = '2024-01-08-11-06-21.bag'
    
    # トピック名
    topic_name = '/velodyne_points'

    # 取り出す時刻（レコード開始時刻からの経過秒数）
    extract_time = 30.0

    # 取り出す空間範囲
    extract_range = 3.0
    ###################

    # velodyne_points トピックのみを抽出し，リスト化
    times = []
    msgs = []
    bag = rosbag.Bag(bag_filepath)
    for topic, msg, t in bag.read_messages():
        if topic == topic_name:
            time = float(f'{t.secs}.{t.nsecs}')
            times.append(time)
            msgs.append(msg)
    times = np.array(times)

    print('レコード時間: ', times[-1] - times[0], '[sec]')
    print('レコード開始時刻: ', times[0])
    print('レコード終了時刻: ', times[-1])

    # レコード開始時刻を基準とした時刻に変換
    times -= times[0]

    # 指定時刻付近のデータを抽出
    idx = np.where(times > extract_time)[0][0]
    print('指定時刻: ', times[idx])
    points = pointcloud2xyz(msgs[idx])

    #範囲内の点群のみを抽出
    points = points[np.linalg.norm(points, axis=1) < extract_range]

    # プロット
    fig = plt.figure()
    # 余白
    plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams['font.size'] = 14
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plt.rcParams['axes.linewidth'] = 1.0
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = '--'
    plt.rcParams['grid.linewidth'] = 0.3
    # plt.rcParams['legend.frameon'] = False
    # plt.rcParams['legend.loc'] = 'lower right'
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['legend.handlelength'] = 1.0
    plt.rcParams['legend.labelspacing'] = 0.5
    plt.rcParams['figure.figsize'] = [6.5, 4.8]
    plt.rcParams['figure.dpi'] = 200
    plt.rcParams['figure.subplot.left'] = 0.1
    plt.rcParams['figure.subplot.bottom'] = 0.12
    plt.rcParams['figure.subplot.right'] = 0.95
    plt.rcParams['figure.subplot.top'] = 0.95
    

    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], s=1)
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_zlabel('Z [m]')
    
    # 視点
    ax.view_init(elev=0)
    ax.view_init(azim=180+45)

    plt.show()

    # ファイル出力
    df = pd.DataFrame(points, columns=['x', 'y', 'z'])
    df.to_csv('points.csv', index=False)


# PointCloud2メッセージをnumpy配列に変換
def pointcloud2xyz(msg):
    pc_data = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
    pc_array = np.array(list(pc_data))
    return pc_array

    
if __name__ == '__main__':
    main()