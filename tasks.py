import shutil

from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF



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
        slowmo=100,
    )
    open_the_intranet_website()
    close_annoying_modal()
    orders = get_orders()

    for order in orders:
        fill_the_form(order)
        pdf_file = store_receipt_as_pdf(order['Order number'])
        screen_file = screenshot_robot(order['Order number'])
        embed_screenshot_to_receipt(screen_file, pdf_file)

        page = browser.page()
        page.locator("#order-another").click()
        close_annoying_modal()
    archive_receipts()

        

def open_the_intranet_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def get_orders():
    """
    Downloads csv file from the given URL and 
    return orders from it
    """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", header=True
    )
    return orders


def close_annoying_modal():
    """Close modal window"""
    page = browser.page()
    page.click("button:text('OK')")


def fill_the_form(order):
    """
    Fill the form with data from order
    """
    page = browser.page()
    page.locator("#head").select_option(order['Head'])
    page.locator(f"#id-body-{order['Body']}").click()
    page.locator("xpath=//div[3]/input").fill(order['Legs'])
    page.fill("#address", order['Address'])

    while True:
        try:
            page.locator("#order").click(timeout=500)
        except:
            #error not occure
            break


def store_receipt_as_pdf(order_number):
    """
    Store the order receipt as a PDF file and return file location
    """
    page = browser.page()
    sales_results_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    file = f"output/receipts/order_{order_number}.pdf"
    pdf.html_to_pdf(sales_results_html, file)
    return file
    

def screenshot_robot(order_number):
    """
    Saves an image of ordered robot and return
    path to the file
    """
    page = browser.page()
    file = f"output/screens/order_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=file)
    return file


def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed screenshot to a PDF with receipt"""
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshot, source_path=pdf_file, output_path=pdf_file
    )


def archive_receipts():
    """Archive the reveipts and remove dir"""
    # Creating a zip archive of the PDFs directory
    archive_path = shutil.make_archive("output/orders", "zip", root_dir="output", base_dir="receipts")
    
    # Optionally, remove the original files directory after archiving
    shutil.rmtree("output/receipts")
    shutil.rmtree("output/screens")