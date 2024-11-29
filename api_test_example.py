import os 
import sys
# import database_api.database_top_api as dbapi
current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = os.path.join(current_dir, "database_api")
sys.path.append(current_dir)
# mlibrary_dir = os.path.join(current_dir, "mlibrary")
# sys.path.append(mlibrary_dir)
# wait_list_dir = os.path.join(current_dir, "wait_list")
# sys.path.append(wait_list_dir)
# active_song_dir = os.path.join(current_dir, "active_song")
# sys.path.append(active_song_dir)
import database_api.database_top_api as dbapi
import database_api.wait_list.wait_list_0 as wl

# print("sys.path:")
# for path in sys.path:
#     print(path)


if  __name__ == "__main__":
    if dbapi.mlibrary_exist():
        print("数据库已存在")
    else:
        print("数据库不存在")
        dbapi.mlibrary_init()
        print("数据库初始化完成")
    # mlibrary_init()
    list = dbapi.mlibrary_search_song_by_title("明我")
    print(list)
    list = dbapi.mlibrary_search_song_by_artist("真夜")
    print(list)

    print("这是add 1,2,1,7")
    print(dbapi.wait_list_add(1))
    print(dbapi.wait_list_add(2))
    print(dbapi.wait_list_add(1))
    print(dbapi.wait_list_add(7))
    song = wl.Song(1, "明我", "真夜", "明我真夜","","","")

    print("这是move 3 2")
    print(dbapi.wait_list_move(3, 2))
    
    print(dbapi.wait_list_delete(2))

    print(dbapi.active_song_adjust_vol(60))

    print("程序结束")