import os
import streamlit as st
import google.generativeai as genai
import re

# Formateador de entrevistas.

error_flag = False  # Global variable to track error display

def clean_text(text):
    # Clean punctuation and special characters using regular expressions
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return cleaned_text

def generate_response(cleaned_input, model):
    global error_flag  # Use the global error_flag variable

    try:
        # Generate response using the model
        response = model.generate_content(cleaned_input, stream=True)

        # Display the generated response
        full_response = ""
        for chunk in response:
            full_response += chunk.text

        return full_response

    except Exception as e:
        error_message = str(e)
        if "text must be a valid text with maximum 5000 character" in error_message and not error_flag:
            error_response = ("The question you are asking may go against Google GEMINI policies: WiseOracle"
                              "Please reformulate your question without forbidden topics or ask something else. "
                              "For more information, see: https://policies.google.com/terms/generative-ai/use-policy "
                             )
            st.error(error_response)
            error_flag = True  # Set the error_flag to True after displaying the error message
            return error_response
        else:
            error_response = f"Error: {error_message}\nSorry, I am an artificial intelligence that is still in development and is in alpha phase. At the moment, I cannot answer your question properly, but in the future, I will be able to do so."
            st.error(error_response)
            return error_response

# Aplicación Streamlit
def principal():
    st.title("Formateador de Entrevistas")

    genai.configure(api_key='your_gemini_api_key')  # Replace with your Google GEMINI API key

    # Choose the Gemini model
    model = genai.GenerativeModel('gemini-pro')

    # Cargador de archivos para el archivo .txt
    archivo_cargado = st.file_uploader("Cargar un archivo .txt", type=["txt"])

    if archivo_cargado is not None:
        # Lee el contenido del archivo cargado
        contenido = archivo_cargado.read()

        # Botón para iniciar el formateo
        if st.button("Iniciar Formateo"):
            st.info("Formateo en progreso...")

            # Divide el contenido en chunks de 1000 palabras
            tamano_chunk = 1000
            chunks = [contenido[i:i + tamano_chunk] for i in range(0, len(contenido), tamano_chunk)]

            # Inicializa la barra de progreso
            barra_progreso_chunks = st.progress(0)

            # Procesa cada chunk y muestra la salida formateada
            salida_formateada = ""
            for i, chunk in enumerate(chunks):
                respuesta_bot = generate_response(
                    f"No hay comentarios ni indicaciones. Simplemente sigue las instrucciones: lee línea por línea, frase por frase, identifica y reconoce los roles del entrevistador y el entrevistado en el siguiente texto de un segmento de entrevista, y formatea la salida como ese segmento de entrevista con etiquetas precediendo cada línea, palabra o frase con etiquetas de entrevistador y entrevistado. Presenta el mismo orden de desarrollo del segmento de entrevista con un salto de línea entre cada uno. Etiqueta cada palabra, línea, frase o párrafo según corresponda: {chunk}",
                    model
                )

                # Decode ASCII characters
                respuesta_bot = respuesta_bot.encode().decode('unicode_escape')

                # Agrega la respuesta formateada a la salida
                salida_formateada += respuesta_bot + "\n"

                # Actualiza la barra de progreso
                barra_progreso_chunks.progress((i + 1) / len(chunks))

            # Muestra la salida formateada
            st.success("Formateo completado")
            st.text_area("Segmento de Entrevista Formateado:", salida_formateada)

            # Botón para descargar la respuesta formateada
            download_button = st.download_button(
                label="Descargar Respuesta",
                data=salida_formateada,
                file_name="respuesta_formateada.txt",
                key="download_button"
            )

if __name__ == "__main__":
    principal()
