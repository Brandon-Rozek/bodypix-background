const zmq = require('zeromq');
const tf = require('@tensorflow/tfjs-node');
const bodyPix = require('@tensorflow-models/body-pix');
const {decodeJpeg} = require('./decode_image');

/*
 * outputStride: Specifies the output stride of the BodyPix model.
 * The smaller the value, the larger the output resolution, and more accurate
 * the model at the cost of speed. Set this to a larger value to increase speed
 * at the cost of accuracy. Stride 32 is supported for ResNet and
 * stride 8,16,32 are supported for various MobileNetV1 models.
 */

/*
 * multiplier: An optional number with values: 1.01, 1.0, 0.75, or
 * 0.50. The value is used only by MobileNet architecture. It is the float
 * multiplier for the depth (number of channels) for all convolution ops.
 * The larger the value, the larger the size of the layers, and more accurate
 * the model at the cost of speed. Set this to a smaller value to increase speed
 * at the cost of accuracy.
 */

/*
 * quantBytes: An optional number with values: 1, 2, or 4.  This parameter
 * affects weight quantization in the models. The available options are
 * 1 byte, 2 bytes, and 4 bytes. The higher the value, the larger the model size
 * and thus the longer the loading time, the lower the value, the shorter the
 * loading time but lower the accuracy.
 */

async function main() {
	const net = await bodyPix.load({
		architecture: 'ResNet50',
		outputStride: 16, 
		multiplier: 1.0,
		quantBytes: 4
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
