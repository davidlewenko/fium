import cv2
import boto3
import os
from urllib.parse import unquote_plus

s3_client = boto3.client('s3')

def handler(event, context):
    source_bucket = event['Records'][0]['s3']['bucket']['name']
    source_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
    target_bucket = 'fiumlandingvideodata'
    image_prefix = 'images/'  # Customize this if you need to store images in a specific sub-folder

    # Download video from S3 to the /tmp folder (note: AWS Lambda has limited disk space)
    local_video_path = '/tmp/' + source_key.split('/')[-1]
    s3_client.download_file(source_bucket, source_key, local_video_path)

    # Load the video
    video = cv2.VideoCapture(local_video_path)
    success, image = video.read()
    count = 0

    # Read frames
    while success:
        # Convert frame to format suitable for S3 upload
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()

        # Upload image to S3
        target_key = f'{image_prefix}{source_key.split(".")[0]}_frame_{count}.jpg'
        s3_client.put_object(Bucket=target_bucket, Key=target_key, Body=image_bytes)
        success, image = video.read()
        count += 1

    # Clean up the video file from /tmp
    if os.path.exists(local_video_path):
        os.remove(local_video_path)

    return {
        'statusCode': 200,
        'body': f'Successfully processed {count} frames from {source_key} and uploaded to {target_bucket}'
    }
