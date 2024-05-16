import boto3
import os

def create_dirs(base_path, dir_names):
    for dir_name in dir_names:
        path = os.path.join(base_path, dir_name)
        os.makedirs(path, exist_ok=True)

def resolve_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

# Start the model function
def start_model(project_arn, model_arn, version_name, min_inference_units):
    client = boto3.client('rekognition')
    try:
        print('Starting model: ' + model_arn)
        response = client.start_project_version(ProjectVersionArn=model_arn, MinInferenceUnits=min_inference_units)
        project_version_running_waiter = client.get_waiter('project_version_running')
        project_version_running_waiter.wait(ProjectArn=project_arn, VersionNames=[version_name])
        describe_response = client.describe_project_versions(ProjectArn=project_arn, VersionNames=[version_name])
        for model in describe_response['ProjectVersionDescriptions']:
            print("Status: " + model['Status'])
            print("Message: " + model['StatusMessage'])
    except Exception as e:
        print(e)
    print('Model started.')

# Run inference on images
def run_inference_on_images(model_arn, images_path):
    client = boto3.client('rekognition')
    misclassified_mefo = 0
    misclassified_negativ = 0
    total_mefo = 0
    total_negativ = 0

    for category in ['MEFO', 'negativ']:
        category_path = os.path.join(images_path, category)
        for image_file in os.listdir(category_path):
            if image_file.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_path = os.path.join(category_path, image_file)
                try:
                    with open(image_path, 'rb') as image:
                        response = client.detect_custom_labels(
                            ProjectVersionArn=model_arn,
                            Image={'Bytes': image.read()}
                        )
                    labels = [label['Name'] for label in response['CustomLabels']]
                    print(f'Image: {image_path}, Labels: {labels}')
                    if category == 'MEFO':
                        total_mefo += 1
                        if 'mefo' not in labels:
                            misclassified_mefo += 1
                    elif category == 'negativ':
                        total_negativ += 1
                        if 'negativ' not in labels:
                            misclassified_negativ += 1
                except client.exceptions.ImageTooLargeException:
                    print(f'Error: Image size is too large for {image_path}')
                except Exception as e:
                    print(f'Error: {e} for {image_path}')

    print(f'Total MEFO images: {total_mefo}, Misclassified MEFO images: {misclassified_mefo}')
    print(f'Total NEGATIV images: {total_negativ}, Misclassified NEGATIV images: {misclassified_negativ}')

def main():
    # Start the model
    project_arn = 'arn:aws:rekognition:eu-central-1:891376916269:project/fium-test/1715165009415'
    model_arn = 'arn:aws:rekognition:eu-central-1:891376916269:project/fium-test/version/fium-test.2024-05-15T17.23.08/1715786588706'
    version_name = 'fium-test.2024-05-15T17.23.08'
    min_inference_units = 1
    start_model(project_arn, model_arn, version_name, min_inference_units)

    # Run inference
    images_path = resolve_path('../data/testing_data')
    run_inference_on_images(model_arn, images_path)

if __name__ == "__main__":
    main()
