import aws_cdk as core
import aws_cdk.assertions as assertions

from video_splitter.video_splitter_stack import VideoSplitterStack

# example tests. To run these tests, uncomment this file along with the example
# resource in video_splitter/video_splitter_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = VideoSplitterStack(app, "video-splitter")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
