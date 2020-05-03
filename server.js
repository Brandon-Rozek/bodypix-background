const zmq = require('zeromq');
const tf = require('@tensorflow/tfjs-node');
const bodyPix = require('@tensorflow-models/body-pix');
const {decodeJpeg} = require('./decode_image');

let net = null;

async function load() {
	net = await bodyPix.load({
		architecture: 'MobileNetV1',
		outputStride: 16,
		multiplier: 0.5,
		quantBytes: 2
	});
}

async function run() {
	const sock = new zmq.Reply;

	await sock.bind('ipc:///tmp/bodypix');
	console.log("Bounded to ipc:///tmp/bodypix");

	for await (const [msg] of sock) {
		console.log("Received RAW Message");
		const image = decodeJpeg(msg)
		const segmentation = await net.segmentPerson(image);
		await sock.send(segmentation.data);
		tf.dispose(image)
	}
}

load();
run();
