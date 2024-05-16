import boto3
import os
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


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


# Run inference on images and compute metrics
def run_inference_on_images(model_arn, images_path):
    client = boto3.client('rekognition')
    y_true = []
    y_pred = []

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
                    y_true.append(category.lower())
                    if 'mefo' in labels:
                        y_pred.append('mefo')
                    elif 'negativ' in labels:
                        y_pred.append('negativ')
                    else:
                        y_pred.append('unknown')
                except client.exceptions.ImageTooLargeException:
                    print(f'Error: Image size is too large for {image_path}')
                except Exception as e:
                    print(f'Error: {e} for {image_path}')

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    print(f'Accuracy: {accuracy:.4f}')
    print(f'Precision: {precision:.4f}')
    print(f'Recall: {recall:.4f}')
    print(f'F1 Score: {f1:.4f}')


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
