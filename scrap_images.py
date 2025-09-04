# scrap images
import os
from django.shortcuts import redirect
import requests
def download_image(url, save_path):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP errors
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image downloaded successfully: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
    return redirect('pg_listings')

def scrap_images(request):
    image_urls = [
        'https://example.com/image1.jpg',
        'https://example.com/image2.jpg',
        'https://example.com/image3.jpg',
    ]

    save_directory = 'static/images/pg_images'
    os.makedirs(save_directory, exist_ok=True)

    for i, url in enumerate(image_urls):
        save_path = os.path.join(save_directory, f'image_{i+1}.jpg')
        download_image(url, save_path)

    return redirect('pg_listings')
    return render(request, 'main_app/register_tenant.html', {'pg': pg})

