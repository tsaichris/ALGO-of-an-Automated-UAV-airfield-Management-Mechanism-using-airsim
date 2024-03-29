# ALGO-of-an-Automated-UAV-airfield-Management-Mechanism-using-airsim

## 特性

- 使用 AirSim 模擬無人機飛行。
- 包含進離場、飛行路線規劃、避讓演算法。

## 安裝

### 前置要求

- Windows 10 或 Linux
- Python 3.8 或更高版本

### 步驟

1. git clone this repo：
git clone https://github.com/tsaichris/ALGO-of-an-Automated-UAV-airfield-Management-Mechanism-using-airsim.git
2. 遵循 [AirSim 安裝指南](https://github.com/Microsoft/AirSim) 設置 AirSim 環境。

## 使用方法
1. 從airsim官網下載地圖，例如Blocks
2. 設置setting.json 編輯無人機設定
3. 直接使用設定檔setting.json打開地圖，例如Blocks.exe，或用自行設定的.json檔案打開，如:
C:\Users\User\Desktop\airsim\Blocks\WindowsNoEditor\Blocks.exe -settings="C:\Users\User\Desktop\airsim\settings_test1.json"
4. 在multiDrone.py 內設定無人機數量(對應.json檔案內的數量)、設置飛行意圖(EX:drone1_intention = "Departure"
    drone2_intention = "Approach")、或到FlightPath.py內的FlightPath_OD設定各意圖的起始點與終點(Class:airsim.types.GpsData)
5. 運行multiDrone.py(請確保地圖.exe有同時運行)


## 引用 AirSim

本項目使用了 Microsoft 的 AirSim 模擬平台。感謝 AirSim 團隊提供的強大模擬工具和文檔。您可以在其 [GitHub 存儲庫](https://github.com/Microsoft/AirSim) 或從[airsim 1.8.1 documentation](https://microsoft.github.io/AirSim/api_docs/html/) 內查看可用之API


## 版權與許可證
本項目使用了第三方AirSim，該repo也遵循 MIT 許可證。更多關於 AirSim 的許可證信息，請參見其 [LICENSE](https://github.com/Microsoft/AirSim/blob/master/LICENSE) 文件。
