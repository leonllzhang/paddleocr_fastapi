from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse

from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import io
import numpy as np

app = FastAPI()
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

@app.post("/ocr")
async def read_ocr(file: UploadFile = File(...)):
    # 确保上传的文件类型是图像
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid image type")

    try:
        # 读取图片内容并处理
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        ocr_result = ocr.ocr(np.array(image), cls=True)

        # 提取文本和坐标
        result_text = []
        for line in ocr_result:
            line_text = ' '.join([text[1][0] for text in line])
            result_text.append({"text": line_text, "location": [text[0] for text in line]})
        
        return JSONResponse(content={"result": result_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ocr_compare")
async def read_ocr_with_compare(file: UploadFile = File(...)):
    # 确保上传的文件类型是图像
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid image type")

    try:
        # 读取图片内容并处理
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        ocr_result = ocr.ocr(np.array(image), cls=True)

        # 提取文本和坐标,画比对图
        for idx in range(len(ocr_result)):
            res = ocr_result[idx]
            for line in res:
                print(line)
        # 显示结果
        result = ocr_result[0]
        image_rgb = image.convert('RGB')
        boxes = [line[0] for line in result]
        txts = [line[1][0] for line in result]
        scores = [line[1][1] for line in result]
        im_show = draw_ocr(image_rgb, boxes, txts, scores, font_path='./ppocr_img/fonts/simfang.ttf')
        im_show = Image.fromarray(im_show)
        # im_show.save('result.jpg')

        # 将处理后的图像保存到临时文件
        output_buffer = io.BytesIO()
        im_show.save(output_buffer, format='JPEG')
        output_buffer.seek(0)

        # return FileResponse(output_buffer, media_type="image/jpeg")
        return StreamingResponse(io.BytesIO(output_buffer.getvalue()), media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/ocr_valid/")
async def read_ocr_valid(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid image type")

    try:
        # 读取图片内容并处理
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        image_np = np.array(image)
        ocr_result = ocr.ocr(image_np, cls=True)

        # 使用 PaddleOCR 的 draw_ocr 方法绘制文本检测结果
        image_with_boxes = draw_ocr(image_np, ocr_result, font_path="path_to_font.ttf")
        image_with_boxes = Image.fromarray(image_with_boxes)

        # 将处理后的图像保存到临时文件
        output_buffer = io.BytesIO()
        image_with_boxes.save(output_buffer, format='JPEG')
        output_buffer.seek(0)

        return FileResponse(output_buffer, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))