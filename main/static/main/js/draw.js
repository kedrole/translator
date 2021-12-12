var canvas = this.__canvas = new fabric.Canvas('c');
// create a rect object
var deleteIcon = "data:image/svg+xml,%3C%3Fxml version='1.0' encoding='utf-8'%3F%3E%3C!DOCTYPE svg PUBLIC '-//W3C//DTD SVG 1.1//EN' 'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'%3E%3Csvg version='1.1' id='Ebene_1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' x='0px' y='0px' width='595.275px' height='595.275px' viewBox='200 215 230 470' xml:space='preserve'%3E%3Ccircle style='fill:%23F44336;' cx='299.76' cy='439.067' r='218.516'/%3E%3Cg%3E%3Crect x='267.162' y='307.978' transform='matrix(0.7071 -0.7071 0.7071 0.7071 -222.6202 340.6915)' style='fill:white;' width='65.545' height='262.18'/%3E%3Crect x='266.988' y='308.153' transform='matrix(0.7071 0.7071 -0.7071 0.7071 398.3889 -83.3116)' style='fill:white;' width='65.544' height='262.179'/%3E%3C/g%3E%3C/svg%3E";

var img = document.createElement('img');
img.src = deleteIcon;

originalImgPath = ''
selected_elem = NaN

fabric.Object.prototype.transparentCorners = false;
fabric.Object.prototype.cornerColor = 'blue';
fabric.Object.prototype.cornerStyle = 'circle';

function AddText() {
    var text = new fabric.Text('hello world', {
        left: 100,
        top: 100,
        fill: "rgb(0,0,0)",
        fontFamily: 'Impact',
        fontSize: 40,
        fontWeight: 'normal', /* bold */
        //stroke: '#ff1318',
        //strokeWidth: 1,
        textAlign: 'center', /* «left», «center», «right», и «justify» */
        lineHeight: 1,
        textBackgroundColor: 'rgb(255,255,255)'
    });

    text.on('mouseup', function (e) {
        selected_elem = e.target
        setTextColorAndBg(e.target)
    });

    text.on('mousedown', readTextParams)

    readTextParams(text)
    setTextColorAndBg(text);
    selected_elem = text

    canvas.add(text);
    canvas.setActiveObject(text);
}

function readTextParams(e) {
    elem = e
    if (e.hasOwnProperty('e')) elem = e.target
    
    document.getElementById('txt_text').value = elem.text
    document.getElementById('txt_text_font').value = elem.fontFamily
    document.getElementById('txt_text_size').value = elem.fontSize
    document.getElementById('txt_line_height').value = elem.lineHeight

    if (elem.fontWeight == 'normal') document.getElementById('txt_bold').checked = false
    else document.getElementById('txt_bold').checked = true
}

async function setTextColorAndBg(t) {
    base64 = await cropImg(originalImgPath, t.width, t.height, t.left, t.top, t.scaleX, t.scaleY, scaleFactor, )
    color = await getDominantColor(base64)

    //console.log(color)
    t.textBackgroundColor = color.dominant
    t.fill = get_text_color_that_diff_from_bg(color.dominant, color.palette, allowable_diff=150, min_allowable_diff=90)
    //console.log(t.fill)
    t.dirty = true
    canvas.renderAll();
}

function parse_rgb(rgb_str) {
    rgb_str = rgb_str.substr(4, rgb_str.length - 5)
    res = rgb_str.split(',')
    return res
}

function calculate_color_difference(first_r_g_b, second_r_g_b) {
    return Math.sqrt(Math.pow(first_r_g_b[0] - second_r_g_b[0], 2) + Math.pow(first_r_g_b[1] - second_r_g_b[1], 2) + Math.pow(first_r_g_b[2] - second_r_g_b[2], 2))
}

function get_text_color_that_diff_from_bg(dominant, palette, allowable_diff, min_allowable_diff) {
    // Разложить Доминантный цвет (цвет фона) в массив [r, g, b]
    dominant_r_g_b = parse_rgb(dominant)

    max_diff = 0
    max_diff_color = dominant_r_g_b

    // Пройтись по всем остальным цветам (по убыванию популярности цвета)
    for (let color of palette) {
        color_r_g_b = parse_rgb(color)

        diff = calculate_color_difference(dominant_r_g_b, color_r_g_b)

        // Если цвет отличается больше чем на пороговое значение - вернуть его
        if (diff > allowable_diff) return "rgb(" + color_r_g_b.join() + ")"

        // Иначе искать цвет, отличающийся больше всего от доминантного
        if (diff > max_diff) {
            max_diff = diff
            max_diff_color = color_r_g_b
        }
    }

    // Если цвет, отличающийся больше всего от доминантного не слишком схож с ним, то вернуть его
    if (max_diff > min_allowable_diff) {
        return "rgb(" + max_diff_color.join() + ")"
    }
    // Если цвет, отличающийся больше всего от доминантного слишком схож с доминантным, то вернуть белый или черный цвет
    else {
        dominant_and_white_diff = calculate_color_difference(dominant_r_g_b, [255, 255, 255])
        dominant_and_black_diff = calculate_color_difference(dominant_r_g_b, [0, 0, 0])
        if (dominant_and_black_diff > dominant_and_white_diff) {
            return "rgb(0,0,0)"
        }
        return "rgb(255,255,255)"
    }
}

