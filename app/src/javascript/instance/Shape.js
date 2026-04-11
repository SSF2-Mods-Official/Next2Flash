/**
 * ベクターデータを管理するクラス、Next2DのShapeクラスとして出力されます。
 * The output is as a Next2D Shape class, a class that manages vector data.
 *
 * @class
 * @extends {Instance}
 * @memberOf instance
 */
class Shape extends Instance
{
    /**
     * @param {object} object
     * @constructor
     * @public
     */
    constructor (object = null)
    {
        super(object);

        this._$bitmapId = 0;
        this._$bounds   = null;
        this._$grid     = null;
        this._$inBitmap = false;
        this._$recodes  = [];

        if (object.inBitmap) {
            this.inBitmap = object.inBitmap;
        }

        if (object.recodes) {
            this.recodes = object.recodes;
        }

        if (object.bounds) {
            this.bounds = object.bounds;
        }

        if (object.bitmapId) {
            this.bitmapId = object.bitmapId;
        }

        if (object.grid) {
            this.grid = object.grid;
        }

        this._$graphicBuffer = null;
        this._$bufferVersion = -1;
    }

    /**
     * @description Shapeクラスを複製
     *              Duplicate Shape class
     *
     * @return {MovieClip}
     * @method
     * @public
     */
    clone ()
    {
        return new Shape(JSON.parse(JSON.stringify(this.toObject())));
    }

    /**
     * @description このアイテムが設定されたDisplayObjectが選択された時
     *              内部情報をコントローラーに表示する
     *              When a DisplayObject with this item set is selected,
     *              internal information is displayed on the controller.
     *
     * @param  {object} place
     * @param  {string} [name=""]
     * @return {void}
     * @method
     * @public
     */
    showController(place, name = "")
    {
        super.showController(place, name);

        // 9スライスの値を初期化
        document
            .getElementById("nine-slice-setting-x")
            .value = "0";

        document
            .getElementById("nine-slice-setting-y")
            .value = "0";

        document
            .getElementById("nine-slice-setting-w")
            .value = "0";

        document
            .getElementById("nine-slice-setting-h")
            .value = "0";

        // Shapeに必要なコントローラーを表示する
        Util.$controller.showObjectSetting([
            "nine-slice-setting"
        ]);

        // Shapeに不要なコントローラーを非表示にする
        Util.$controller.hideObjectSetting([
            "text-setting",
            "loop-setting",
            "video-setting",
            "fill-color-setting"
        ]);
    }

    /**
     * @description タップした範囲のShapeのカラーをコントローラーに表示
     *              Display the color of the shape in the tapped area on the controller
     *
     * @param {object} place
     * @param {MouseEvent} event
     * @method
     * @public
     */
    showShapeColor (place, event)
    {
        // マウスのタッチポイントがShapeの描画範囲か判定する
        this.setHitColor(event.offsetX, event.offsetY, place.matrix);

        // 9スライスの設定があれば値をセット
        const grid = this._$grid;
        if (grid && grid.x && grid.y) {

            document
                .getElementById("nine-slice-setting-x")
                .value = `${grid.x}`;

            document
                .getElementById("nine-slice-setting-y")
                .value = `${grid.y}`;

            document
                .getElementById("nine-slice-setting-w")
                .value = `${grid.w}`;

            document
                .getElementById("nine-slice-setting-h")
                .value = `${grid.h}`;

            Util
                .$gridController
                .show()
                .relocation();
        }

        // マウスポイントがShapeの描画範囲にヒットしていれば
        // 必要なコントローラーを表示して値をセットする
        if (Util.$hitColor) {
            Util.$controller.showObjectSetting([
                "fill-color-setting",
                "nine-slice-setting"
            ]);
        }
    }

    /**
     * @description 表示領域(バウンディングボックス)のObjectを返す
     *              Returns the Object of the display area (bounding box)
     *
     * @param  {array} [matrix=null]
     * @return {object}
     * @method
     * @public
     */
    getBounds (matrix = null)
    {
        return matrix
            ? Util.$boundsMatrix(this._$bounds, matrix)
            : this._$bounds;
    }

    /**
     * @description SWFのShapeで画像が使われているかの判定
     *              Determining if an image is used in a SWF Shape
     *
     * @member {boolean}
     * @default false
     * @public
     */
    get inBitmap ()
    {
        return this._$inBitmap;
    }
    set inBitmap (in_bitmap)
    {
        this._$inBitmap = !!in_bitmap;
    }

    /**
     * @description Shapeの幅を返す
     *              Return image width
     *
     * @member {number}
     * @readonly
     * @public
     */
    get width ()
    {
        return Math.abs(this._$bounds.xMax - this._$bounds.xMin);
    }

    /**
     * @description Shapeの高さを返す
     *              Return image width
     *
     * @member {number}
     * @readonly
     * @public
     */
    get height ()
    {
        return Math.abs(this._$bounds.yMax - this._$bounds.yMin);
    }

    /**
     * @description シンボルを指定した時の継承先を返す
     *              Returns the inheritance destination when a symbol is specified.
     *
     * @member   {string}
     * @readonly
     * @public
     */
    get defaultSymbol ()
    {
        return window.next2d.display.Shape.namespace;
    }

    /**
     * @description Shapeの描画のポイント情報を配列で返す
     *              Returns an array of shape drawing point information
     *
     * @member {array}
     * @public
     */
    get recodes ()
    {
        if (!this._$inBitmap) {
            return this._$recodes;
        }

        const recodes = [];
        const { BitmapData } = window.next2d.display;
        for (let idx = 0; this._$recodes.length > idx; ++idx) {

            const value = this._$recodes[idx];
            recodes[idx] = value;

            if (typeof value !== "object") {
                continue;
            }

            if (value.namespace !== BitmapData.namespace) {
                continue;
            }

            recodes[idx] = {
                "buffer": Array.from(value._$buffer),
                "width": value.width,
                "height": value.height
            };
        }

        return recodes;
    }
    set recodes (recodes)
    {
        this._$recodes = recodes;
        if (this._$inBitmap) {

            const { BitmapData } = window.next2d.display;
            for (let idx = 0; this._$recodes.length > idx; ++idx) {

                const value = this._$recodes[idx];

                if (typeof value !== "object") {
                    continue;
                }

                if (value.namespace === BitmapData.namespace) {
                    continue;
                }

                if (!value.buffer) {
                    continue;
                }

                const bitmapData = new BitmapData(
                    value.width, value.height, true, 0
                );
                bitmapData._$buffer = new Uint8Array(value.buffer);

                this._$recodes[idx] = bitmapData;
            }
        }
    }

    /**
     * @description 表示領域(バウンディングボックス)のObjectを返す
     *              Returns the Object of the display area (bounding box)
     *
     * @member {object}
     * @default null
     * @public
     */
    get bounds ()
    {
        return this._$bounds;
    }
    set bounds (bounds)
    {
        this._$bounds = bounds;
    }

