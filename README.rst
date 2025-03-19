========
專案名稱
========

這是寵物用品銷售資料產生器，產生顧客資料表、產品資料表、交易資料表等銷售相關模擬資料，
透過 `Pydantic`_ 進行資料驗證後存入資料庫 `PostgreSQL`_，作為銷售分析儀表板之範例資料。


資料說明
=========
* 顧客資料表
    * 使用 Python 套件 `Faker`_ 生成顧客資料。
    * 顧客資料包含姓名、性別、生日、聯絡資訊、居住地等資訊。
    * 設定排程每日06:00生成隨機筆數的顧客資料，模擬前一天新會員註冊之情境。
    * 顧客資料筆數透過 ``/src/company_operation_data_gen/constants.py`` 進行設定。

* 商品資料表
    * 爬取 `MOMO`_ 的寵物用品資訊。
    * 商品資料包含商品名稱、品牌、價格、資料更新時間等資訊。
    * 設定排程每週一04:00爬取最新商品資訊與價格。
    * 爬取的商品關鍵字與網站頁數透過 ``/src/company_operation_data_gen/constants.py`` 進行設定。

* 促銷檔期表
    * 促銷活動類型包含：滿額折扣、多件優惠、免運滿額贈。
    * 根據消費者心理與平假日的購買行為差異，指定一週七天適用的促銷活動類型。
        * 週二至週四為工作日，購買低峰，推出多件優惠引導消費者囤貨，單一商品購買數量較高，且偏好購買必需品或消耗品，例如：飼料、罐頭及尿布墊。
        * 週六與週日為假日，消費者出門遊玩逛街較少線上購物，推出滿額贈及免運活動，減少購買猶豫時間，單一商品購買數量較低，但交易筆數較高，消費者偏好購買非必需品或低價商品，例如：零食及潔牙骨。
        * 憂鬱週一購物紓解壓力，快樂週五迎接假日犒賞自己，購買高峰，推出滿額折扣，用高額折扣刺激購物，消費者偏好購買單價較高的商品，以達折扣門檻，例如：保健食品及凍乾零食。
    * 基於上述情境模擬每日交易筆數、每筆訂單商品購買數量、各類商品購買機率。透過 ``/src/company_operation_data_gen/constants.py`` 進行設定。

* 促銷活動表
    * 基於三種促銷活動類型（滿額折扣、多件優惠、免運滿額贈），設定活動內容、折扣門檻與贈品。
    * 促銷活動包含活動名稱、活動類型、折扣門檻值、折扣比率、贈品等資訊。

* 顧客行為資料表
    * 設定排程每日隨機選取資料庫中的顧客資料與產品資料，產生顧客行為資料。
    * 顧客行為包含瀏覽商品、加入購物車及購買商品。

* 交易資料表
    * 儲存顧客行為資料中的購買資料，並計算該筆交易適用的折扣活動與結帳金額。


開發
=======
安裝 Python
---------------
* 專案環境是 `Python 3.12.3`_ 。
* 以符號連結，環境變數路徑指向執行檔 ``/usr/local/bin/python3.12 -> /opt/python3.12/bin/python3.12`` 。

:: 

    % sudo apt build-dep python3
    % sudo apt install zlib1g-dev libbz2-dev libffi-dev libgdbm-compat-dev liblzma-dev libreadline-dev libsqlite3-dev libssl-dev tk-dev uuid-dev
    % wget https://www.python.org/ftp/python/3.12.3/Python-3.12.3.tar.xz
    % tar xJf Python-3.12.3.tar.xz
    % cd Python-3.12.3
    % ./configure --prefix=/opt/python3.12 --enable-optimizations
    % make
    % make test
    % sudo make install
    % sudo ln -sf /opt/python3.12/bin/python3.12 /usr/local/bin
    % sudo ln -sf /opt/python3.12/bin/pip3 /usr/local/bin/pip3
    % sudo ln -sf /opt/python3.12/bin/pip3.12 /usr/local/bin/pip3.12

虛擬環境
---------------
* 用 ``pipx`` 安裝套件管理工具 `Poetry`_ 。 
    * 隔離環境：將 ``Poetry`` 安裝至獨立的虛擬環境，避免衝突。
    * 簡化管理：將 ``Poetry`` 執行檔連結到全域環境中，可以直接在CMD中使用指令。

:: 

    % pip install --user pipx
    % pipx ensurepath
    % pipx install poetry
    % poetry config --list

* 套件管理初始化。

