{'clip': {'url': '{{ video_info.video.get_absolute_url }}',
          'autoPlay': true,
          'screencolor': '0x666666',
          'volume': 50,
          {% if video_info.height %}'height': {{ video_info.height }},{% endif %}
          {% if video_info.width %}'width': {{ video_info.width }},{% endif %}
          'thumbsinplaylist': true,
          'allowfullscreen': true,
          'height': 10,
          'width': 20,
          'coverImage': {'url': '{{ THEME_MEDIA_URL }}img/video_preview.jpg', 'scaling': 'orig'}}}