    /**
     * @description 画像の色設定で画像がセットされた際の画像ID
     *              Image ID when the image is set in the image color settings
     *
     * @member {number}
     * @default 0
     * @public
     */
    get bitmapId ()
    {
        return this._$bitmapId;
    }
    set bitmapId (bitmap_id)
    {
        this._$bitmapId = bitmap_id | 0;
    }

    /**
     * @description 9sliceの4点の座標情報
     *              Coordinate information for 4 points of 9slice
     *
     * @member {object}
     * @default null
     * @public
     */
    get grid ()
    {
        return this._$grid;
    }
    set grid (grid)
    {
        this._$grid = grid;
    }

    /**
     * @description 描画パスのxyポインターを生成
     *              Generate xy pointer for drawing path
     *
     * @param  {number} layer_id
     * @param  {number} character_id
     * @return {void}
     * @method
     * @public
     */
    createPointer (layer_id, character_id)
    {
        const { Graphics } = window.next2d.display;

        Util.$clearShapePointer();

        const element = document.getElementById("stage-area");

        let syncId = 2;

        let movePointer = null;
        for (let idx = 0; idx < this._$recodes.length; ) {

            switch (this._$recodes[idx++]) {

                case Graphics.MOVE_TO:
                    syncId = idx;
                    movePointer = {
                        "idx": idx,
                        "x": this._$recodes[idx++],
                        "y": this._$recodes[idx++]
                    };
                    break;

                case Graphics.LINE_TO:

                    this.addPointer(
                        layer_id,
                        character_id,
                        idx,
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        Graphics.LINE_TO
                    );

                    this._$adjustmentPointer(idx, syncId);

                    break;

                case Graphics.CUBIC:

                    for (let jdx = 0; 2 > jdx; ++jdx) {
                        this.addPointer(
                            layer_id,
                            character_id,
                            idx,
                            this._$recodes[idx++],
                            this._$recodes[idx++],
                            Graphics.CUBIC,
                            true
                        );
                    }

                    this.addPointer(
                        layer_id,
                        character_id,
                        idx,
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        Graphics.CUBIC,
                        false
                    );

                    this._$adjustmentPointer(idx, syncId);

                    break;

                case Graphics.CURVE_TO:

                    this.addPointer(
                        layer_id,
                        character_id,
                        idx,
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        Graphics.CURVE_TO,
                        true
                    );

                    this.addPointer(
                        layer_id,
                        character_id,
                        idx,
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        Graphics.CURVE_TO
                    );

                    this._$adjustmentPointer(idx, syncId);

                    break;

                case Graphics.FILL_STYLE:
                    idx += 4;
                    break;

                case Graphics.STROKE_STYLE:
                    if (movePointer) {
                        this.addPointer(
                            layer_id,
                            character_id,
                            movePointer.idx,
                            movePointer.x,
                            movePointer.y,
                            Graphics.MOVE_TO
                        );
                        movePointer = null;
                    }
                    idx += 8;
                    break;

                case Graphics.GRADIENT_FILL:
                    idx += 6;
                    break;

                case Graphics.GRADIENT_STROKE:
                    idx += 10;
                    break;

                case Graphics.BEGIN_PATH:
                case Graphics.END_FILL:
                case Graphics.END_STROKE:
                    break;

                default:
                    break;

            }

        }

        Util.$addModalEvent(element);
    }

    /**
     * @description 始点と終点が重なるポインターは調整
     *              Pointers where the start and end points overlap are adjusted
     *
     * @param  {number} index
     * @param  {number} sync_id
     * @return {void}
     * @method
     * @private
     */
    _$adjustmentPointer (index, sync_id)
    {
        const { Graphics } = window.next2d.display;
        switch (this._$recodes[index]) {

            case Graphics.MOVE_TO:
            case Graphics.FILL_STYLE:
            case Graphics.GRADIENT_FILL:
                {
                    const children = document
                        .getElementById("stage-area")
                        .children;

                    const node = children[children.length - 1];
                    node.dataset.syncId = `${sync_id}`;
                }
                break;

            default:
                break;

        }
    }

    /**
     * @description 指定のxy座標にパスのelementを追加
     *              Add a path element at the specified xy-coordinates
     *
     * @param  {number}  layer_id
     * @param  {number}  character_id
     * @param  {number}  index
     * @param  {number}  x
     * @param  {number}  y
     * @param  {number}  type
     * @param  {boolean} [curve=false]
     * @return {void}
     * @method
     * @public
     */
    addPointer (
        layer_id, character_id, index, x, y, type, curve = false
    ) {
        const layer = Util
            .$currentWorkSpace()
            .scene
            .getLayer(layer_id);

        const character = layer.getCharacter(character_id);

        const stageArea = document
            .getElementById("stage-area");

        const div = document.createElement("div");

        div.classList.add("transform");

        // dataset
        div.dataset.shapePointer = "true";
        div.dataset.layerId      = `${layer_id}`;
        div.dataset.characterId  = `${character_id}`;
        div.dataset.index        = `${index}`;
        div.dataset.libraryId    = `${this.id}`;
        div.dataset.curve        = `${curve}`;
        div.dataset.type         = `${type}`;
        div.dataset.position     = `${stageArea.children.length}`;

        let matrix = [1, 0, 0, 1, 0, 0];
        if (character) {
            const frame = Util.$timelineFrame.currentFrame;
            matrix = character.getPlace(frame).matrix;
            if (Util.$sceneChange.matrix.length) {
                matrix = Util.$multiplicationMatrix(
                    Util.$sceneChange.concatenatedMatrix,
                    matrix
                );
            }
        }

        // css
        const tx = x * matrix[0] + y * matrix[2] + matrix[4];
        const ty = x * matrix[1] + y * matrix[3] + matrix[5];

        div.style.left = `${tx * Util.$zoomScale + Util.$offsetLeft - 3}px`;
        div.style.top  = `${ty * Util.$zoomScale + Util.$offsetTop  - 3}px`;

        if (curve) {
            div.style.borderRadius = "5px";
        } else {
            div.dataset.detail = "{{ダブルクリックでカーブポイントが追加されます}}";
        }

        div.addEventListener("mousedown", (event) =>
        {
            if (event.button) {
                return ;
            }

            // 親のイベントを中止する
            event.stopPropagation();

            const activeTool = Util.$tools.activeTool;
            if (activeTool) {
                event.shapePointer = true;
                activeTool.dispatchEvent(
                    EventType.MOUSE_DOWN,
                    event
                );
            }
        });

        div.addEventListener("dblclick", (event) =>
        {
            // 親のイベントを中止する
            event.stopPropagation();

            const activeTool = Util.$tools.activeTool;
            if (activeTool) {
                event.shapePointer = true;
                activeTool.dispatchEvent(
                    EventType.DBL_CLICK,
                    event
                );
            }
        });

        stageArea.appendChild(div);
    }

