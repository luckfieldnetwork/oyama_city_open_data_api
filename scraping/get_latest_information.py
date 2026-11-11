from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sqlalchemy
import re
import requests
import os
from urllib.parse import urljoin

CSV_FILE_DIR = './csv/'
class OpenData:
        def __init__(self):
            self.top_url = 'https://www.city.oyama.tochigi.jp/opendata.php'
            self.driver = self.create_driver()

        def create_driver(self):
            options = webdriver.ChromeOptions()
            # options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=options)
            return driver

        def get_opendata_top(self):
            self.driver.get(self.top_url)

        def get_latest_informations(self):
            wait = WebDriverWait(self.driver, 10)
            try:
                target_h2 = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[text()='オープンデータ最新情報']")))
                print(f"セクションを発見: {target_h2.text}")
            except TimeoutException:
                print("「オープンデータ最新情報」セクションが見つかりませんでした。")
                return

            # StaleElementReferenceExceptionを避けるため、先にリンクの数を取得
            list_container = target_h2.find_element(By.XPATH, "./following-sibling::ul[1]")
            links = list_container.find_elements(By.TAG_NAME, 'a')
            num_links = len(links)

            if num_links == 0:
                print("最新情報にリンクが見つかりませんでした。")
                return

            # ループ内で要素を再取得しながらクリックする
            for i in range(num_links):
                # ページ遷移で要素が無効になるため、毎回トップページから要素を再取得する
                try:
                    # h2要素を再取得
                    h2_re = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[text()='オープンデータ最新情報']")))
                    # ul要素を再取得
                    list_container_re = h2_re.find_element(By.XPATH, "./following-sibling::ul[1]")
                    # i番目のリンク要素を取得してクリック
                    link_to_click = list_container_re.find_elements(By.TAG_NAME, 'a')[i]
                    
                    link_text = link_to_click.text or "No Text"
                    print(f"リンクをクリックします: {link_text}")
                    link_to_click.click()

                except (TimeoutException, IndexError) as e:
                    print(f"リンクの再取得またはクリックに失敗しました (index: {i}): {e}")
                    self.get_opendata_top() # 失敗した場合はトップページに戻って次のループへ
                    continue

                # 「最新情報」のリンクは、直接データセットの詳細ページ（最終ページ）に遷移すると想定。
                # したがって、中間ページの処理は行わず、直接最終ページのダウンロード処理を行う。
                try:
                    # ページ遷移を確実にするため、パンくずリストの最後がクリックしたリンクのテキストになるまで待機
                    wait.until(EC.presence_of_element_located((By.XPATH, f"//nav[@id='topicpath']/ol/li[last()][normalize-space()='{link_text}']")))

                    current_url = self.driver.current_url
                    print(f"詳細ページに移動しました: {current_url}")

                    # h3タグのテキストが「データ」である要素を特定（前後の空白を無視）
                    data_h3 = wait.until(EC.presence_of_element_located((By.XPATH, "//h3[normalize-space()='データ']")))
                    # そのh3タグの直後にあるul要素を取得
                    list_container = data_h3.find_element(By.XPATH, "./following-sibling::ul[1]")
                    # ul要素内のli要素をすべて取得
                    li_elements = list_container.find_elements(By.TAG_NAME, 'li')
                    for li in li_elements:
                        # 各li要素内の最初のaタグがダウンロードリンクであると想定
                        try:
                            csv_link = li.find_element(By.TAG_NAME, 'a')
                            href = csv_link.get_attribute('href')
                            link_text_for_filename = csv_link.text.strip() # リンクのテキストを取得
                            if href and 'opendata_download.php' in href:
                                absolute_url = urljoin(current_url, href)
                                print(f"CSVダウンロードリンクを発見: {absolute_url}")
                                self.download_csv(absolute_url, link_text_for_filename + ".csv")
                        except Exception:
                            # li内に期待するaタグがなかった場合、次のliへ
                            continue
                except TimeoutException:
                    print(f"詳細ページ ({self.driver.current_url}) で予期した要素（パンくずリストや「データ」セクション）が見つかりませんでした。")
                except Exception as e:
                    print(f"詳細ページ ({self.driver.current_url}) での処理中にエラーが発生しました: {e}")

                # 次のリンクを処理するためにトップページに戻る
                self.get_opendata_top()

        def download_csv(self, url, desired_filename=None): # desired_filename 引数を追加
             try:
                if not os.path.exists(CSV_FILE_DIR):
                    os.makedirs(CSV_FILE_DIR)

                response = requests.get(url)
                response.raise_for_status()

                filename = desired_filename # 渡された desired_filename を最優先で使用
                if not filename: # desired_filename がない場合のみ、Content-Dispositionヘッダーから取得を試みる
                    content_disposition = response.headers.get('content-disposition')
                    if content_disposition:
                        fname = re.findall('filename="?([^"]+)"?', content_disposition)
                        if fname:
                            filename = fname[0]
                
                # ヘッダーから取得できない場合、URLから取得
                if not filename:
                    filename = url.split('/')[-1]

                # ファイル名として不適切な文字を置換
                filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
                filepath = os.path.join(CSV_FILE_DIR, filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)
                print(f'CSVファイルをダウンロードしました: {filepath}')
             except requests.exceptions.RequestException as e:
                print(f'ダウンロードエラー: {e}')

        def check_update(self):
            #最終更新日を記録
            pass

        def quit(self):
            if self.driver:
                self.driver.quit()

def main():
    opendata = OpenData()
    try:
        opendata.get_opendata_top()
        opendata.get_latest_informations()
    finally:
        opendata.quit()

if __name__=="__main__":
    main()
