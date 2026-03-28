from fastapi import FastAPI, File, UploadFile
import os
from PIL import Image
import win32print
import win32ui
from PIL import ImageWin

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/print")
async def print_image(file: UploadFile = File(...)):
    # Read file content
    file_content = await file.read()
    
    # Create a safe filename for images only
    import re
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', file.filename or "image")
    if not safe_filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
        safe_filename += ".jpg"
    
    input_path = f"{UPLOAD_FOLDER}/{safe_filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(file_content)

    # Print image directly using Windows API
    try:
        # Get Brother printer (not PDF)
        printers = [printer[2] for printer in win32print.EnumPrinters(2)]
        brother_printer = None
        for printer in printers:
            if "Brother" in printer and "PDF" not in printer:
                brother_printer = printer
                break
        
        if not brother_printer:
            return {"status": "image print failed", "error": "No Brother printer found", "file": safe_filename}
        
        printer_name = brother_printer
        
        # Open image
        image = Image.open(input_path)
        
        # Check if rotating the image would give better fit
        image_width, image_height = image.size
        printer_width = 2480  # Typical A4 width in pixels at 300 DPI
        printer_height = 3508  # Typical A4 height in pixels at 300 DPI
        
        # Calculate fit ratios for both orientations
        fit_normal = min(printer_width/image_width, printer_height/image_height)
        fit_rotated = min(printer_width/image_height, printer_height/image_width)
        
        # Rotate if it gives better fit (larger scale)
        if fit_rotated > fit_normal:
            image = image.rotate(90, expand=True)
        
        # Create printer device context
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        
        # Start print job
        hDC.StartDoc(safe_filename)
        hDC.StartPage()
        
        # Get printer capabilities
        printer_width = hDC.GetDeviceCaps(110)  # HORZRES - printer width in pixels
        printer_height = hDC.GetDeviceCaps(111)  # VERTRES - printer height in pixels
        
        # Get image size
        image_width, image_height = image.size
        
        # Calculate scaling to fill the entire page
        scale_x = printer_width / image_width
        scale_y = printer_height / image_height
        
        # Use the smaller scale to fit the image completely on the page
        scale = min(scale_x, scale_y)
        
        # Calculate new size
        new_width = int(image_width * scale)
        new_height = int(image_height * scale)
        
        # Center the image on the page
        x_offset = (printer_width - new_width) // 2
        y_offset = (printer_height - new_height) // 2
        
        # Print the image centered and scaled to fill more of the page
        dib = ImageWin.Dib(image)
        dib.draw(hDC.GetHandleOutput(), (x_offset, y_offset, x_offset + new_width, y_offset + new_height))
        
        # End print job
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        
        return {"status": "image printed successfully", "file": safe_filename, "printer": printer_name}
        
    except Exception as e:
        return {"status": "image print failed", "error": str(e), "file": safe_filename}