from django.test import TestCase, Client
from django.urls import reverse
from .models import AudioFile
import json


class TranscriptionTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_transcribe_with_keywords(self):
        audio_file_path = 'audiofile.mp3'
        with open(audio_file_path, 'rb') as audio_file:
            response = self.client.post(
                reverse('transcribe'),
                {'mp3_files': [audio_file], 'keywords': 'depression and anxiety'}
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('transcription', data)
        self.assertIn('found_keywords', data)

    def test_transcription_saves_to_database(self):
        url = "https://depressedanon.com/wp-content/uploads/conference/2023/DA-Hope-Session1-Moore.mp3"

        """Test, if transcription is being saved in the database """
        AudioFile.objects.create(
            url=url,
            transcription_text="This is a test transcription.",
            duration=10.0,
            related_to_depression=True,
            found_keywords="test"
        )
        audio_file = AudioFile.objects.get(url=url)
        self.assertEqual(audio_file.transcription_text, "This is a test transcription.")
        self.assertTrue(audio_file.related_to_depression)


class SearchTestCase(TestCase):
    def test_search_finds_audio_links(self):
        response = self.client.post(
            reverse('search'),
            data=json.dumps({'url': 'https://freesound.org/people/bjornbradley/sounds/723502/'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
