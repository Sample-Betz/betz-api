from django.http import JsonResponse

##### UTILS #####

def error(message: str, code: int):
    return JsonResponse({'error': message}, status=code)