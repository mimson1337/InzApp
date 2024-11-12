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


model = whisper.load_model("base")
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
            # local files
            if 'mp3_files' in request.FILES:
                uploaded_files = request.FILES.getlist('mp3_files')
                keywords = request.POST.get('keywords', '').split(',')

                for uploaded_file in uploaded_files:
                    fs = FileSystemStorage()
                    filename = fs.save(uploaded_file.name, uploaded_file)
                    file_path = fs.path(filename)

                    metadata = audio_metadata.load(file_path)
                    duration = metadata.streaminfo['duration']

                    result = model.transcribe(file_path)
                    transcription_text = result['text']
                    transcription_results.append(transcription_text)

                    # looking for keywords
                    keywords_found_in_file = [kw for kw in keywords if kw.lower() in transcription_text.lower()]
                    found_keywords.extend(keywords_found_in_file)

                    # if keyowrds found -> related = true
                    related_to_depression = bool(keywords_found_in_file)

                    AudioFile.objects.create(
                        url=None,
                        local_file=filename,
                        transcription_text=transcription_text,
                        duration=duration,
                        related_to_depression=related_to_depression,
                        found_keywords=', '.join(keywords_found_in_file)
                    )

            # links
            else:
                data = json.loads(request.body)
                mp3_links = data.get('mp3s', [])
                keywords = data.get('keywords', [])

                for mp3_link in mp3_links:
                    response = requests.get(mp3_link)

                    if response.status_code == 403:
                        continue

                    if response.status_code != 200:
                        return JsonResponse({'error': f'Failed to download file: {mp3_link}'}, status=400)

                    audio_path = f"temp_{mp3_link.split('/')[-1]}"
                    with open(audio_path, 'wb') as f:
                        f.write(response.content)

                    metadata = audio_metadata.load(audio_path)
                    duration = metadata.streaminfo['duration']

                    result = model.transcribe(audio_path)
                    transcription_text = result['text']
                    transcription_results.append(transcription_text)

                    # looking for keywords in transcription
                    keywords_found_in_file = [kw for kw in keywords if kw.lower() in transcription_text.lower()]
                    found_keywords.extend(keywords_found_in_file)

                    # if keyowrds found -> related = true
                    related_to_depression = bool(keywords_found_in_file)

                    AudioFile.objects.create(
                        url=mp3_link,
                        transcription_text=transcription_text,
                        duration=duration,
                        related_to_depression=related_to_depression,
                        found_keywords=', '.join(keywords_found_in_file)
                    )

            return JsonResponse({
                'transcription': '\n'.join(transcription_results),
                'found_keywords': list(set(found_keywords)),
                'message': 'Files processed and saved to database.'
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

            for tag in soup.find_all('a'):
                href = tag.get('href')
                if href and (href.endswith('.mp3') or href.endswith('.wav')):
                    results.append(href)

            for source in soup.find_all('source'):
                src = source.get('src')
                if src and (src.endswith('.mp3') or src.endswith('.wav')):
                    results.append(src)

            return JsonResponse(results, safe=False)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)