fabric.Object.prototype.controls.deleteControl = new fabric.Control({
    x: 0.5,
    y: -0.5,
    offsetY: 16,
    cursorStyle: 'pointer',
    mouseUpHandler: deleteObject,
    render: renderIcon,
    cornerSize: 24
});

function deleteObject(eventData, transform) {
    var target = transform.target;
    var canvas = target.canvas;
        canvas.remove(target);
    canvas.requestRenderAll();
}

function renderIcon(ctx, left, top, styleOverride, fabricObject) {
    var size = this.cornerSize;
    ctx.save();
    ctx.translate(left, top);
    ctx.rotate(fabric.util.degreesToRadians(fabricObject.angle));
    ctx.drawImage(img, -size/2, -size/2, size, size);
    ctx.restore();
}

function setCanvasBgImage(baseWidth) {
    const img1 = new Image();
    img1.src = originalImgPath;
    img1.onload = function() {
      whRatio = this.width / this.height
      canvas.setWidth(baseWidth);
      canvas.setHeight(baseWidth * this.height / this.width);
    
      scaleFactor = baseWidth / this.width
      canvas.setBackgroundImage(originalImgPath, canvas.renderAll.bind(canvas), {
          top: 0,
          left: 0,
          originX: 'left',
          originY: 'top',
          scaleX: scaleFactor,
          scaleY: scaleFactor
      });
      canvas.renderAll();
    }    
}

function cropImg(path, width, height, left, top, scaleX, scaleY, scaleFactor) {
    return new Promise((resolve, reject) => {
        var canv = document.getElementById('cropCanvas');
        var context = canv.getContext('2d');
        var imageObj = new Image();
      
        imageObj.onload = function() {
          canv.width = width * scaleX
          canv.height = height* scaleY
    
          context.drawImage(imageObj, left / scaleFactor, top / scaleFactor, width / scaleFactor * scaleX, height / scaleFactor * scaleY, 0, 0, width * scaleFactor * scaleX, height * scaleFactor * scaleY);
          resolve(canv.toDataURL())
        };
        imageObj.src = path;
    })
}

function getDominantColor(img) {
    return new Promise((resolve, reject) => {
        RGBaster.colors(img, {
            // Не учитывать белый цвет
            //exclude: ['rgb(255,255,255)'],
            success: function(payload) {
                resolve(payload);  // Преобладающий цвет
                // console.log(payload.palette);   // Палитра цветов (по умолчанию 30)
                // Устанавливаем фоновый цвет равный самому популярному.
                //document.body.style.background = payload.dominant;
            }
            });
    })
}

function imageToBase64(img)
{
    var canvas, ctx, dataURL, base64;
    canvas = document.createElement("canvas");
    ctx = canvas.getContext("2d");
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);
    dataURL = canvas.toDataURL("image/png");
    base64 = dataURL.replace(/^data:image\/png;base64,/, "");
    return base64;
}

function resizedataURL(datas, wantedWidth, wantedHeight){
    return new Promise(function(resolve,reject){

        // We create an image to receive the Data URI
        var img = document.createElement('img');

        // When the event "onload" is triggered we can resize the image.
        img.onload = function()
        {        
            // We create a canvas and get its context.
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');

            // We set the dimensions at the wanted size.
            canvas.width = wantedWidth;
            canvas.height = wantedHeight;

            // We resize the image with the canvas method drawImage();
            ctx.drawImage(this, 0, 0, wantedWidth, wantedHeight);

            var dataURI = canvas.toDataURL();

            // This is the return of the Promise
            resolve(dataURI);
        };

        // We put the Data URI in the image's src attribute
        img.src = datas;

    })
}// Use it like : var newDataURI = await resizedataURL('yourDataURIHere', 50, 50);

//var newDataURI = resizedataURL('input.png', 50, 50).then((res) => console.log(res));

function txt_param_changed(obj) {

    //console.log(obj)
    //console.log(selected_elem)

    switch(obj.id) {
        case 'txt_text':
            selected_elem.text = obj.value
            break
        case 'txt_text_font':
            selected_elem.fontFamily = obj.value
            break
        case 'txt_text_size':
            int_val = Number(obj.value)
            selected_elem.fontSize = int_val
            break
        case 'txt_bold':
            if (obj.checked) selected_elem.fontWeight = 'bold'
            else selected_elem.fontWeight = 'normal'
            break
        case 'txt_line_height':
            float_val = parseFloat(obj.value)
            selected_elem.lineHeight = float_val
            break
    }
    selected_elem.dirty = true
    canvas.renderAll();
}