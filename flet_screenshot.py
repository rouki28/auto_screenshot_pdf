import flet as ft
import pyautogui
import keyboard
import time
from PIL import Image
import os
import threading

def main(page: ft.Page):
    # ウィンドウの基本設定
    page.title = "Auto Screenshot Tool"
    page.window_width = 500
    page.window_height = 800
    page.padding = 20
    
    # モダンなテーマ設定 (Material 3)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.INDIGO, # テーマカラーをインディゴに
        use_material3=True
    )
    # 背景色を少し落ち着いたグレーにして、カードを浮き立たせる
    page.bgcolor = ft.colors.SURFACE_VARIANT 

    # --- フォルダ選択ダイアログの設定 ---
    def get_directory_result(e: ft.FilePickerResultEvent):
        if e.path:
            dir_input.value = e.path
            page.update()

    file_picker = ft.FilePicker(on_result=get_directory_result)
    page.overlay.append(file_picker)

    # --- UIコンポーネントの定義 (モダンデザイン化) ---
    
    # テキストフィールドの共通スタイル
    field_style = {
        "border_radius": 12,
        "filled": True,
        "border_color": ft.colors.TRANSPARENT,
        "content_padding": 15,
    }

    pages_input = ft.TextField(
        label="保存するページ数 (半角数字)", 
        value="10", 
        keyboard_type=ft.KeyboardType.NUMBER,
        prefix_icon=ft.icons.NUMBERS,
        **field_style
    )
    
    filename_input = ft.TextField(
        label="ファイル名", 
        value="screenshot",
        prefix_icon=ft.icons.INSERT_DRIVE_FILE,
        **field_style
    )
    
    direction_dropdown = ft.Dropdown(
        label="ページの開き設定",
        options=[
            ft.dropdown.Option("1", "右開き"),
            ft.dropdown.Option("2", "左開き"),
        ],
        value="1",
        prefix_icon=ft.icons.MENU_BOOK,
        **field_style
    )
    
    dir_input = ft.TextField(
        label="保存先フォルダ", 
        value=r"C:\Users\liana\OneDrive\デスクトップ\sc_py",
        expand=True,
        prefix_icon=ft.icons.FOLDER,
        **field_style
    )
    
    dir_button = ft.IconButton(
        icon=ft.icons.FOLDER_OPEN,
        icon_color=ft.colors.PRIMARY,
        icon_size=30,
        tooltip="フォルダを選択",
        on_click=lambda _: file_picker.get_directory_path()
    )
    dir_row = ft.Row([dir_input, dir_button])

    # 入力エリアを白いカード風にまとめる
    input_card = ft.Container(
        content=ft.Column(
            [pages_input, filename_input, direction_dropdown, dir_row],
            spacing=20
        ),
        bgcolor=ft.colors.SURFACE,
        padding=20,
        border_radius=15,
        shadow=ft.BoxShadow(
            blur_radius=10, 
            color=ft.colors.with_opacity(0.1, ft.colors.ON_SURFACE)
        )
    )
    
    # ログ表示エリア (ターミナル風)
    log_text = ft.Text(
        value="システム待機中...\n※実行中はqキーで緊急停止します。",
        color=ft.colors.GREEN_ACCENT_400,
        font_family="Consolas"
    )
    
    log_card = ft.Container(
        content=ft.Column([log_text], scroll=ft.ScrollMode.AUTO),
        bgcolor=ft.colors.ON_SURFACE, # ダークな背景色
        padding=15,
        border_radius=10,
        height=150,
        width=float("inf"),
        shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.BLACK12)
    )
    
    is_running = False

    def start_screenshot(e):
        nonlocal is_running
        if is_running:
            return
        
        try:
            n = int(pages_input.value)
            text = filename_input.value
            read = int(direction_dropdown.value)
            current_dir = dir_input.value
        except ValueError:
            log_text.value = "[Error] ページ数には有効な数値を入力してください。"
            page.update()
            return

        if not os.path.exists(current_dir):
            try:
                os.makedirs(current_dir)
            except Exception as ex:
                log_text.value = f"[Error] 保存先フォルダの作成に失敗しました。\n{ex}"
                page.update()
                return

        is_running = True
        start_button.disabled = True
        progress_ring.visible = True
        log_text.value = "[Info] 3秒後に処理を開始します。\n[Info] 対象の画面を前面に表示してください...\n[Warn] qキーで緊急停止できます。"
        page.update()

        threading.Thread(
            target=run_automation, 
            args=(n, text, read, current_dir), 
            daemon=True
        ).start()

    def run_automation(n, text, read, current_dir):
        nonlocal is_running
        
        time.sleep(3) 
        image_paths = []
        i = 0

        while i < (n // 2):
            path = os.path.join(current_dir, f"{text}{i+1}.png")
            pyautogui.screenshot().save(path)
            image_paths.append(path)

            if read == 1:
                pyautogui.click(x=2524, y=719)
            elif read == 2:
                pyautogui.click(x=49, y=719)
            else:
                log_text.value += "\n[Error] ページの開き設定が不正です。"
                page.update()
                break

            time.sleep(1.5)
            i += 1
            
            if keyboard.is_pressed('q'):
                log_text.value += "\n\n[Warn] qキーが押されたため緊急停止しました。"
                break

        log_text.value += "\n\n[Info] スクリーンショット撮影完了。"
        page.update()

        if image_paths:
            log_text.value += "\n[Info] PDFへの変換を開始します..."
            page.update()
            try:
                first_image = Image.open(image_paths[0]).convert('RGB')
                other_images = [Image.open(p).convert('RGB') for p in image_paths[1:]]
                
                pdf_path = os.path.join(current_dir, f"{text}.pdf")
                first_image.save(pdf_path, save_all=True, append_images=other_images)
                
                log_text.value += f"\n[Success] PDFへの結合が完了しました:\n{pdf_path}"
            except Exception as ex:
                log_text.value += f"\n[Error] PDF化中にエラーが発生しました:\n{ex}"
        else:
            log_text.value += "\n[Info] 画像が保存されなかったため、PDF化をスキップします。"

        is_running = False
        start_button.disabled = False
        progress_ring.visible = False
        page.update()

    # スタートボタンのモダンデザイン化
    progress_ring = ft.ProgressRing(width=20, height=20, stroke_width=2, visible=False)
    
    start_button = ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(ft.icons.PLAY_ARROW), ft.Text("キャプチャ開始", size=16, weight=ft.FontWeight.BOLD), progress_ring],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        style=ft.ButtonStyle(
            color=ft.colors.ON_PRIMARY,
            bgcolor=ft.colors.PRIMARY,
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.all(20),
        ),
        on_click=start_screenshot,
        width=300,
    )

    # ヘッダー部分
    header = ft.Row(
        [
            ft.Icon(ft.icons.CAMERA_ALT, size=30, color=ft.colors.PRIMARY),
            ft.Text("Auto Screenshot", size=28, weight=ft.FontWeight.W_900, color=ft.colors.PRIMARY)
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    # 画面にコンポーネントを追加
    page.add(
        ft.Column(
            [
                header,
                ft.Container(height=10),
                input_card,
                ft.Container(height=10),
                ft.Row([start_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=10),
                ft.Text("ステータスログ:", size=14, weight=ft.FontWeight.BOLD, color=ft.colors.ON_SURFACE_VARIANT),
                log_card
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        )
    )

if __name__ == "__main__":
    ft.app(target=main)