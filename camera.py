from threading import Thread, Event, Lock
import cv2

class Camera(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=True)
        self.finished = Event()
        self.ready = Event()
        self._cap = cv2.VideoCapture(0)
        self._frame = None
        self.frame_lock = Lock()

    def stop(self):
        """Stop the timer if it hasn't finished yet."""
        self.finished.set()
    
    def read(self):
        f = None
        self.ready.wait()
        f = self.frame
        self.ready.clear()
        return f
    
    @property
    def frame(self):
        f = None
        with self.frame_lock:
            f = self._frame
        return f
    
    @frame.setter
    def frame(self, f):
        with self.frame_lock:
            self._frame = f

    def run(self):
        while not self.finished.is_set():
            _, self.frame = self._cap.read()
            self.ready.set()
        self._cap.release()
       