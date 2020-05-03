import zmq
import cv2
import numpy as np

ctx = zmq.Context() 
sock = ctx.socket(zmq.REQ)
sock.connect('ipc:///tmp/bodypix')
cap = cv2.VideoCapture(0)
while True:
    _, frame = cap.read()
    _, image = cv2.imencode('.jpg', frame)

    print("LENGTH", len(image.tostring()), flush=True)
    sock.send(image.tostring())
    convereted_img = sock.recv()

    mask = np.frombuffer(convereted_img, dtype=np.uint8)
    mask = mask.reshape((frame.shape[0], frame.shape[1], 4))
    mask = mask[:, :, 0]

    # post-process mask and frame
    mask = cv2.UMat(mask)
    mask = cv2.dilate(mask, np.ones((10, 10), np.uint8), iterations=1)
    mask = cv2.blur(cv2.UMat(mask.get().astype(np.float32)), (30, 30))

    frame = cv2.UMat(frame)
    background = cv2.GaussianBlur(frame, (221, 221), sigmaX=20, sigmaY=20)

    # composite the foreground and background
    frame = frame.get().astype(np.uint8)
    mask = mask.get().astype(np.float32)
    background = background.get().astype(np.uint8)
    inv_mask = 1 - mask
    for c in range(frame.shape[2]):
        frame[:, :, c] = frame[:, :, c] * mask + background[:, :, c] * inv_mask

    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
  
cap.release()
cv2.destroyAllWindows()
