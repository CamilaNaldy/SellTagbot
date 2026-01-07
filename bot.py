import io
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from PIL import Image

TOKEN = "8250598286:AAEFQVWC205YdEALmAzEITO6kKxwZQDlfx8"
async def processar_layout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    legenda = update.message.caption or ""
    foto = update.message.photo

    if legenda.strip().upper() == "TEMA" and foto:
        await update.message.reply_text("Gerando layout sem bordas (Rente ao topo)...")

        # 1. Baixar a foto enviada
        arquivo_foto = await foto[-1].get_file()
        foto_bytes = await arquivo_foto.download_as_bytearray()
        img_usuario = Image.open(io.BytesIO(foto_bytes))

        # 2. Configurações A4 em 150 DPI
        LARGURA_A4 = 1240
        ALTURA_A4 = 1754
        ALTURA_RETANGULO = 472 # Exatos 8cm em 150 DPI

        # 3. Criar Folha Branca (O fundo garante o restante vazio)
        folha = Image.new('RGB', (LARGURA_A4, ALTURA_A4), (255, 255, 255))

        # 4. Ajustar imagem do usuário para preencher EXATAMENTE o retângulo de 8cm
        # Usamos o 'fit' para que ela cubra toda a largura e altura de 8cm
        # sem deixar espaços brancos nas laterais do retângulo.
        img_ajustada = Image.getoutput = Image.new('RGB', (LARGURA_A4, ALTURA_RETANGULO))
        
        # Redimensiona a imagem para cobrir a área de 8cm x largura total
        from PIL import ImageOps
        img_final_cabecalho = ImageOps.fit(img_usuario, (LARGURA_A4, ALTURA_RETANGULO), Image.Resampling.LANCZOS)

        # 5. Colar na posição (0,0) - Rente ao topo e às laterais
        folha.paste(img_final_cabecalho, (0, 0))

        # 6. Salvar e Enviar
        output = io.BytesIO()
        folha.save(output, format="JPEG", quality=95)
        output.seek(0)
        
        await update.message.reply_document(
            document=output, 
            filename="layout_sem_bordas.jpg",
            caption="Aqui está o layout A4. Cabeçalho de 8cm rente às bordas."
        )
    else:
        await update.message.reply_text("Comando inválido. Envie a foto com a legenda TEMA.")

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, processar_layout))
    application.run_polling()
