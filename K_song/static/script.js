// 加载演唱队列
function loadSongQueue() {
    fetch('/song_queue')
        .then(response => response.json())
        .then(data => {
            const songQueueList = document.getElementById('songQueue');
            songQueueList.innerHTML = ''; // 清空队列显示

            data.forEach((song) => {
                const listItem = document.createElement('li');
                listItem.textContent = `Song Name: ${song.title}`;

                // 上移按钮
                const moveUpButton = document.createElement('button');
                moveUpButton.textContent = 'MOVE UP';
                moveUpButton.onclick = () => moveSong('MOVE_UP', song.queue_id);

                // 下移按钮
                const moveDownButton = document.createElement('button');
                moveDownButton.textContent = 'MOVE DOWN';
                moveDownButton.onclick = () => moveSong('MOVE_DOWN', song.queue_id);

                // 移动到第一位按钮
                const moveFirstButton = document.createElement('button');
                moveFirstButton.textContent = 'MOVE FIRST';
                moveFirstButton.onclick = () => moveSong('MOVE_FIRST', song.queue_id);

                // 删除按钮
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'DELETE';
                deleteButton.onclick = () => deleteSong(song.queue_id);

                // 将按钮加入到列表项中
                listItem.appendChild(moveUpButton);
                listItem.appendChild(moveDownButton);
                listItem.appendChild(moveFirstButton);
                listItem.appendChild(deleteButton);

                songQueueList.appendChild(listItem);
            });
        });
}

// 移动歌曲位置（上移、下移）
function moveSong(action, songId) {
    fetch('/song_queue', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, queue_id: songId })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // 提示操作结果
            loadSongQueue(); // 重新加载队列
        });
}

// 删除歌曲
function deleteSong(songId) {
    fetch('/song_queue', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ queue_id: songId })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // 提示操作结果
            loadSongQueue(); // 重新加载队列
        });
}

// 加载所有歌曲数据
function loadAllSongs() {
    fetch('/song_data')
        .then(response => response.json())
        .then(data => {
            const allSongsList = document.getElementById('allSongs');
            allSongsList.innerHTML = ''; // 清空歌曲列表

            data.forEach(song => {
                const listItem = document.createElement('li');
                listItem.textContent = `Song Name: ${song.Title}`;

                // 添加到队列的按钮
                const addButton = document.createElement('button');
                addButton.textContent = 'Add';
                addButton.onclick = () => addToQueue(song);

                listItem.appendChild(addButton);
                allSongsList.appendChild(listItem);
            });
        });
}

// 添加歌曲到队列
function addToQueue(song) {
    fetch('/song_queue', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: song.Title, data_id: song.data_id })
    })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // 提示操作结果
            loadSongQueue(); // 重新加载队列
        });
}

// 页面加载时初始化
window.onload = function () {
    loadSongQueue();
    loadAllSongs();
};