:: 

    % poetry init
    # 產生 pyproject.toml
    % poetry config virtualenvs.in-project true
    # 設置在專案資料夾創建對應的 .venv
    % poetry env use /usr/local/bin/python3.12
    # 指定用 Python3.12 創建虛擬環境
    % poetry shell
    # 啟動虛擬環境

* 安裝所需套件，會自動更新 ``pyproject.toml`` 內容。

::

    % pip install --upgrade pip setuptools wheel
    % poetry add numpy

*  如需安裝 ``pyproject.toml`` 內所有套件。

::

    % poetry install

*  如需安裝選擇性套件 [tool.poetry.extras]。
    * ``--extras`` 安裝指定的套件，刪除其他未指定的套件。
    * ``--with`` 安裝指定的套件，而不會刪除其他未指定的套件。

::

    % poetry install --extras "package1, package2"
    % poetry install --with "package1, package2"

*  如手動修改 ``pyproject.toml`` ，需更新 ``poetry.lock`` 。

::

    % poetry update
 
* 修改 ``pyproject.toml`` 內容，可以將開發完成的程式碼打包成可執行的指令。

::

    [tool.poetry.scripts]
    data-gen = "company_operation_data_gen.__main__:main"

測試
---------------
* 測試 ``argparse`` 參數是否正常設定。

::

    % cd /company-operation-data-gen
    % python3 -m company_operation_data_gen --version
    # 查看程式碼版本
    % python3 -m company_operation_data_gen init
    # 產生初始顧客資料

* 自動化測試並計算測試覆蓋率。

::

    % cd /company-operation-data-gen
    % PYTHONPATH=src pytest tests/
    % pip install pytest-cov
    % pytest --cov=company_operation_data_gen

資料庫
---------------
* 產生資料並存入 ``PostgreSQL`` 資料庫。

::

    % sudo apt install postgresql

* 預設使用 ``Peer authentication`` ，登入的 Linux 使用者要和資料庫帳號一致。
* 需修改 ``pg_hba.conf`` 設定，讓開發者可以利用密碼登入資料庫擁有者的帳號。

::

    % cd /etc/postgresql/14/main
    % sudo nano pg_hba.conf
    # 將 local all all peer 修改成 local all all scram-sha-256

* 使用 postgres 管理員帳號，登入資料庫，建立資料庫 source_db 和資料庫帳號，並設定密碼。

::

    % sudo -u postgres psql

    postgres=# CREATE USER source_db;
    postgres=# CREATE DATABASE source_db;
    postgres=# ALTER DATABASE source_db OWNER TO source_db;
    postgres=# \password source_db
    Enter new password for user "source_db":
    Enter it again:

    postgres=# \q

* 建立資料表，資料表定義參考 ``/support-files/source_db.schema.sql`` 檔案。

::

    % psql -U source_db source_db -f support-files/source_db.schema.sql

歷史資料
---------------
* 產生歷史資料並存入 ``PostgreSQL`` 資料庫，需修改程式碼內的指定日期。

::

    % python3 -m company_operation_data_gen.history_customer
    % python3 -m company_operation_data_gen.history_behavior
    

部署
===========
資料產生器專用帳號
--------------------
使用資料產生器專用帳號 ``company-operation-data-gen``，限縮該使用者權限。

::

    % sudo groupadd -r company-operation-data-gen
    % sudo useradd -r -g company-operation-data-gen -d /nonexistent -s /usr/sbin/nologin -c "資料產生器" -M company-operation-data-gen
    # -d /nonexistent：系統服務使用者沒有家目錄
    # -s /usr/sbin/nologin：無法登錄系統，僅能執行系統服務
    # -c：使用者用途
    # -M：不創建家目錄
    % sudo usermod -aG company-operation-data-gen company-operation-data-gen

虛擬環境
----------
將專案程式碼複製到 ``/srv`` ，建立虛擬環境。
::

    % cd /srv
    % git clone git@github.com:dspim/company-operation-data-gen.git

    % sudo chown $USER:$USER /srv/company-operation-data-gen
    # 開發測試階段，先設定資料夾擁有者為開發者，後續可修改成資料產生器專用帳號
    % poetry config virtualenvs.in-project true
    # 設置在專案資料夾創建對應的 .venv
    % poetry env use /usr/local/bin/python3.12
    # 指定用 Python3.12 創建虛擬環境
    % poetry shell
    # 啟動虛擬環境
    % poetry install
    # 安裝資料產生器至 /srv/company-operation-data-gen/.venv/bin/data-gen


設定檔
---------
* 資料產生器需要 ``.env`` 設定檔，參考範例 ``/support-files/.env.example`` 。
* 複製範例，將設定檔存在 ``/etc/data-pipeline/company-operation-data-gen.conf`` ，以符號連結至資料管線檔案 ``.env`` 。

