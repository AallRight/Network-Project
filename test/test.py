from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # 允许所有来源的跨域请求


# 内存中的模拟数据库
tasks = [
    {"id": 1, "title": "Learn Flask", "completed": False},
    {"id": 2, "title": "Build a REST API", "completed": True},
]

# 首页路由


@app.route("/", methods=["GET"])
def home():
    return "Welcome to the Flask Task API!"

# 获取所有任务


@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks)

# 获取单个任务


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task:
        return jsonify(task)
    return jsonify({"error": "Task not found"}), 404

# 创建新任务


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json
    if "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    new_task = {
        "id": len(tasks) + 1,
        "title": data["title"],
        "completed": data.get("completed", False),
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

# 更新任务


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    task["title"] = data.get("title", task["title"])
    task["completed"] = data.get("completed", task["completed"])
    return jsonify(task)

# 删除任务


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": "Task deleted"})


# 启动服务器
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
