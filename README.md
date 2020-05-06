# Bodypix-Background

Adds a different background to your video feed. 

This is made in part by the hard work of many people:

- Dan Oved and Tyler Zhu for the [Bodypix model](https://blog.tensorflow.org/2019/11/updated-bodypix-2.html).
- [Ben Elder](https://elder.dev/posts/open-source-virtual-background/) and [Daniel Llewellyn](https://snapcraft.io/fakecam) for their implementations

Daniel Llewellyn has the highest polish solution so far, making it easily installable under Linux as a snap package.

This solution aims for lower latency through the following ways
- Uses ZeroMQ IPC for communication between the TFJS model and the image processing
- Less transformations
- If blurred background is chosen, only the first frame is captured and blurred

## Setup

First we need to install the nodejs and python parts.

```bash
npm install
pip install .
```

Next we need to setup the `v4l2loopback` kernel module for the fake webcam.

To install,

```bash
 sudo apt install v4l2loopback-dkms
```

If you already had an existing module, remove it so we can customize it,
```bash
 sudo modprobe -r v4l2loopback
```

Create a file in `/etc/modprobe.d/fakecam.conf` and add the following:
```
options v4l2loopback devices=1 video_nr=20 card_label=fakecam exclusive_caps=1
```

Finally, load the kernel module
```bash
sudo modprobe v4l2loopback
```

Then we can start the script with `./start.sh`.