    /**
     * @description リサイズやパスの座標変更時にバウンディングボックスの座標を再計算
     *              Recalculate bounding box coordinates when resizing or changing path coordinates
     *
     * @return {object}
     * @method
     * @public
     */
    reloadBounds ()
    {
        const { Graphics, Shape } = window.next2d.display;
        const shape = new Shape();

        const graphics = shape.graphics;

        const types = [];
        for (let idx = 0; idx < this._$recodes.length; ) {
            switch (this._$recodes[idx++]) {

                case Graphics.MOVE_TO:
                case Graphics.LINE_TO:
                    idx += 2;
                    break;

                case Graphics.CURVE_TO:
                    idx += 4;
                    break;

                case Graphics.CUBIC:
                    idx += 6;
                    break;

                case Graphics.FILL_STYLE:
                    types.push("fill");
                    idx += 4;
                    break;

                case Graphics.STROKE_STYLE:
                    types.push(idx + 1);
                    idx += 8;
                    break;

                case Graphics.GRADIENT_FILL:
                    types.push("fill");
                    idx += 6;
                    break;

                case Graphics.GRADIENT_STROKE:
                    types.push(idx + 1);
                    idx += 10;
                    break;

                case Graphics.BEGIN_PATH:
                case Graphics.END_FILL:
                case Graphics.END_STROKE:
                    break;

            }
        }

        for (let idx = 0; idx < this._$recodes.length; ) {

            switch (this._$recodes[idx++]) {

                case Graphics.MOVE_TO:
                    graphics.moveTo(
                        this._$recodes[idx++],
                        this._$recodes[idx++]
                    );
                    break;

                case Graphics.LINE_TO:
                    graphics.lineTo(
                        this._$recodes[idx++],
                        this._$recodes[idx++]
                    );
                    break;

                case Graphics.CUBIC:
                    graphics.cubicCurveTo(
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        this._$recodes[idx++]
                    );
                    break;

                case Graphics.CURVE_TO:
                    graphics.curveTo(
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        this._$recodes[idx++],
                        this._$recodes[idx++]
                    );
                    break;

                case Graphics.FILL_STYLE:
                    idx += 4;
                    break;

                case Graphics.STROKE_STYLE:
                    idx += 8;
                    break;

                case Graphics.GRADIENT_FILL:
                    {
                        const { Matrix } = window.next2d.geom;
                        const matrix = new Matrix();
                        const xScale = this.width  / 2 / 819.2;
                        const yScale = this.height / 2 / 819.2;
                        matrix.scale(xScale, yScale);
                        matrix.translate(
                            this.width  / 2 + graphics._$xMin,
                            this.height / 2 + graphics._$yMin
                        );

                        this._$recodes[idx + 2] = Array.from(matrix._$matrix);
                        idx += 6;
                    }
                    break;

                case Graphics.GRADIENT_STROKE:
                    {
                        const { Matrix } = window.next2d.geom;
                        const matrix = new Matrix();
                        const xScale = this.width  / 2 / 819.2;
                        const yScale = this.height / 2 / 819.2;
                        matrix.scale(xScale, yScale);
                        matrix.translate(
                            this.width  / 2 + graphics._$xMin,
                            this.height / 2 + graphics._$yMin
                        );

                        this._$recodes[idx + 6] = Array.from(matrix._$matrix);
                        idx += 10;
                    }
                    break;

                case Graphics.BEGIN_PATH:
                    {
                        const type = types.shift();
                        if (type === "fill") {
                            graphics.beginFill();
                        } else {
                            graphics.lineStyle(type);
                        }
                    }
                    break;

                case Graphics.END_FILL:
                    graphics.endFill();
                    break;

                case Graphics.END_STROKE:
                    graphics.endLine();
                    break;

                default:
                    break;

            }

        }

        return {
            "xMin": graphics._$xMin,
            "xMax": graphics._$xMax,
            "yMin": graphics._$yMin,
            "yMax": graphics._$yMax
        };
    }

    /**
     * @description 引数のShapeオブジェクトにこのオブジェクトのパス情報をコピーする
     *              Copy the path information of this object to the argument Shape object
     *
     * @param  {Shape} shape
     * @return {Shape}
     * @method
     * @public
     */
    copyFrom (shape)
    {
        shape._$recodes  = this._$recodes.slice();
        shape._$bounds   = {
            "xMin": this._$bounds.xMin,
            "xMax": this._$bounds.xMax,
            "yMin": this._$bounds.yMin,
            "yMax": this._$bounds.yMax
        };
        shape._$bitmapId = this._$bitmapId;

        return shape;
    }

    /**
     * @description クラス内の変数をObjectにして返す
     *              Return variables in a class as Objects
     *
     * @return {object}
     * @method
     * @public
     */
    toObject ()
    {
        return {
            "id":       this.id,
            "name":     this.name,
            "type":     this.type,
            "symbol":   this.symbol,
            "folderId": this.folderId,
            "bitmapId": this.bitmapId,
            "grid":     this.grid,
            "inBitmap": this.inBitmap,
            "recodes":  this.recodes,
            "bounds":   this.bounds
        };
    }

    /**
     * @description 書き出し用のObjectを返す
     *              Returns an Object for export
     *
     * @return {object}
     * @method
     * @public
     */
    toPublish ()
    {
        if (this._$bitmapId) {
            Util.$useIds.set(this._$bitmapId, true);
        }

        return {
            "symbol":   this.symbol,
            "extends":  this.defaultSymbol,
            "bitmapId": this.bitmapId,
            "grid":     this.grid,
            "inBitmap": this.inBitmap,
            "recodes":  this.recodes,
            "bounds": {
                "xMin": this._$bounds.xMin,
                "xMax": this._$bounds.xMax,
                "yMin": this._$bounds.yMin,
                "yMax": this._$bounds.yMax
            }
        };
    }

