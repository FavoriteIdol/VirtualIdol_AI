from PIL import Image, ImageDraw, ImageFont

import os
import sys

buf = Image.open("./BASE_DIR/bg.png")
backgroundticket = Image.open("bg.png")
textticket = Image.open("txtbg.png")
draw=ImageDraw.Draw(buf)
draw.text((1600,150),"버튜바 \n20시",font=ImageFont.truetype("EF_jejudoldam(OTF).otf", 100), fill=(255,255,255))
buf.save("title.png")

input_text = "동해물과 백두산이 \n마르고닳도록\n하느님이보우하사\n우리나라만수ㅔ이"

text_ticket_img = ImageDraw.Draw(textticket)
text_ticket_img.text((50,50), 
                    input_text,
                    font=ImageFont.truetype("EF_jejudoldam(OTF).otf", 100),
                    fill=(255,255,255),
                    )
backgroundticket.paste(buf,(50,50))
backgroundticket.paste(textticket,(2100,50))
backgroundticket.save("merged_img.png", "PNG")