
import io
import numpy as np  # ESTA LINHA CORRIGE O ERRO 'np is not defined'
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image, ImageOps, ImageDraw

TOKEN = "7930739159:AAEqXuDVlLWlvKmk7bDhBu3TVwyucRC_J5I"

def limpar_fundo_e_pegar_cor(img):
    img = img.convert("RGBA")
    data = np.array(img)
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    mask = (r > 220) & (g > 220) & (b > 220)
    data[:,:,3][mask] = 0
    img_limpa = Image.fromarray(data)
    
    img_rgb = img.convert('RGB').resize((1, 1), resample=Image.Resampling.LANCZOS)
    cor_predominante = img_rgb.getpixel((0, 0))
    return img_limpa, cor_predominante

async def processar_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    legenda = update.message.caption or ""
    foto = update.message.photo

    if legenda.strip().upper() == "TEMA" and foto:
        try:
            await update.message.reply_text("Um momento, estou gerando seu tema...")

            arquivo_foto = await foto[-1].get_file()
            foto_bytes = await arquivo_foto.download_as_bytearray()
            img_original = Image.open(io.BytesIO(foto_bytes))

            img_logo, cor_borda = limpar_fundo_e_pegar_cor(img_original)

            LARGURA_A4 = 1240
            ALTURA_A4 = 1754
            ALTURA_RET = 295      
            ESPESSURA_BORDA = 15  
            FOLGA_INTERNA = 20    
            
            folha = Image.new('RGB', (LARGURA_A4, ALTURA_A4), (255, 255, 255))
            draw = ImageDraw.Draw(folha)            
          
            draw.rectangle([0, 0, LARGURA_A4, ALTURA_RET], outline=cor_borda, width=ESPESSURA_BORDA)
            
            largura_max = LARGURA_A4 - (ESPESSURA_BORDA * 2) - (FOLGA_INTERNA * 2)
            altura_max = ALTURA_RET - (ESPESSURA_BORDA * 2) - (FOLGA_INTERNA * 2)
            img_logo.thumbnail((largura_max, altura_max), Image.Resampling.LANCZOS)
            
            pos_x = (LARGURA_A4 - img_logo.width) // 2
            pos_y = (ALTURA_RET - img_logo.height) // 2
            
            folha.paste(img_logo, (pos_x, pos_y), img_logo)

            output = io.BytesIO()
            folha.save(output, format="JPEG", quality=95)
            output.seek(0)
            
            await update.message.reply_document(document=output, filename="tema criado.jpg")

        except Exception as e:
            await update.message.reply_text(f"Erro técnico: {str(e)}")
    else:
        await update.message.reply_text("Envie em anexo o logo com a legenda TEMA.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, processar_layout))
    application.run_polling()