    /**
     * @description Shapeの色設定の変更関数
     *              Function to change the color settings of a Shape
     *
     * @param  {string} style
     * @return {void}
     * @method
     * @public
     */
    changeStyle (style)
    {
        const { Graphics } = window.next2d.display;

        const index = Util.$hitColor.index;
        const currentStyle = Util.$hitColor.style;
        switch (currentStyle) {

            case Graphics.BITMAP_FILL:
            case Graphics.FILL_STYLE:
                {
                    const element = document
                        .getElementById("fill-color-type-select");

                    switch (element.value) {

                        case "linear":
                        case "radial":
                            {
                                const colorValue = document
                                    .getElementById("fill-color-value")
                                    .value;

                                const color = Util.$intToRGB(
                                    `0x${colorValue.slice(1)}` | 0
                                );

                                const alpha = (document
                                    .getElementById("fill-alpha-value")
                                    .value | 0) / 100 * 255;

                                this.changeGradient(
                                    index, style, Graphics.GRADIENT_FILL,
                                    6, color, alpha
                                );
                            }
                            break;

                        default:
                            break;

                    }
                }
                break;

            case Graphics.GRADIENT_FILL:
                {
                    const element = document
                        .getElementById("fill-color-type-select");

                    const stops = this._$recodes[index + 1];
                    const color = stops.pop();
                    switch (element.value) {

                        case "bitmap":
                        case "rgba":
                            this._$recodes.splice(index - 1, 12,
                                Graphics.FILL_STYLE,
                                color.R, color.G,
                                color.B, color.A,
                                Graphics.END_FILL
                            );

                            Util.$hitColor = {
                                "index": index,
                                "style": Graphics.FILL_STYLE,
                                "shape": this
                            };
                            break;

                        default:
                            this.changeGradient(
                                index, style, Graphics.GRADIENT_FILL,
                                12, color, color.A
                            );
                            break;

                    }
                }
                break;

            case Graphics.STROKE_STYLE:
                {
                    const element = document
                        .getElementById("fill-color-type-select");

                    switch (element.value) {

                        case "linear":
                        case "radial":
                            {
                                const colorValue = document
                                    .getElementById("fill-color-value")
                                    .value;

                                const color = Util.$intToRGB(
                                    `0x${colorValue.slice(1)}` | 0
                                );

                                const alpha = (document
                                    .getElementById("fill-alpha-value")
                                    .value | 0) / 100 * 255;

                                this.changeGradient(
                                    index, style, Graphics.GRADIENT_STROKE,
                                    5, color, alpha
                                );
                            }
                            break;

                        default:
                            break;

                    }
                }
                break;

            case Graphics.GRADIENT_STROKE:
                {
                    const element = document
                        .getElementById("fill-color-type-select");

                    const stops      = this._$recodes[index + 5];
                    const color      = stops.pop();
                    const width      = this._$recodes[index];
                    const caps       = this._$recodes[index + 1];
                    const joints     = this._$recodes[index + 2];
                    const miterLimit = this._$recodes[index + 3];
                    switch (element.value) {

                        case "bitmap":
                        case "rgba":
                            this._$recodes.splice(index - 1, 11,
                                Graphics.STROKE_STYLE,
                                width, caps,
                                joints, miterLimit,
                                color.R, color.G,
                                color.B, color.A,
                                Graphics.END_STROKE
                            );

                            Util.$hitColor = {
                                "index": index,
                                "width": width,
                                "style": Graphics.STROKE_STYLE,
                                "shape": this
                            };
                            break;

                        default:
                            this.changeGradient(
                                index, style, Graphics.GRADIENT_STROKE,
                                6, color, color.A
                            );
                            break;

                    }
                }
                break;

        }

        this.cacheClear();

        const frame = Util.$timelineFrame.currentFrame;

        Util.$currentWorkSpace().scene.changeFrame(frame);
    }

    /**
     * @description 色設定をグラデーションへ変更
     *              Change color setting to gradient
     *
     * @param  {number} index
     * @param  {string} style
     * @param  {number} graphics_type
     * @param  {number} delete_number
     * @param  {object} color
     * @param  {number} alpha
     * @return {void}
     * @method
     * @public
     */
    changeGradient (index, style, graphics_type, delete_number, color, alpha)
    {
        const { Graphics } = window.next2d.display;
        const { Matrix } = window.next2d.geom;

        const matrix = new Matrix();
        const xScale = this.width  / 2 / 819.2;
        const yScale = this.height / 2 / 819.2;
        matrix.scale(xScale, yScale);
        matrix.translate(
            this.width  / 2 + this._$bounds.xMin,
            this.height / 2 + this._$bounds.yMin
        );

        const ratios = [{
            "ratio": 0,
            "R": 255,
            "G": 255,
            "B": 255,
            "A": 255
        }, {
            "ratio": 1,
            "R": color.R,
            "G": color.G,
            "B": color.B,
            "A": alpha
        }];

        Util.$hitColor = {
            "index"  : index,
            "style"  : graphics_type,
            "type"   : style,
            "ratios" : ratios,
            "shape"  : this
        };

        if (Graphics.GRADIENT_STROKE === graphics_type) {

            this._$recodes[index - 1] = Graphics.GRADIENT_STROKE;

            this._$recodes.splice(index + 4, delete_number,
                style, ratios,
                Array.from(matrix._$matrix),
                "pad",
                "rgb",
                0
            );

            Util.$hitColor.width = this._$recodes[index];

        } else {

            this._$recodes.splice(index - 1, delete_number,
                graphics_type, style, ratios,
                Array.from(matrix._$matrix),
                "pad",
                "rgb",
                0
            );

        }

        Util
            .$shapeController
            .initializeGradient();

    }

