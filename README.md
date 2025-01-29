# ntpu-linebot

一個可以查詢北大公開資訊的小工具\
加 Line 好友後即可使用(聊天)\
有發現 bug 或想加什麼功能都歡迎提出來討論

ID：[@148wrcch](https://lin.ee/QiMmPBv)

[![friend](/add_friend/S_add_friend_button.png)](https://lin.ee/QiMmPBv)

![qrcode](/add_friend/S_gainfriends_qr.png)

## 目前功能清單

1. 輸入**學號**查**姓名** (日夜)
2. 輸入**姓名**查**學號** (日)
3. 輸入**系名**查**系代碼** (日)
4. 輸入**系代碼**查**系名** (日)
5. 輸入**系級**查**學生名單** (日)
6. 輸入**課程名稱**查**課程清單** (日夜)
7. 輸入**教師姓名**查**授課課程清單** (日夜)
8. 輸入**單位/成員名稱**查**聯繫方式** (日夜)

## 資料來源

1. [國立臺北大學數位學苑 2.0](https://lms.ntpu.edu.tw)
2. [國立臺北大學校園聯絡簿](https://sea.cc.ntpu.edu.tw/pls/ld/campus_dir_m.main)
3. [國立臺北大學課程查詢系統](https://sea.cc.ntpu.edu.tw/pls/dev_stud/course_query_all.CHI_MAIN)

## 開發

本專案使用 [Poetry](https://python-poetry.org/) 作為套件管理及建立虛擬環境的工具\
詳細安裝及使用方式請參考官方文件，以下為常用的指令

### 安裝套件

```bash
poetry install
```

### 進入虛擬環境

```bash
poetry shell
```

### 測試執行

```bash
sanic app:app --debug
```

### 生產環境執行（docker）

> 需要先複製一份 docker/.env.example 到 docker/.env 並設定相關參數

```bash
cd docker
docker compose up -d
```

> 預設 port 為 10000

## 生產環境更新（latest）

```bash
docker compose down
docker compose pull
# docker image prune -f # 有需要可以清除舊的 image
docker compose up -d
```

> 也可以直接執行 `update.sh` 來更新
