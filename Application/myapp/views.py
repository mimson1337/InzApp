from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from bs4 import BeautifulSoup as bs
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import whisper
import os
from .models import AudioFile
import audio_metadata
from django.core.files.storage import FileSystemStorage
import logging
import re

#20.51 tiny 89.61%
#29.12 base 91.62%
#small 1:12:00 92.36%
#medium 3:09:00 94.26%
#large 16:57 93.27%


# , device="cuda"
model = whisper.load_model("tiny")
os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg\ffmpeg.exe"


def home(request):
    return render(request, "home.html")


def search_records(request):
    return render(request, "search.html")


logger = logging.getLogger(__name__)
related_to_depression = False


@csrf_exempt
def transcribe(request):
    if request.method == 'POST':
        transcription_results = []
        found_keywords = []
        try:
            # Pobierz słowa kluczowe z żądania i przetwórz
            keywords = []
            if 'mp3_files' in request.FILES:
                keywords = request.POST.get('keywords', '').split(' and ')
            else:
                data = json.loads(request.body)
                keywords = data.get('keywords', '').split(' and ')

            keywords = [kw.strip().lower() for kw in keywords if kw.strip()]


            def highlight_keywords(text, keywords):
                for kw in set(keywords):
                    text = re.sub(rf'\b({re.escape(kw)})\b', r'<mark>\1</mark>', text, flags=re.IGNORECASE)
                return text

            def process_transcription(transcription_text, source, duration):
                transcription_text_lower = transcription_text.lower()

                keywords_found = [kw for kw in keywords if kw.lower() in transcription_text_lower]
                related_to_depression = len(keywords_found) > 0
                found_keywords.extend(keywords_found)

                highlighted_text = highlight_keywords(transcription_text, keywords_found)

                AudioFile.objects.create(
                    url=source,
                    transcription_text=transcription_text,
                    duration=duration,
                    related_to_depression=related_to_depression,
                    found_keywords=', '.join(set(keywords_found))
                )
                return highlighted_text

            # Przetwarzanie przesłanych plików
            if 'mp3_files' in request.FILES:
                for uploaded_file in request.FILES.getlist('mp3_files'):
                    fs = FileSystemStorage()
                    filename = fs.save(uploaded_file.name, uploaded_file)
                    file_path = fs.path(filename)
                    metadata = audio_metadata.load(file_path)
                    duration = metadata.streaminfo['duration']
                    result = model.transcribe(file_path)
                    transcription_results.append(
                        process_transcription(result['text'], filename, duration)
                    )
            else:
                # Przetwarzanie plików z URL
                mp3_links = json.loads(request.body).get('mp3s', [])
                for mp3_link in mp3_links:
                    response = requests.get(mp3_link)
                    if response.status_code == 200:
                        audio_path = f"temp_{mp3_link.split('/')[-1]}"
                        with open(audio_path, 'wb') as f:
                            f.write(response.content)
                        metadata = audio_metadata.load(audio_path)
                        duration = metadata.streaminfo['duration']
                        result = model.transcribe(audio_path)
                        transcription_results.append(
                            process_transcription(result['text'], mp3_link, duration)
                        )

            return JsonResponse({
                'transcription': '\n'.join(transcription_results),
                'found_keywords': list(set(found_keywords)),
                'message': ''
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)



@csrf_exempt
def search(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        url = data.get('url')

        if not url:
            return JsonResponse({'error': 'URL not provided'}, status=400)

        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            driver.get(url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'a'))
            )

            page_source = driver.page_source
            driver.quit()

            soup = bs(page_source, 'html.parser')
            results = []

            # Zbieranie linków do plików audio
            for tag in soup.find_all('a'):
                href = tag.get('href')
                if href and (href.endswith('.mp3') or href.endswith('.wav')):
                    results.append(href)

            for source in soup.find_all('source'):
                src = source.get('src')
                if src and (src.endswith('.mp3') or src.endswith('.wav')):
                    results.append(src)

            # Usuwanie duplikatów za pomocą `set`
            unique_results = list(set(results))

            return JsonResponse(unique_results, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