    /**
     * @description 色情報を更新
     *              Update color information
     *
     * @param  {number} [color_index=-1]
     * @return {void}
     * @method
     * @public
     */
    changeColor (color_index = -1)
    {
        const { Graphics } = window.next2d.display;

        const index = Util.$hitColor.index;
        switch (Util.$hitColor.style) {

            case Graphics.BITMAP_FILL:
                break;

            case Graphics.BITMAP_STROKE:
                {
                    const width = Util.$clamp(document
                        .getElementById("fill-stroke-width-value")
                        .value | 0, 1, 255);

                    if (this._$recodes[index] !== width) {

                        Util.$hitColor.width  = width;
                        this._$recodes[index] = width;

                        const bounds = this.reloadBounds(width);
                        this._$bounds.xMin = bounds.xMin;
                        this._$bounds.xMax = bounds.xMax;
                        this._$bounds.yMin = bounds.yMin;
                        this._$bounds.yMax = bounds.yMax;

                        this.cacheClear();
                    }
                }
                break;

            case Graphics.FILL_STYLE:
                {
                    const colorValue = document
                        .getElementById("fill-color-value")
                        .value;

                    const color = Util.$intToRGB(
                        `0x${colorValue.slice(1)}` | 0
                    );

                    this._$recodes[index    ] = color.R;
                    this._$recodes[index + 1] = color.G;
                    this._$recodes[index + 2] = color.B;
                    this._$recodes[index + 3] = Util.$clamp((document
                        .getElementById("fill-alpha-value")
                        .value | 0) / 100 * 255, 0, 255);
                }
                break;

            case Graphics.GRADIENT_FILL:
                {
                    const colors = this._$recodes[index + 1];

                    const colorIndex = color_index > -1
                        ? color_index
                        : colors.length - 1;

                    const object = colors[colorIndex];

                    const colorValue = document
                        .getElementById("fill-color-value")
                        .value;

                    const color = Util.$intToRGB(
                        `0x${colorValue.slice(1)}` | 0
                    );

                    object.R = color.R;
                    object.G = color.G;
                    object.B = color.B;
                    object.A = Util.$clamp((document
                        .getElementById("fill-alpha-value")
                        .value | 0) / 100 * 255, 0, 255);
                }

                break;

            case Graphics.STROKE_STYLE:
                {
                    const colorValue = document
                        .getElementById("fill-color-value")
                        .value;

                    const color = Util.$intToRGB(
                        `0x${colorValue.slice(1)}` | 0
                    );

                    this._$recodes[index + 4] = color.R;
                    this._$recodes[index + 5] = color.G;
                    this._$recodes[index + 6] = color.B;
                    this._$recodes[index + 7] = Util.$clamp((document
                        .getElementById("fill-alpha-value")
                        .value | 0) / 100 * 255, 0, 255);

                    const width = Util.$clamp(document
                        .getElementById("fill-stroke-width-value")
                        .value | 0, 1, 255);

                    if (this._$recodes[index] !== width) {

                        Util.$hitColor.width  = width;
                        this._$recodes[index] = width;

                        const bounds = this.reloadBounds(width);
                        this._$bounds.xMin = bounds.xMin;
                        this._$bounds.xMax = bounds.xMax;
                        this._$bounds.yMin = bounds.yMin;
                        this._$bounds.yMax = bounds.yMax;

                        this.cacheClear();
                    }

                }
                break;

            case Graphics.GRADIENT_STROKE:
                {
                    const colors = this._$recodes[index + 5];

                    const colorIndex = color_index > -1
                        ? color_index
                        : colors.length - 1;

                    const object = colors[colorIndex];

                    const colorValue = document
                        .getElementById("fill-color-value")
                        .value;

                    const color = Util.$intToRGB(
                        `0x${colorValue.slice(1)}` | 0
                    );

                    object.R = color.R;
                    object.G = color.G;
                    object.B = color.B;
                    object.A = Util.$clamp((document
                        .getElementById("fill-alpha-value")
                        .value | 0) / 100 * 255, 0, 255);

                    const width = Util.$clamp(document
                        .getElementById("fill-stroke-width-value")
                        .value | 0, 1, 255);

                    if (this._$recodes[index] !== width) {

                        Util.$hitColor.width  = width;
                        this._$recodes[index] = width;

                        const bounds = this.reloadBounds(width);
                        this._$bounds.xMin = bounds.xMin;
                        this._$bounds.xMax = bounds.xMax;
                        this._$bounds.yMin = bounds.yMin;
                        this._$bounds.yMax = bounds.yMax;

                        this.cacheClear();
                    }
                }
                break;

        }

        this.cacheClear();
    }

    /**
     * @description このオブジェクトが設置されてる全てのDisplayObjectのキャッシュを削除
     *              Delete the cache of all DisplayObjects where this object is located
     *
     * @return {void}
     * @method
     * @public
     */
    cacheClear ()
    {
        const scene =  Util.$currentWorkSpace().scene;
        for (const layer of scene._$layers.values()) {

            const length = layer._$characters.length;
            for (let idx = 0; idx < length; ++idx) {

                const character = layer._$characters[idx];

                if (character.libraryId !== this.id) {
                    continue;
                }

                character.dispose();
            }
        }

        this._$graphicBuffer = null;
    }

