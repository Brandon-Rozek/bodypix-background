import zmq
import cv2
from pyfakewebcam import FakeWebcam
import numpy as np
from camera import Camera
from argparse import ArgumentParser
from signal import signal, SIGINT

def process_mask(m, shape):
    w, h = shape
    m = np.frombuffer(m, dtype=np.uint8).reshape((w, h, -1))
    m = m[:, :, 0].astype(np.float32)
    m = cv2.blur(cv2.UMat(m), (30, 30))
    return m.get()

def composite(foreground, backdrop, fore_mask):
    inv_mask = 1 - fore_mask
    for c in range(foreground.shape[2]):
        foreground[:, :, c] = foreground[:, :, c] * fore_mask + backdrop[:, :, c] * inv_mask
    return foreground


def get_background(uri=None):
    """
        Either grabs the image specified or
        blurs the current background.
    """
    initial_frame = camera.read()
    w, h = initial_frame.shape[0], initial_frame.shape[1]
    backdrop = None
    if uri is not None:
        backdrop = cv2.resize(
            cv2.UMat(cv2.imread(uri)),
            (h, w)
        ).get().astype(np.uint8)
    else:
        backdrop = cv2.GaussianBlur(initial_frame, (221, 221), sigmaX=20, sigmaY=20).astype(np.uint8)
    return backdrop, (w, h)


def stop(signal_received, stack_frame):
    """Gracefully stops the application."""
    global running
    running = False
    print("Stopping...")

parser = ArgumentParser(description="Virtual Backgrounds with Bodypix")
parser.add_argument(
    "--background",
    type=str,
    help="The background to use. If not specified, will be a blur of the initial frame."
)
args = vars(parser.parse_args())


# Start Camera
camera = Camera()
camera.start()

if __name__ == "__main__":
    signal(SIGINT, stop)

    # Setup ZeroMQ
    ctx = zmq.Context() 
    sock = ctx.socket(zmq.REQ)
    sock.connect('ipc:///tmp/bodypix')

    background, (width, height) = get_background(args['background'])
    fake = FakeWebcam('/dev/video20', height, width)

    running = True
    print("Running...")
    
    while running:
        frame = camera.read()
        _, image = cv2.imencode('.jpg', frame)
        frame = frame.astype(np.uint8)

        # Process image to find body masks
        sock.send(image.tostring())
        mask = process_mask(sock.recv(), (width, height))

        frame = composite(frame, background, mask)

        # Send to the fake camera device
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        fake.schedule_frame(frame)
