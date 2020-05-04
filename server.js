const zmq = require('zeromq');
const tf = require('@tensorflow/tfjs-node');
const bodyPix = require('@tensorflow-models/body-pix');
const {decodeJpeg} = require('./decode_image');

async function main() {
	const net = await bodyPix.load({
		architecture: 'MobileNetV1',
		outputStride: 16,
		multiplier: 0.5,
		quantBytes: 2
	});
	const sock = new zmq.Reply;

	await sock.bind('ipc:///tmp/bodypix');
	console.log("Bounded to ipc:///tmp/bodypix");

	for await (const [msg] of sock) {
		const image = decodeJpeg(msg)
		const segmentation = await net.segmentPerson(image);
		await sock.send(segmentation.data);
		tf.dispose(image)
	}
}

main();