    /**
     * @description マウスダウンしたxy座標にShapeの色があれば、ヒットした色をコントローラーに表示する
     *              If there is a Shape color at the xy-coordinates of the mouse down, display the hit color on the controller.
     *
     * @param  {number} x
     * @param  {number} y
     * @param  {array} place_matrix
     * @return {void}
     * @method
     * @public
     */
    setHitColor (x, y, place_matrix)
    {
        if (!this._$recodes.length) {
            return ;
        }

        const { Graphics } = window.next2d.display;
        const { Point, Matrix } = window.next2d.geom;

        const matrix = new Matrix();

        const xScale = Math.sqrt(
            place_matrix[0] * place_matrix[0]
            + place_matrix[1] * place_matrix[1]
        ) * Util.$zoomScale;

        const yScale = Math.sqrt(
            place_matrix[2] * place_matrix[2]
            + place_matrix[3] * place_matrix[3]
        ) * Util.$zoomScale;
        matrix.scale(xScale, yScale);

        const radian = Math.atan2(place_matrix[1], place_matrix[0]);
        if (radian) {
            matrix.translate(-this.width / 2, -this.height / 2);
            matrix.rotate(radian);
            matrix.translate(this.width / 2, this.height / 2);
        }

        const topLeft     = matrix.transformPoint(new Point(0, 0));
        const topRight    = matrix.transformPoint(new Point(this.width, 0));
        const bottomLeft  = matrix.transformPoint(new Point(0, this.height));
        const bottomRight = matrix.transformPoint(new Point(this.width, this.height));

        const left = Math.min(topLeft.x, topRight.x, bottomLeft.x, bottomRight.x);
        const top  = Math.min(topLeft.y, topRight.y, bottomLeft.y, bottomRight.y);
        matrix.translate(-left, -top);

        // reset
        Util.$hitColor = null;

        Util.$hitContext.lineWidth = 0;
        Util.$hitContext.beginPath();
        Util.$hitContext.setTransform(
            matrix._$matrix[0], matrix._$matrix[1],
            matrix._$matrix[2], matrix._$matrix[3],
            -this._$bounds.xMin * xScale + matrix._$matrix[4],
            -this._$bounds.yMin * yScale + matrix._$matrix[5]
        );

        const recode = this._$recodes;
        const length  = recode.length;
        for (let idx = 0; idx < length; ) {
            switch (recode[idx++]) {

                case Graphics.BEGIN_PATH:
                    Util.$hitContext.beginPath();
                    break;

                case Graphics.MOVE_TO:
                    Util.$hitContext.moveTo(recode[idx++], recode[idx++]);
                    break;

                case Graphics.LINE_TO:
                    Util.$hitContext.lineTo(recode[idx++], recode[idx++]);
                    break;

                case Graphics.CURVE_TO:
                    Util.$hitContext.quadraticCurveTo(
                        recode[idx++], recode[idx++],
                        recode[idx++], recode[idx++]
                    );
                    break;

                case Graphics.CUBIC:
                    Util.$hitContext.bezierCurveTo(
                        recode[idx++], recode[idx++],
                        recode[idx++], recode[idx++],
                        recode[idx++], recode[idx++]
                    );
                    break;

                case Graphics.FILL_STYLE:
                    if (Util.$hitContext.isPointInPath(x, y)) {
                        if (this._$bitmapId) {

                            Util.$hitColor = {
                                "index": idx,
                                "style": Graphics.BITMAP_FILL,
                                "shape": this
                            };

                            document
                                .getElementById("fill-color-type-select")[1]
                                .selected = true;

                        } else {

                            Util.$hitColor = {
                                "index": idx,
                                "style": Graphics.FILL_STYLE,
                                "shape": this
                            };

                            const R = recode[idx    ].toString(16).padStart(2, "0");
                            const G = recode[idx + 1].toString(16).padStart(2, "0");
                            const B = recode[idx + 2].toString(16).padStart(2, "0");

                            document
                                .getElementById("fill-color-type-select")[0]
                                .selected = true;

                            document
                                .getElementById("fill-color-value")
                                .value = `#${R}${G}${B}`;

                            document
                                .getElementById("fill-alpha-value")
                                .value = `${recode[idx + 3] / 255 * 100}`;

                        }

                        Util
                            .$shapeController
                            .changeFillColorTypeSelect();

                    }
                    idx += 4;
                    break;

                case Graphics.GRADIENT_FILL:
                    if (Util.$hitContext.isPointInPath(x, y)) {

                        document
                            .getElementById("fill-color-type-select")[
                                recode[idx] === "linear" ? 2 : 3
                            ]
                            .selected = true;

                        Util.$hitColor = {
                            "index"  : idx,
                            "style"  : Graphics.GRADIENT_FILL,
                            "type"   : recode[idx],
                            "ratios" : recode[idx + 1],
                            "shape"  : this
                        };

                        Util
                            .$shapeController
                            .changeFillColorTypeSelect();

                    }
                    idx += 6;
                    break;

                case Graphics.STROKE_STYLE:
                    Util.$hitContext.lineWidth = recode[idx] | 0;
                    if (Util.$hitContext.isPointInStroke(x, y)) {

                        if (this._$bitmapId) {

                            Util.$hitColor = {
                                "index": idx,
                                "width": Util.$hitContext.lineWidth,
                                "style": Graphics.BITMAP_STROKE,
                                "shape": this
                            };

                            document
                                .getElementById("fill-color-type-select")[1]
                                .selected = true;

                        } else {

                            Util.$hitColor = {
                                "index": idx,
                                "width": Util.$hitContext.lineWidth,
                                "style": Graphics.STROKE_STYLE,
                                "shape": this
                            };

                            const R = recode[idx + 4].toString(16).padStart(2, "0");
                            const G = recode[idx + 5].toString(16).padStart(2, "0");
                            const B = recode[idx + 6].toString(16).padStart(2, "0");

                            document
                                .getElementById("fill-color-type-select")[0]
                                .selected = true;

                            document
                                .getElementById("fill-color-value")
                                .value = `#${R}${G}${B}`;

                            document
                                .getElementById("fill-alpha-value")
                                .value = `${recode[idx + 7] / 255 * 100}`;
                        }

                        document
                            .getElementById("fill-stroke-width-value")
                            .value = `${Util.$hitContext.lineWidth}`;

                        Util
                            .$shapeController
                            .changeFillColorTypeSelect();

                    }
                    idx += 8;
                    break;

                case Graphics.GRADIENT_STROKE:
                    Util.$hitContext.lineWidth = recode[idx];
                    if (Util.$hitContext.isPointInStroke(x, y)) {

                        document
                            .getElementById("fill-color-type-select")[
                                recode[idx + 4] === "linear" ? 2 : 3
                            ]
                            .selected = true;

                        Util.$hitColor = {
                            "index"  : idx,
                            "width"  : recode[idx],
                            "style"  : Graphics.GRADIENT_STROKE,
                            "type"   : recode[idx + 4],
                            "ratios" : recode[idx + 5],
                            "shape"  : this
                        };

                        Util
                            .$shapeController
                            .changeFillColorTypeSelect();

                    }
                    idx += 10;
                    break;

                case Graphics.CLOSE_PATH:
                case Graphics.END_STROKE:
                case Graphics.END_FILL:
                    break;

                default:
                    break;

            }
        }
    }

