# 还是用熟悉的方式进行部署吧.......

from searchclient import create_app

app = create_app()
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