::
    
    % cd /srv/company-operation-data-gen
    % sudo mkdir -p /etc/data-pipeline
    % sudo cp support-files/.env.example /etc/data-pipeline/company-operation-data-gen.conf
    % sudo chown root:company-operation-data-gen /etc/data-pipeline/company-operation-data-gen.conf
    % sudo chmod 640 /etc/data-pipeline/company-operation-data-gen.conf
    % ln -sf /etc/data-pipeline/company-operation-data-gen.conf /srv/company-operation-data-gen/.env

嘗試執行資料產生器，看是否有任何錯誤。
::

    % cd /srv/company-operation-data-gen
    % sudo -u company-operation-data-gen .venv/bin/data-gen init

記錄檔
--------
* 記錄檔存放在 ``/var/log`` 。
* 確保使用者 ``company-operation-data-gen`` 有寫入權限。

::

    % cd /var/log
    % sudo touch company-operation-data-gen.log
    % sudo chown company-operation-data-gen:root /var/log/company-operation-data-gen.log

Systemd服務設定
-----------------
* ``Systemd`` 是 ``Linux`` 的服務排程管理系統。 
* ``Systemd`` 排程需要兩個檔案： ``service 服務設定檔`` 定義工作內容， ``timer 排程設定檔`` 定義執行時間。
* 設定檔存放於 ``/etc/systemd/system/`` 。
* 下列設定步驟，以「每周一04:00更新產品資料」的排程為例。參考範例檔 ``/support-files/company-operation-data-gen-weekly.service`` 和 ``support-files/company-operation-data-gen-weekly.timer`` 。
    * 每周一04:00更新產品資料。
    * 每日06:00產生前一日的顧客資料、顧客行為資料與交易資料。
    
::

    % cd /srv/company-operation-data-gen
    % sudo cp -p support-files/company-operation-data-gen-weekly.service support-files/company-operation-data-gen-weekly.timer /etc/systemd/system/
    % sudo chown root:root /etc/systemd/system/company-operation-data-gen-weekly.service /etc/systemd/system/company-operation-data-gen-weekly.timer
    % sudo chmod 644 /etc/systemd/system/company-operation-data-gen-weekly.service
    % sudo chmod 644 /etc/systemd/system/company-operation-data-gen-weekly.timer
    # 不需要執行權限
    % sudo nano /etc/systemd/system/company-operation-data-gen-weekly.service
    % sudo nano /etc/systemd/system/company-operation-data-gen-weekly.timer
    # 可直接編輯檔案

* 驗證檔案是否有語法錯誤。

::

    % sudo systemd-analyze verify /etc/systemd/system/company-operation-data-gen-weekly.service

* 如修改服務設定檔，需重新讀取配置。

::

    % sudo systemctl daemon-reload
    # 修改設定檔後
    % sudo systemctl daemon-reexec
    # systemd更新或異常
    
    % sudo systemctl stop company-operation-data-gen-daily.timer
    % sudo systemctl stop company-operation-data-gen-weekly.timer
    % sudo systemctl disable company-operation-data-gen-daily.timer
    % sudo systemctl disable company-operation-data-gen-weekly.timer

    % sudo systemctl enable --now company-operation-data-gen-daily.timer
    % sudo systemctl enable --now company-operation-data-gen-weekly.timer
    % sudo systemctl start company-operation-data-gen-daily.timer
    % sudo systemctl start company-operation-data-gen-weekly.timer

* 查看服務狀態。

::

    % sudo systemctl status company-operation-data-gen-weekly.timer
    % sudo systemctl status company-operation-data-gen-weekly.service

* 檢查是否有任何錯誤。

::

    % sudo journalctl -u company-operation-data-gen-weekly.service -n 10
    # systemd管理日誌
    % sudo tail -n 100 /var/log/company-operation-data-gen.log
    # 手動設定的日誌

* 如需刪除log內容。

::

    % sudo truncate -s 0 /var/log/company-operation-data-gen.log

* 查看所有排程服務下次執行時間。

::

    % systemctl list-timers --all

授權條款
=========
版權所有 2025 Hailey Hsiao， 作者保有所有權利。

作者
=========
| Hailey Hsiao
| dwarfxiao@gmail.com

.. _Pydantic: https://docs.pydantic.dev/latest
.. _PostgreSQL: https://www.postgresql.org
.. _Faker: https://faker.readthedocs.io/en/master
.. _MOMO: https://www.momoshop.com.tw
.. _Python 3.12.3: https://www.python.org/downloads/release/python-3123/
.. _Poetry: https://python-poetry.org/docs/
