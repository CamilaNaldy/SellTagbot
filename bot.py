import io
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image
# Configuração para economizar memória no servidor
os.environ["ONNXRUNTIME_EXECUTION_PROVIDERS"] = "[CPUExecutionProvider]"
TOKEN = "8250598286:AAEFQVWC205YdEALmAzEITO6kKxwZQDlfx8"
# Criamos uma sessão única para a remoção de fundo não precisar recarregar toda vez
session = new_session()

def get_predominant_color(img):
    img_temp = img.convert('RGB').resize((1, 1), resample=Image.Resampling.LANCZOS)
    return img_temp.getpixel((0, 0))

async def processar_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    legenda = update.message.caption or ""
    foto = update.message.photo

    if legenda.strip().upper() == "TEMA" and foto:
        try:
            status_msg = await update.message.reply_text("Processando imagem (Removendo fundo)...")

            # 1. Baixar a foto
            arquivo_foto = await foto[-1].get_file()
            foto_bytes = await arquivo_foto.download_as_bytearray()
            
            # 2. Remoção de Fundo Otimizada
            img_input = Image.open(io.BytesIO(foto_bytes))
            # Reduzimos um pouco a imagem antes de remover o fundo para não travar a RAM
            if img_input.width > 1000:
                img_input.thumbnail((1000, 1000))
                
            img_sem_fundo = remove(img_input, session=session)

            # 3. Configurações A4 (150 DPI)
            LARGURA_A4 = 1240
            ALTURA_A4 = 1754
            ALTURA_RET = 295  # 5cm
            ESPESSURA_BORDA = 30 # ~5mm
            
            # 4. Criar Folha e Desenhar Borda
            folha = Image.new('RGB', (LARGURA_A4, ALTURA_A4), (255, 255, 255))
            draw = ImageDraw.Draw(folha)
            cor_borda = get_predominant_color(img_sem_fundo)
            
            # Retângulo Branco com Contorno Colorido
            draw.rectangle([0, 0, LARGURA_A4, ALTURA_RET], outline=cor_borda, width=ESPESSURA_BORDA)

            # 5. Redimensionar e Centralizar o Logo (com respiro de 20px)
            largura_max = LARGURA_A4 - (ESPESSURA_BORDA * 2) - 40
            altura_max = ALTURA_RET - (ESPESSURA_BORDA * 2) - 40
            img_sem_fundo.thumbnail((largura_max, altura_max), Image.Resampling.LANCZOS)

            pos_x = (LARGURA_A4 - img_sem_fundo.width) // 2
            pos_y = (ALTURA_RET - img_sem_fundo.height) // 2
            folha.paste(img_sem_fundo, (pos_x, pos_y), img_sem_fundo)

            # 6. Salvar e Enviar
            output = io.BytesIO()
            folha.save(output, format="JPEG", quality=90)
            output.seek(0)
            
            await update.message.reply_document(document=output, filename="layout_final.jpg")
            await status_msg.delete()

        except Exception as e:
            print(f"Erro: {e}")
            await update.message.reply_text("Erro ao processar. Tente uma imagem menor ou mais simples.")
    else:
        await update.message.reply_text("Envie a foto com a legenda TEMA.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, processar_layout))
    application.run_polling()
