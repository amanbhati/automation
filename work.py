import subprocess
import psutil
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException, TimeoutException

import mss
import cv2
import numpy as np
import threading

# Video recording parameters
VIDEO_FILENAME = 'output.mp4'
RECORD_DURATION = 60  # Duration to record in seconds

def start_video_recording(filename=VIDEO_FILENAME, duration=RECORD_DURATION):
    global recording_started
    recording_started = time.time()

    # Define the screen resolution
    screen_size = (1920, 1080)  # Adjust this to your screen resolution
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Define the codec
    global video_writer
    video_writer = cv2.VideoWriter(filename, fourcc, 25.0, screen_size)

    def record_screen():
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Use the primary monitor
            while True:
                # Capture the screen
                img = sct.grab(monitor)
                frame = np.array(img)

                # Convert to BGR (OpenCV uses BGR format)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                # Resize the frame to match the screen size
                resized_frame = cv2.resize(frame, screen_size)

                # Write the frame to the video file
                video_writer.write(resized_frame)

                # Stop recording after a set duration
                if time.time() - recording_started > duration:
                    break

        video_writer.release()

    # Start recording in a separate thread
    recording_thread = threading.Thread(target=record_screen)
    recording_thread.start()

def stop_video_recording():
    # Release video writer
    global video_writer
    if video_writer is not None:
        video_writer.release()

def run_test():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get("https://demo.dealsdray.com/")
    time.sleep(2)
    
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username.send_keys("prexo.mis@dealsdray.com")
    
    password = driver.find_element(By.NAME, "password")
    password.send_keys("prexo.mis@dealsdray.com")
    
    login_button = driver.find_element(By.CLASS_NAME, "MuiButton-root")
    login_button.click()
    time.sleep(2)
    
    file_path = os.path.abspath(r"C:\Users\Amanb\OneDrive\Maths Assignments\project\demo-data.xlsx")
    print(f"File Path: {file_path}")
    
    driver.get("https://demo.dealsdray.com/mis/orders/bulk-import")
    time.sleep(2)

    try:
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )
        if file_input.is_enabled() and file_input.is_displayed():
            print("File input field located and interactable.")
            file_input.send_keys(file_path)
    except Exception as e:
        print(f"Error locating file input field: {e}")

    try:
        upload_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "css-6aomwy"))
        )
        driver.execute_script("arguments[0].click();", upload_button)
        time.sleep(4)
    except Exception as e:
        print(f"Error clicking upload button: {e}")

    try:
        validate_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "css-6aomwy"))
        )
        driver.execute_script("arguments[0].click();", validate_button)
        try:
            WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print("Alert found: ", alert.text)
            alert.dismiss()  # Use alert.accept() if you need to accept the alert
        except (NoAlertPresentException, TimeoutException) as e:
            print(f"No alert present or alert dismissed successfully: {e}")
        time.sleep(4)
    except Exception as e:
        print(f"Error clicking validate button: {e}")

    time.sleep(2)
    screenshot_path = f"screenshot-{int(time.time())}.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved to: {screenshot_path}")
    
    driver.quit()

if __name__ == "__main__":
    start_video_recording()
    run_test()
    stop_video_recording()
