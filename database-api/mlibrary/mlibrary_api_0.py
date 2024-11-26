from typing import List, Dict
import mlibrary_scratch_0 as mlibscratch 
import mlibrary_search_0 as mlibsearch
import mlibrary_getdata_0 as mlibget 
import os

def mlibrary_initialize(directory: str = "./data/music_file"):
    """
    重新扫描指定目录下的音频文件并更新数据库。
    
    :param directory: 需要扫描的文件夹路径，默认为 "./data/music_file"
    """

    # DB_DIR = "./cache/mlibrary"
    # DB_PATH = f"{DB_DIR}/songs.db"
    # 初始化数据库，清空旧数据
    if os.path.exists(mlibscratch.DB_PATH):
        os.remove(mlibscratch.DB_PATH)
    mlibscratch.initialize_database()
    # MU_PATH = "./data/music_file"
    # 测试能否更新成功
    # audio_table = mlibscratch.get_audio_info(directory)
    # print(audio_table)
    mlibscratch.get_audio_info(directory)


def mlibrary_search_title(name: str) -> List[int]:
    """
    按照歌名模糊搜索，返回匹配的歌曲 ID 列表。

    :param name: 歌名关键词
    :return: 歌曲 ID 列表
    """
    # 可以直接使用，不用进行空格处理
    name = name.replace(" ", "")
    return mlibsearch.search_songs_by_title(name)

def mlibrary_search_artist(name: str) -> List[int]:
    """
    按照艺术家名模糊搜索，返回匹配的歌曲 ID 列表。

    :param name: 艺术家关键词
    :return: 歌曲 ID 列表
    """
    # 可以直接使用，不用进行空格处理
    name = name.replace(" ", "")
    return mlibsearch.search_songs_by_artist(name)

def mlibrary_get_data(id_list: List[int]) -> List[Dict]:
    """
    根据 ID 列表获取对应的歌曲信息。

    :param id_list: 歌曲 ID 列表
    :return: 包含每首歌曲信息的字典列表
    """
    # all_songs = mlibget.fetch_all_songs()
    # return [song for song in all_songs if song["ID"] in id_list]
    return mlibget.fetch_songs_by_ids(id_list)


if __name__ == "__main__":
    mlibrary_initialize()
    # mlibrary_update()
    print(mlibrary_search_title("明我"))
    # mlibrary_search_title("明我")
    print(mlibrary_search_artist("s"))
    # mlibrary_search_artist("s")
    # mlibrary_get_data([1, 2, 3])
    print(mlibrary_get_data([1, 2, 3]))