    /**
     * @description Patch Graphics._$getRecodes to use segment-based
     *              Float32Array construction with _$buffer-first checks
     *              for bitmap pixel data.
     * @static
     * @private
     */
    static _patchFastGetRecodes ()
    {
        const G = window.next2d.display.Graphics;
        if (!G || G.prototype._$n2fFastRecodes) return;
        G.prototype._$n2fFastRecodes = true;

        /**
         * Resolve bitmap pixel data, preferring _$buffer over canvas/image.
         * @param {object} bmd - BitmapData instance
         * @returns {Uint8Array|Uint8ClampedArray|null}
         */
        function _getBitmapPixels (bmd)
        {
            // FAST PATH: use raw buffer directly (avoids canvas getImageData)
            if (bmd._$buffer) return bmd._$buffer;
            if (null !== bmd.image || null !== bmd.canvas) {
                const c = document.createElement("canvas");
                c.width  = bmd.width;
                c.height = bmd.height;
                const ctx = c.getContext("2d");
                if (!ctx) return null;
                ctx.drawImage(bmd.image || bmd.canvas, 0, 0);
                return new Uint8Array(
                    ctx.getImageData(0, 0, bmd.width, bmd.height).data
                );
            }
            return null;
        }

        G.prototype._$getRecodes = function () {
            if (this._$doLine) this.endLine();
            if (this._$doFill) this.endFill();
            if (!this._$recode) this._$recode = [];

            if (!this._$buffer) {
                // Segment-based approach: build small Arrays for commands,
                // store typed-array references for pixel data, then merge
                // into a single Float32Array using native .set() calls.
                const segments = [];  // [{data: Array|TypedArray}]
                let totalLen   = 0;
                let cur        = [];  // current batch of number values
                segments.push(cur);

                const e = this._$recode;

                for (let i = 0; i < e.length;) {
                    const s = e[i++];
                    cur.push(s);

                    switch (s) {
                        case G.BEGIN_PATH:
                        case G.END_FILL:
                        case G.END_STROKE:
                        case G.CLOSE_PATH:
                            break;

                        case G.MOVE_TO:
                        case G.LINE_TO:
                            cur.push(e[i++], e[i++]);
                            break;

                        case G.CURVE_TO:
                        case G.FILL_STYLE:
                            cur.push(e[i++], e[i++], e[i++], e[i++]);
                            break;

                        case G.CUBIC:
                            cur.push(e[i++], e[i++], e[i++], e[i++], e[i++], e[i++]);
                            break;

                        case G.STROKE_STYLE: {
                            cur.push(e[i++]); // lineWidth
                            const caps = e[i++];
                            cur.push(caps === "none" ? 0 : caps === "round" ? 1 : 2);
                            const joints = e[i++];
                            cur.push(joints === "bevel" ? 0 : joints === "miter" ? 1 : 2);
                            cur.push(e[i++], e[i++], e[i++], e[i++], e[i++]);
                            break;
                        }

                        case G.ARC:
                            cur.push(e[i++], e[i++], e[i++]);
                            break;

                        case G.GRADIENT_FILL: {
                            const type = e[i++];
                            const stops = e[i++];
                            const mx = e[i++];
                            const spread = e[i++];
                            const interp = e[i++];
                            const focal = e[i++];
                            cur.push(type === "linear" ? 0 : 1);
                            cur.push(stops.length);
                            for (let j = 0; j < stops.length; ++j) {
                                cur.push(stops[j].ratio, stops[j].R, stops[j].G, stops[j].B, stops[j].A);
                            }
                            cur.push(mx[0], mx[1], mx[2], mx[3], mx[4], mx[5]);
                            cur.push(spread === "reflect" ? 0 : spread === "repeat" ? 1 : 2);
                            cur.push(interp === "linearRGB" ? 0 : 1);
                            cur.push(focal);
                            break;
                        }

                        case G.GRADIENT_STROKE: {
                            cur.push(e[i++]); // lineWidth
                            const caps2 = e[i++];
                            cur.push(caps2 === "none" ? 0 : caps2 === "round" ? 1 : 2);
                            const joints2 = e[i++];
                            cur.push(joints2 === "bevel" ? 0 : joints2 === "miter" ? 1 : 2);
                            cur.push(e[i++]); // miterLimit
                            const type2 = e[i++];
                            const stops2 = e[i++];
                            const mx2 = e[i++];
                            const spread2 = e[i++];
                            const interp2 = e[i++];
                            const focal2 = e[i++];
                            cur.push(type2 === "linear" ? 0 : 1);
                            cur.push(stops2.length);
                            for (let j = 0; j < stops2.length; ++j) {
                                cur.push(stops2[j].ratio, stops2[j].R, stops2[j].G, stops2[j].B, stops2[j].A);
                            }
                            cur.push(mx2[0], mx2[1], mx2[2], mx2[3], mx2[4], mx2[5]);
                            cur.push(spread2 === "reflect" ? 0 : spread2 === "repeat" ? 1 : 2);
                            cur.push(interp2 === "linearRGB" ? 0 : 1);
                            cur.push(focal2);
                            break;
                        }

                        case G.BITMAP_FILL: {
                            const bmd = e[i++];
                            const r = _getBitmapPixels(bmd);
                            if (!r) { i += 3; break; }

                            cur.push(bmd.width, bmd.height,
                                this._$xMax - this._$xMin,
                                this._$yMax - this._$yMin,
                                r.length);

                            // End current batch, insert typed pixel data, start new batch
                            totalLen += cur.length;
                            cur = [];
                            segments.push(r);
                            totalLen += r.length;
                            segments.push(cur);

                            const mx3 = e[i++];
                            if (mx3) {
                                cur.push(mx3[0], mx3[1], mx3[2], mx3[3], mx3[4], mx3[5]);
                            } else {
                                cur.push(1, 0, 0, 1, 0, 0);
                            }
                            cur.push(e[i++] ? 1 : 0); // repeat
                            cur.push(e[i++] ? 1 : 0); // smooth
                            break;
                        }

                        case G.BITMAP_STROKE: {
                            cur.push(e[i++]); // lineWidth
                            const caps3 = e[i++];
                            cur.push(caps3 === "none" ? 0 : caps3 === "round" ? 1 : 2);
                            const joints3 = e[i++];
                            cur.push(joints3 === "bevel" ? 0 : joints3 === "miter" ? 1 : 2);
                            cur.push(e[i++]); // miterLimit
                            const bmd2 = e[i++];
                            const r2 = _getBitmapPixels(bmd2);
                            if (!r2) { i += 3; break; }

                            cur.push(bmd2.width, bmd2.height,
                                this._$xMax - this._$xMin,
                                this._$yMax - this._$yMin,
                                r2.length);

                            // End current batch, insert typed pixel data, start new batch
                            totalLen += cur.length;
                            cur = [];
                            segments.push(r2);
                            totalLen += r2.length;
                            segments.push(cur);

                            const mx4 = e[i++];
                            if (mx4) {
                                cur.push(mx4[0], mx4[1], mx4[2], mx4[3], mx4[4], mx4[5]);
                            } else {
                                cur.push(1, 0, 0, 1, 0, 0);
                            }
                            cur.push(e[i++] ? 1 : 0); // repeat
                            cur.push(e[i++] ? 1 : 0); // smooth
                            break;
                        }
                    }
                }

                // Account for the last batch
                totalLen += cur.length;

                // Merge all segments into a single Float32Array
                const f = new Float32Array(totalLen);
                let pos = 0;
                for (let si = 0; si < segments.length; si++) {
                    const seg = segments[si];
                    if (seg.length === 0) continue;
                    if (ArrayBuffer.isView(seg)) {
                        // Typed array (Uint8Array etc) — native .set()
                        f.set(seg, pos);
                    } else {
                        // Regular JS Array — copy values
                        for (let k = 0; k < seg.length; k++) f[pos + k] = seg[k];
                    }
                    pos += seg.length;
                }

                this._$buffer = f;
            }

            return this._$buffer.slice();
        };
    }

