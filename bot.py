
import io
import numpy as np  # ESTA LINHA CORRIGE O ERRO 'np is not defined'
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image, ImageOps, ImageDraw

TOKEN = "8250598286:AAEFQVWC205YdEALmAzEITO6kKxwZQDlfx8"

def limpar_fundo_e_pegar_cor(img):
    # Converte para RGBA para manipular transparência
    img = img.convert("RGBA")
    data = np.array(img)
    
    # Identifica pixels claros (branco/cinza) e os torna transparentes
    r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    mask = (r > 220) & (g > 220) & (b > 220)
    data[:,:,3][mask] = 0
    
    img_limpa = Image.fromarray(data)
    
    # Pega a cor predominante para a borda baseada no centro do logo
    img_rgb = img.convert('RGB').resize((1, 1), resample=Image.Resampling.LANCZOS)
    cor_predominante = img_rgb.getpixel((0, 0))
    
    return img_limpa, cor_predominante

async def processar_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    legenda = update.message.caption or ""
    foto = update.message.photo

    if legenda.strip().upper() == "TEMA" and foto:
        try:
            await update.message.reply_text("Processando layout técnico...")

            # 1. Baixar imagem
            arquivo_foto = await foto[-1].get_file()
            foto_bytes = await arquivo_foto.download_as_bytearray()
            img_original = Image.open(io.BytesIO(foto_bytes))

            # 2. Limpar fundo e obter cor
            img_logo, cor_borda = limpar_fundo_e_pegar_cor(img_original)

            # 3. Configurações A4 (150 DPI)
            LARGURA_A4 = 1240
            ALTURA_A4 = 1754
            ALTURA_RET = 295  # 5cm
            ESPESSURA_BORDA = 30 # ~5mm
            
            # 4. Criar Folha e Borda
            folha = Image.new('RGB', (LARGURA_A4, ALTURA_A4), (255, 255, 255))
            draw = ImageDraw.Draw(folha)
            
            # Desenha o retângulo branco com contorno colorido
            draw.rectangle([0, 0, LARGURA_A4, ALTURA_RET], outline=cor_borda, width=ESPESSURA_BORDA)

            # 5. Redimensionar Logo e Centralizar
            # Espaço útil dentro da borda de 5mm com folga extra
            largura_max = LARGURA_A4 - (ESPESSURA_BORDA * 2) - 60
            altura_max = ALTURA_RET - (ESPESSURA_BORDA * 2) - 60
            img_logo.thumbnail((largura_max, altura_max), Image.Resampling.LANCZOS)

            pos_x = (LARGURA_A4 - img_logo.width) // 2
            pos_y = (ALTURA_RET - img_logo.height) // 2
            
            # Cola o logo centralizado usando alpha channel
            folha.paste(img_logo, (pos_x, pos_y), img_logo)

            # 6. Enviar
            output = io.BytesIO()
            folha.save(output, format="JPEG", quality=95)
            output.seek(0)
            
            await update.message.reply_document(document=output, filename="layout_final.jpg")

        except Exception as e:
            # Captura erros para não travar o bot
            await update.message.reply_text(f"Erro técnico: {str(e)}")
    else:
        # Resposta caso enviem sem a legenda TEMA
        await update.message.reply_text("Envie a foto com a legenda TEMA.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, processar_layout))
    application.run_polling()
