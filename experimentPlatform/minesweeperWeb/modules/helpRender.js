let preloaded_assets = {}

export function preloadURL(src, key) {
    let preloadedImg = document.createElement("img");
    preloadedImg.src = src;

	return new Promise((resolve) => preloadedImg.onload = () => {
        preloaded_assets[key] = preloadedImg;
        resolve();
        // console.log("resolved asset " + key);
    });
}

export function placeURL(src, context, x, y, deg=0) {
    let imgObj = new Image();
    imgObj.src = src

    // draw image at 0,0 and restore un-adjusted canvas draw settings
    imgObj.onload = () => {
        // save current canvas rotation/position
        context.save();
        context.translate(x, y); // translate the canvas position
        context.rotate(deg*Math.PI/180); // rorate the canvas draw pos

        context.drawImage(imgObj, 0, 0);

        context.restore(); }
}

export function placePreloaded(context, key, x, y, deg=0) {
    // WARNING: check for key presence in dict?
    let imgObj = preloaded_assets[key]

    // draw image at 0,0 and restore un-adjusted canvas draw settings
    context.save();
    context.translate(x, y); // translate the canvas position
    context.rotate(deg*Math.PI/180); // rorate the canvas draw pos

    context.drawImage(imgObj, 0, 0);

    context.restore();
}
