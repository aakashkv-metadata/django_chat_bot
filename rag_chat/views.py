from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UploadedDocument
from .utils import ingest_document, get_answer
import os

def index(request):
    return render(request, 'rag_chat/index.html')

@csrf_exempt
def upload_document(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Save to DB and Disk
        doc = UploadedDocument.objects.create(file=uploaded_file)
        
        # Ingest (could be async in production)
        try:
            ingest_document(doc.file.path)
            doc.processed = True
            doc.save()
            return JsonResponse({'status': 'success', 'message': 'File uploaded and processed successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        query = data.get('query')
        
        if not query:
            return JsonResponse({'error': 'No query provided'}, status=400)
            
        try:
            answer = get_answer(query)
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)