    /**
     * @description Next2DのDisplayObjectを生成
     *              Generate Next2D DisplayObject
     *
     * @return {next2d.display.Shape}
     * @method
     * @public
     */
    createInstance ()
    {
        this.constructor._patchFastGetRecodes();

        const _siPlayback = !Util.$timelinePlayer._$stopFlag;
        const _siT0 = _siPlayback ? performance.now() : 0;

        const { Shape, Graphics } = window.next2d.display;

        const shape = new Shape();
        shape._$loaderInfo  = Util.$loaderInfo;
        shape._$characterId = this.id;

        if (this._$grid) {
            const { Rectangle } = window.next2d.geom;
            shape.scale9Grid = new Rectangle(
                this._$grid.x, this._$grid.y,
                this._$grid.w, this._$grid.h
            );
        }

        const graphics = shape.graphics;

        graphics._$maxAlpha = 1;
        graphics._$canDraw  = true;
        graphics._$xMin     = this._$bounds.xMin;
        graphics._$xMax     = this._$bounds.xMax;
        graphics._$yMin     = this._$bounds.yMin;
        graphics._$yMax     = this._$bounds.yMax;

        if (this._$bitmapId) {

            const { BitmapData } = window.next2d.display;

            const instance = Util
                .$currentWorkSpace()
                .getLibrary(this._$bitmapId);

            if (instance) {

                graphics._$bitmapId = this._$bitmapId;
                graphics._$mode     = "bitmap";

                // setup
                graphics._$recode = [];

                const bitmapData = new BitmapData(
                    instance.width, instance.height, true, 0
                );
                if (instance._$buffer) {
                    bitmapData._$buffer = instance._$buffer;
                } else {
                    // Lazy stub: transparent placeholder
                    const c = document.createElement('canvas');
                    c.width = instance.width || 1;
                    c.height = instance.height || 1;
                    bitmapData.canvas = c;
                }

                // clone
                const recodes = this._$recodes;
                if (recodes[recodes.length - 1] === Graphics.END_FILL) {

                    const length  = recodes.length - 6;
                    for (let idx = 0; idx < length; ++idx) {
                        graphics._$recode.push(recodes[idx]);
                    }

                    // add Bitmap Fill
                    graphics._$recode.push(
                        Graphics.BITMAP_FILL,
                        bitmapData,
                        null,
                        "repeat",
                        false
                    );

                } else {

                    const width      = this._$recodes[recodes.length - 9];
                    const caps       = this._$recodes[recodes.length - 8];
                    const joints     = this._$recodes[recodes.length - 7];
                    const miterLimit = this._$recodes[recodes.length - 6];

                    const length  = recodes.length - 10;
                    for (let idx = 0; idx < length; ++idx) {
                        graphics._$recode.push(recodes[idx]);
                    }

                    graphics._$recode.push(
                        Graphics.BITMAP_STROKE,
                        width,
                        caps,
                        joints,
                        miterLimit,
                        bitmapData,
                        [1, 0, 0, 1, graphics._$xMin, graphics._$yMin],
                        "repeat",
                        false
                    );

                }

            } else {

                graphics._$recode = this._$recodes.slice(0);

            }

        } else {

            graphics._$recode = this._$recodes.slice(0);
            const bitmapData = graphics._$recode[graphics._$recode.length - 4];
            if (typeof bitmapData === "object"
                && bitmapData.namespace === "next2d.display.BitmapData"
            ) {
                graphics._$mode = "bitmap";
            }

        }

        const hydrationVersion = Util.$hydrationVersion | 0;
        if (this._$bufferVersion !== hydrationVersion) {
            this._$graphicBuffer = null;
        }

        if (!this._$graphicBuffer) {

            // Resolve numeric bitmap library IDs to BitmapData objects.
            // The SWF converter stores bitmap references as library IDs,
            // but the player's _$getRecodes expects BitmapData instances.
            if (this._$inBitmap && graphics._$recode) {
                const { BitmapData } = window.next2d.display;
                const recode = graphics._$recode;
                for (let idx = 0; idx < recode.length; idx++) {

                    // BITMAP_FILL pattern: [13, bmpId(number), matrix(Array), ...]
                    if (recode[idx] === Graphics.BITMAP_FILL
                        && typeof recode[idx + 1] === "number"
                        && Array.isArray(recode[idx + 2])
                    ) {
                        const libId  = recode[idx + 1];
                        const bitmap = Util
                            .$currentWorkSpace()
                            .getLibrary(libId);

                        const bd = new BitmapData(
                            bitmap && bitmap.width  || 0,
                            bitmap && bitmap.height || 0,
                            true, 0
                        );
                        if (bitmap && bitmap._$buffer) {
                            bd._$buffer = bitmap._$buffer;
                        } else {
                            const c = document.createElement('canvas');
                            c.width = (bitmap && bitmap.width) || 1;
                            c.height = (bitmap && bitmap.height) || 1;
                            bd.canvas = c;
                        }
                        recode[idx + 1] = bd;
                    }

                    // BITMAP_STROKE pattern: [14, w, cap, join, miter, bmpId(number), matrix(Array), ...]
                    if (recode[idx] === Graphics.BITMAP_STROKE
                        && typeof recode[idx + 5] === "number"
                        && Array.isArray(recode[idx + 6])
                    ) {
                        const libId  = recode[idx + 5];
                        const bitmap = Util
                            .$currentWorkSpace()
                            .getLibrary(libId);

                        const bd = new BitmapData(
                            bitmap && bitmap.width  || 0,
                            bitmap && bitmap.height || 0,
                            true, 0
                        );
                        if (bitmap && bitmap._$buffer) {
                            bd._$buffer = bitmap._$buffer;
                        } else {
                            const c = document.createElement('canvas');
                            c.width = (bitmap && bitmap.width) || 1;
                            c.height = (bitmap && bitmap.height) || 1;
                            bd.canvas = c;
                        }
                        recode[idx + 5] = bd;
                    }
                }
            }

            // Validate _$recode: log any non-BitmapData at BITMAP_FILL positions
            if (graphics._$recode) {
                const { BitmapData } = window.next2d.display;
                const rc = graphics._$recode;
                for (let vi = 0; vi < rc.length; vi++) {
                    if (rc[vi] === Graphics.BITMAP_FILL) {
                        const bd = rc[vi + 1];
                        if (bd && !(bd instanceof BitmapData)
                            && typeof bd !== "number"
                        ) {
                            console.warn(
                                `[ShapeDiag] lib=${this.id} BITMAP_FILL@${vi+1}`
                                + ` is ${typeof bd}`
                                + (bd && bd.constructor
                                    ? ` (${bd.constructor.name})`
                                    : "")
                                + ` keys=${bd ? Object.keys(bd).join(",") : "null"}`
                                + ` bitmapId=${this._$bitmapId}`
                                + ` inBitmap=${this._$inBitmap}`
                            );
                        }
                    }
                    if (rc[vi] === Graphics.BITMAP_STROKE) {
                        const bd = rc[vi + 5];
                        if (bd && !(bd instanceof BitmapData)
                            && typeof bd !== "number"
                        ) {
                            console.warn(
                                `[ShapeDiag] lib=${this.id} BITMAP_STROKE@${vi+5}`
                                + ` is ${typeof bd}`
                                + (bd && bd.constructor
                                    ? ` (${bd.constructor.name})`
                                    : "")
                                + ` keys=${bd ? Object.keys(bd).join(",") : "null"}`
                                + ` bitmapId=${this._$bitmapId}`
                                + ` inBitmap=${this._$inBitmap}`
                            );
                        }
                    }
                }
            }

            this._$graphicBuffer = graphics._$getRecodes();
            this._$bufferVersion = hydrationVersion;
        }
        graphics._$buffer = this._$graphicBuffer;

        if (_siPlayback) {
            const _siT1 = performance.now();
            const _siTotal = _siT1 - _siT0;
            if (_siTotal > 10) {
                const _msg = `[ShapeInstDbg] shape.id=${this.id} recodes=${this._$recodes.length} bufferCached=${this._$bufferVersion === (Util.$hydrationVersion|0)} total=${_siTotal.toFixed(1)}ms`;
                if (window.n2fElectron) window.n2fElectron.logDebug(_msg); else console.warn(_msg);
            }
        }

        return shape;
    }

    /**
     * @override
     */
    _applyHydratedData (data)
    {
        if (data.recodes) {
            this.recodes = data.recodes;
        }
        if (data.bounds) {
            this.bounds = data.bounds;
        }
        // Invalidate cached graphics so next render uses real data
        this._$graphicBuffer = null;
    }
}
