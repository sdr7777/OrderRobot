from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Browser.Selenium import selenium_webdriver
import os
from zipfile import ZipFile


@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo = 100,
    )
    open_robot_order_website()
    download_orders()
    place_order()
    archive_receipts()


def download_orders():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/")

def get_orders():
    orders = Tables().read_table_from_csv(path="orders.csv")
    return orders

def place_order():
    orders = get_orders()
    for row in orders:
        browser.goto("https://robotsparebinindustries.com/?robot-order#/robot-order")
        close_annoying_modal()
        fill_the_form(row)

def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", index=int(order["Head"]))
    page.locator(".radio:nth-child(" + order["Body"] + ") > label").check()
    page.locator("xpath=//label[contains(.,'3. Legs:')]/../input").fill(order["Legs"])
    page.fill("#address", order["Address"])
    page.click("button:text('Order')")
    resubmit_order_on_error()
    pdf_file = store_receipt_as_pdf(order["Order number"])
    screenshot = screenshot_robot(order["Order number"])
    embed_screenshot_to_receipt(screenshot, pdf_file)
    page.click("text=Order another robot")

def close_annoying_modal():
    page = browser.page()
    page.click("text=OK")

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = "output/Receipts/" + order_number + ".pdf"
    pdf.html_to_pdf(receipt_html, pdf_file)
    return pdf_file

def screenshot_robot(order_number):
    page = browser.page()
    preview_html = page.locator("#robot-preview-image").inner_html()
    pdf = PDF()
    screenshot = "output/Preview/" + order_number + ".jpg"
    page.locator("#robot-preview-image").screenshot(path=screenshot)
    #pdf.html_to_pdf(preview_html, screenshot)
    return screenshot

def embed_screenshot_to_receipt(screenshot, pdf_file):
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)

def resubmit_order_on_error_old():
    page = browser.page()
    counter = 1
    while counter > 0:
        print(str(counter))
        try:
            alert_msg = str(page.inner_html(".alert-danger"))
            if "error" in alert_msg.lower():
                page.click("button:text('Order')")
            else:
                counter = 0
        except:
            print("No error")
            counter = 0

def resubmit_order_on_error():
    page = browser.page()
    counter = 1
    while counter > 0:
        print(str(counter))
        try:
            alert_msg_exists = page.is_visible(".alert-danger")
            print(alert_msg_exists)
            if alert_msg_exists:
                page.click("button:text('Order')")
            else:
                counter = 0
        except:
            print("No error")
            counter = 0

def archive_receipts():
    # Create object of ZipFile
    with ZipFile('output/Zipped file.zip', 'w') as zip_object:
    # Traverse all files in directory
        for folder_name, sub_folders, file_names in os.walk("output/Receipts/"):
            for filename in file_names:
                # Create filepath of files in directory
                file_path = os.path.join(folder_name, filename)
                # Add files to zip file
                zip_object.write(file_path, os.path.basename(file_path))

    if os.path.exists('output/Zipped file.zip'):
        print("ZIP file created")
    else:
        print("ZIP file not created")