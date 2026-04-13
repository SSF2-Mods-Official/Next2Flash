/**
 * @type {number}
 * @default 0
 */
let characterId = 0;

const Util = {};
window.Util = Util;

// Route [N2F-DBG] console.warn to Electron main-process stdout + log file
(function () {
    const _origWarn = console.warn;
    console.warn = function () {
        _origWarn.apply(console, arguments);
        if (window.n2fElectron && arguments.length > 0
            && typeof arguments[0] === 'string'
            && arguments[0].indexOf('[N2F-DBG]') === 0
        ) {
            window.n2fElectron.logDebug(arguments[0]);
        }
    };
})();

Util.VERSION                  = 1;
Util.PREFIX                   = "__next2d-tools__";
Util.DATABASE_NAME            = "save-data";
Util.STORE_KEY                = "local";
Util.REVISION_LIMIT           = 100;
Util.$activeWorkSpaceId       = 0;
Util.$activeCharacterIds      = [];
Util.$workSpaces              = [];
Util.$readStatus              = 0;
Util.$readEnd                 = 1;
Util.$shiftKey                = false;
Util.$ctrlKey                 = false;
Util.$altKey                  = false;
Util.$zoomScale               = 1.0;
Util.$currentFrame            = 1;
Util.$root                    = null;
Util.$Rad2Deg                 = 180 / Math.PI;
Util.$Deg2Rad                 = Math.PI / 180;
Util.$keyLock                 = false;
Util.$activeScript            = false;
Util.$previewMode             = false;
Util.$offsetLeft              = 0;
Util.$offsetTop               = 0;
Util.$currentCursor           = "auto";
Util.$useIds                  = new Map();
Util.$symbols                 = new Map();
Util.$copyWorkSpaceId         = -1;
Util.$copyLibrary             = null;
Util.$copyLayer               = null;
Util.$copyCharacter           = null;
Util.$canCopyLayer            = false;
Util.$canCopyCharacter        = false;
Util.$hitColor                = null;
Util.$updated                 = false;
Util.$languages               = new Map();
Util.$currentLanguage         = null;
Util.$shapePointerColor       = "#009900";
Util.$shapeLinkedPointerColor = "#ffa500";
Util.$shortcut                = new Map();
Util.$globalShortcut          = new Map();
Util.$useShortcutSetting      = false;
Util.$changeLibraryId         = 0;
Util.$canvases                = [];
Util.$sleepCanvases           = [];
Util.$waitFiles               = [];
Util.$loadingFile             = false;
// Incremented after lazy hydration completes to invalidate stale draw caches.
Util.$hydrationVersion        = 0;

const userAgentData = window.navigator.userAgentData;
if (userAgentData) {
    userAgentData
        .getHighEntropyValues(["platform"])
        .then((object) =>
        {
            Util.$isMac = object.platform.indexOf("mac") > -1;
        });
} else {
    Util.$isMac = window.navigator.userAgent.indexOf("Mac") > -1;
}

const canvas     = document.createElement("canvas");
canvas.width     = 1;
canvas.height    = 1;
Util.$hitContext = canvas.getContext("2d");

Util.$useOffscreenCanvas = "transferControlToOffscreen" in canvas;

/**
 * @return {HTMLCanvasElement}
 * @static
 */
Util.$getCanvas = () =>
{
    return Util.$canvases.length
        ? Util.$canvases.shift()
        : document.createElement("canvas");
};

/**
 * @param {HTMLCanvasElement} canvas
 * @static
 */
Util.$poolCanvas = (canvas) =>
{
    if (!(canvas instanceof HTMLCanvasElement)) {
        return ;
    }

    // canvas reset
    canvas.width = canvas.height = 1;

    // pool
    canvas.setAttribute("class", "");
    canvas.setAttribute("style", "");
    Util.$canvases.push(canvas);
};

Util.$cloneMovieClip = (from_work_space_id, movie_clip) =>
{
    const fromWorkSpace = Util.$workSpaces[from_work_space_id];
    const toWorkSpace   = Util.$currentWorkSpace();

    const activeWorkSpaceId = Util.$activeWorkSpaceId;
    Util.$activeWorkSpaceId = this._$copyWorkSpaceId;

    const movieClip = movie_clip.clone();
    Util.$activeWorkSpaceId = activeWorkSpaceId;

    for (const layer of movieClip._$layers.values()) {

        // 設置されたレイヤーを複製
        const newLayer = new Layer();
        for (let idx = 0; idx < layer._$characters.length; ++idx) {

            // 複製先でIDを発番するのでtoObjectを利用する
            Util.$activeWorkSpaceId = from_work_space_id;
            const character = new Character(
                JSON.parse(JSON.stringify(layer._$characters[idx].toObject()))
            );

            // 初期化
            character._$id = toWorkSpace._$characterId++;

            Util.$activeWorkSpaceId = activeWorkSpaceId;

            const instance = fromWorkSpace
                .getLibrary(character.libraryId);

            if (this._$copyMapping.has(instance.id)) {
                character.libraryId = this._$copyMapping.get(instance.id);
                newLayer.addCharacter(character);
                continue;
            }

            if (instance.folderId) {

                const folders = [];

                let parent = instance;
                while (parent._$folderId) {
                    parent = fromWorkSpace.getLibrary(
                        parent._$folderId
                    );
                    folders.unshift(parent);
                }

                for (let idx = 0; folders.length > idx; ++idx) {

                    const folder = folders[idx];

                    const path = folder
                        .getPathWithWorkSpace(fromWorkSpace);

                    if (toWorkSpace._$nameMap.has(path)) {

                        if (!this._$instanceMap.has(folder.id)) {
                            this._$instanceMap.set(folder.id, []);
                        }

                        this._$instanceMap
                            .get(folder.id)
                            .push({
                                "layer": null,
                                "path": path,
                                "character": folder
                            });

                        continue;
                    }

                    const clone = folder.clone();

                    const id = toWorkSpace.nextLibraryId;
                    this._$copyMapping.set(clone.id, id);

                    clone._$id = id;
                    if (clone.folderId
                        && this._$copyMapping.has(clone.folderId)
                    ) {
                        clone.folderId = this
                            ._$copyMapping
                            .get(clone.folderId);
                    }

                    toWorkSpace._$libraries.set(clone.id, clone);

                    Util
                        .$libraryController
                        .createInstance(
                            clone.type,
                            clone.name,
                            clone.id,
                            clone.symbol
                        );

                }
            }

            // コピー元のワークスペースからpathを算出
            const path = instance
                .getPathWithWorkSpace(fromWorkSpace);

            if (toWorkSpace._$nameMap.has(path)) {

                if (!this._$instanceMap.has(instance.id)) {
                    this._$instanceMap.set(instance.id, []);
                }

                this._$instanceMap
                    .get(instance.id)
                    .push({
                        "layer": newLayer,
                        "path": path,
                        "character": character
                    });

                continue;
            }

            // fixed logic 複製を生成
            const clone = instance.type === InstanceType.MOVIE_CLIP
                ? this.cloneMovieClip(instance)
                : instance.clone();

            // ライブラリにアイテムを追加
            const id = toWorkSpace.nextLibraryId;
            this._$copyMapping.set(instance.id, id);

            character.libraryId = id;
            clone._$id = id;
            toWorkSpace._$libraries.set(clone.id, clone);

            if (clone.folderId
                && this._$copyMapping.has(clone.folderId)
            ) {
                clone.folderId = this
                    ._$copyMapping
                    .get(clone.folderId);
            }

            Util
                .$libraryController
                .createInstance(
                    clone.type,
                    clone.name,
                    clone.id,
                    clone.symbol
                );

            toWorkSpace
                ._$nameMap
                .set(path, clone.id);

            newLayer.addCharacter(character);
        }

        // 空のキーフレームをコピー
        for (let idx = 0; idx < layer._$emptys.length; ++idx) {
            newLayer.addEmptyCharacter(
                layer._$emptys[idx].clone()
            );
        }

        newLayer.id = layer.id;
        movieClip.setLayer(newLayer.id, newLayer);
    }

    return movieClip;
};

/**
 * @param  {*}   value
 * @param  {int} min
 * @param  {int} max
 * @return {number}
 * @static
 */
Util.$clamp = (value, min, max) =>
{
    const number = +value;
    return Math.min(Math.max(min, isNaN(number) || !isFinite(number) ? 0 : number), max);
};

/**
 * @param  {string} key
 * @param  {object} [options=null]
 * @return {string}
 * @static
 */
Util.$generateShortcutKey = (key, options = null) =>
{
    let value = key.length === 1 ? key.toLowerCase() : key;
    if (options) {
        if (options.shift) {
            value += "Shift";
        }
        if (options.alt) {
            value += "Alt";
        }
        if (options.ctrl) {
            value += "Ctrl";
        }
    }
    return value;
};

/**
 * @param  {*} source
 * @return {boolean}
 * @static
 */
Util.$isArray = (source) =>
{
    return Array.isArray(source);
};

/**
 * @param  {string} [value="auto"]
 * @return {void}
 * @static
 */
Util.$setCursor = (value = "auto") =>
{
    if (Util.$currentCursor !== value) {
        Util.$currentCursor = value;
        document
            .documentElement
            .style
            .setProperty("--tool-cursor", value);
    }
};

/**
 * @description モーダルのアニメーションイベントを登録
 *
 * @param  {HTMLElement} element
 * @return {void}
 * @method
 * @static
 */
Util.$addModalEvent = (element) =>
{
    const elements = element
        .querySelectorAll("[data-detail]");

    for (let idx = 0; idx < elements.length; ++idx) {

        const element = elements[idx];

        element.addEventListener("mouseover", Util.$fadeIn);
        element.addEventListener("mouseout",  Util.$fadeOut);
    }
};

/**
 * @description モーダルのフェードアウト関数
 *
 * @param  {MouseEvent} event
 * @method
 * @static
 */
Util.$fadeIn = (event) =>
{
    const object = Util.$userSetting.getPublishSetting();
    if ("modal" in object && !object.modal) {
        return ;
    }

    const target = event.currentTarget;

    let value = Util.$currentLanguage.replace(
        target.dataset.detail
    );

    let shortcutKey = target.dataset.shortcutKey;
    if (shortcutKey) {

        const mapping = Util.$shortcutSetting.viewMapping.get(
            target.dataset.area
        );

        const shortcutText = mapping.has(shortcutKey)
            ? mapping.get(shortcutKey).text
            : target.dataset.shortcutText;

        value += ` (${shortcutText})`;
    }

    const element = document.getElementById("detail-modal");
    if (element.textContent !== value) {
        element.textContent = value;
    }

    // 表示領域に収まるようx座標を調整
    switch (true) {

        case element.clientWidth + event.pageX - 20 > window.innerWidth:
            element.style.left = `${event.pageX - (element.clientWidth + event.pageX + 10 - window.innerWidth)}px`;
            break;

        case 0 > event.pageX - 20:
            element.style.left = "10px";
            break;

        default:
            element.style.left  = `${event.pageX - 20}px`;
            break;

    }

    // 表示領域に収まるようy座標を調整
    switch (true) {

        case element.clientHeight + event.pageY + 20 > window.innerHeight:
            element.style.top = `${event.pageY - element.clientHeight - 20}px`;
            break;

        default:
            element.style.top = `${event.pageY + 20}px`;
            break;

    }

    element.setAttribute("class", "fadeIn");

    // 1.5秒で自動的に消えるようタイマーをセット
    element.dataset.timerId = setTimeout(() =>
    {
        if (!element.classList.contains("fadeOut")) {
            element.setAttribute("class", "fadeOut");
        }
    }, 1500);
};

/**
 * @description モーダルのフェードアウト関数
 *
 * @method
 * @static
 */
Util.$fadeOut = () =>
{
    const object = Util.$userSetting.getPublishSetting();
    if ("modal" in object && !object.modal) {
        return ;
    }

    const element = document.getElementById("detail-modal");
    clearTimeout(element.dataset.timerId | 0);
    element.setAttribute("class", "fadeOut");
};

/**
 * @param  {string} ignore
 * @return {void}
 * @static
 */
Util.$endMenu = (ignore) =>
{
    const names = [
        "timeline-menu",
        "timeline-header-menu",
        "library-menu",
        "tab-name-menu",
        "timeline-layer-menu",
        "scene-name-menu",
        "user-setting",
        "screen-menu",
        "editor-modal",
        "plugin-modal",
        "shortcut-setting-menu",
        "library-export-modal",
        "screen-order-menu",
        "screen-align-menu",
        "change-movie-clip"
    ];

    for (let idx = 0; idx < names.length; ++idx) {

        const name = names[idx];
        if (name === ignore) {
            continue;
        }

        if (name === "editor-modal"
            && Util.$javaScriptEditor.active
        ) {
            Util.$javaScriptEditor.hide();
        }

        const menu = document.getElementById(name);
        if (!menu.classList.contains("fadeIn")) {
            continue;
        }
        menu.setAttribute("class", "fadeOut");
    }
};

/**
 * @return {void}
 * @static
 */
Util.$loadSaveData = () =>
{
    Util.$saveProgress.start();

    const binary = localStorage
        .getItem(`${Util.PREFIX}@${Util.DATABASE_NAME}`);

    if (binary) {

        localStorage
            .removeItem(`${Util.PREFIX}@${Util.DATABASE_NAME}`);

        const length = binary.length;
        const buffer = new Uint8Array(length);
        for (let idx = 0; idx < length; ++idx) {
            buffer[idx] = binary.charCodeAt(idx) & 0xff;
        }

        Util.$saveProgress.zlibInflate();

        Util.$unZlibWorker.postMessage({
            "buffer": buffer,
            "type": "local"
        }, [buffer.buffer]);

    } else {

        Util.$saveProgress.launchDatabase(10);

        const request = Util.$launchDB();
        request.onsuccess = (event) =>
        {
            const db = event.target.result;
            const transaction = db.transaction(
                `${Util.DATABASE_NAME}`, "readonly"
            );

            const store = transaction
                .objectStore(`${Util.DATABASE_NAME}`);

            const request = store.get(Util.STORE_KEY);
            request.onsuccess = (event) =>
            {
                const binary = event.target.result;
                if (binary) {

                    const length = binary.length;
                    const buffer = new Uint8Array(length);
                    for (let idx = 0; idx < length; ++idx) {
                        buffer[idx] = binary.charCodeAt(idx) & 0xff;
                    }

                    Util.$saveProgress.zlibInflate();

                    Util.$unZlibWorker.postMessage({
                        "buffer": buffer,
                        "type": "local"
                    }, [buffer.buffer]);

                } else {

                    Util.$workSpaces.push(new WorkSpace());

                    Util.$screenTab.run();

                    Util.$initializeEnd();

                }

                db.close();
            };
        };
    }
};

/**
 * @param   {Float32Array} a
 * @param   {Float32Array} b
 * @returns {Float32Array}
 * @static
 */
Util.$multiplicationMatrix = (a, b) =>
{
    return new Float32Array([
        a[0] * b[0] + a[2] * b[1],
        a[1] * b[0] + a[3] * b[1],
        a[0] * b[2] + a[2] * b[3],
        a[1] * b[2] + a[3] * b[3],
        a[0] * b[4] + a[2] * b[5] + a[4],
        a[1] * b[4] + a[3] * b[5] + a[5]
    ]);
};

/**
 * @description 画面全体のショートカットを登録
 *
 * @param  {string} code
 * @param  {function} callback
 * @return {void}
 * @method
 * @static
 */
Util.$setShortcut = (code, callback) =>
{
    Util.$shortcut.set(code, callback);
};

/**
 * @description 画面全体のショートカットを登録
 *
 * @param  {string} code
 * @param  {function} callback
 * @return {void}
 * @method
 * @static
 */
Util.$setGlobalShortcut = (code, callback) =>
{
    Util.$globalShortcut.set(code, callback);
};

/**
 * @description ショートカットを削除
 *
 * @param  {string} code
 * @return {void}
 * @method
 * @static
 */
Util.$deleteShortcut = (code) =>
{
    if (!Util.$shortcut.has(code)) {
        return ;
    }
    Util.$shortcut.delete(code);
};

/**
 * @param  {KeyboardEvent} event
 * @return {void}
 * @method
 * @static
 */
Util.$executeKeyCommand = (event) =>
{
    Util.$shiftKey = event.shiftKey;
    Util.$ctrlKey  = event.ctrlKey || event.metaKey; // command
    Util.$altKey   = event.altKey;

    if (Util.$ctrlKey) {

        switch (event.key) {

            case "-":
            case "+":
            case ";":
                event.stopPropagation();
                event.preventDefault();
                break;

            default:
                break;

        }

    }

    const code = Util.$generateShortcutKey(event.key, {
        "alt": Util.$altKey,
        "shift": Util.$shiftKey,
        "ctrl": Util.$ctrlKey
    });

    if (Util.$globalShortcut.has(code)) {
        event.stopPropagation();
        event.preventDefault();
        Util.$globalShortcut.get(code)(event);
        return ;
    }

    if (Util.$keyLock) {
        return ;
    }

    if (Util.$useShortcutSetting) {
        event.stopPropagation();
        event.preventDefault();
        return ;
    }

    if (!Util.$shortcut.has(code)) {
        return ;
    }

    event.stopPropagation();
    event.preventDefault();
    Util.$shortcut.get(code)(event);
};

/**
 * @description AudioContextを起動
 */
Util.$loadAudioContext = () =>
{
    window.removeEventListener("click", Util.$loadAudioContext);
    Util.$audioContext = new AudioContext();

    if ("next2d" in window) {
        Util.$root.stage._$player._$loadWebAudio();
    }
};

/**
 * @return {void}
 * @static
 */
Util.$initialize = () =>
{
    if ("Raven" in window) {
        Raven.config(
            "https://ebbc692644d14dddaa6f6fec5a9a2dc6@o4504829779705856.ingest.sentry.io/4504829782458368"
        ).install();

        // eslint-disable-next-line no-unused-vars
        window.onerror = (message, file, line, col, error) =>
        {
            Raven.captureException(error);
        };
    }

    // end event
    window.removeEventListener("DOMContentLoaded", Util.$initialize);

    // clickでAudioContextを起動
    window.addEventListener("mousedown", Util.$loadAudioContext);

    // ブラウザを離れる時は初期化
    document.body.addEventListener("mouseleave", () =>
    {
        Util.$shiftKey = false;
        Util.$ctrlKey  = false;
        Util.$altKey   = false;
    });

    Util.$filterClasses = {
        "BevelFilter": BevelFilter,
        "BlurFilter": BlurFilter,
        "DropShadowFilter": DropShadowFilter,
        "GlowFilter": GlowFilter,
        "GradientBevelFilter": GradientBevelFilter,
        "GradientGlowFilter": GradientGlowFilter
    };

    Util.$languages.set("Japanese", Japanese);
    Util.$languages.set("English", English);
    Util.$languages.set("Chinese", Chinese);
    Util.$languages.set("Korean", Korean);
    Util.$languages.set("French", French);
    Util.$languages.set("Russia", Russia);
    Util.$languages.set("Italiano", Italiano);
    Util.$languages.set("Spanish", Spanish);
    Util.$languages.set("Bulgaria", Bulgaria);
    Util.$languages.set("Finland", Finland);
    Util.$languages.set("Germany", Germany);
    Util.$languages.set("Hungary", Hungary);
    Util.$languages.set("Indonesia", Indonesia);
    Util.$languages.set("Latvia", Latvia);
    Util.$languages.set("Lithuania", Lithuania);
    Util.$languages.set("Netherlands", Netherlands);
    Util.$languages.set("Poland", Poland);
    Util.$languages.set("Romania", Romania);
    Util.$languages.set("Slovakia", Slovakia);
    Util.$languages.set("Turkey", Turkey);

    let language = localStorage
        .getItem(`${Util.PREFIX}@language-setting`);

    if (!language) {

        switch (navigator.language) {

            case "ja":
                language = "Japanese";
                break;

            case "ko":
                language = "Korean";
                break;

            case "zh":
                language = "Chinese";
                break;

            case "fr":
                language = "French";
                break;

            case "ru":
                language = "Russia";
                break;

            case "it":
                language = "Italiano";
                break;

            case "es":
                language = "Spanish";
                break;

            case "bg":
                language = "Bulgaria";
                break;

            case "fi":
                language = "Finland";
                break;

            case "de":
                language = "Germany";
                break;

            case "hu":
                language = "Hungary";
                break;

            case "id":
                language = "Indonesia";
                break;

            case "lv":
                language = "Latvia";
                break;

            case "lt":
                language = "Lithuania";
                break;

            case "nl":
                language = "Netherlands";
                break;

            case "pl":
                language = "Poland";
                break;

            case "ro":
                language = "Romania";
                break;

            case "sk":
                language = "Slovakia";
                break;

            case "tr":
                language = "Turkey";
                break;

            default:
                language = "English";
                break;

        }

    }

    const LanguageClass = Util.$languages.get(language);
    Util.$currentLanguage = new LanguageClass();

    const width  = Stage.STAGE_DEFAULT_WIDTH;
    const height = Stage.STAGE_DEFAULT_HEIGHT;
    const fps    = Stage.STAGE_DEFAULT_FPS;

    const previewDisplay = document.getElementById("preview-display");
    if (previewDisplay) {
        previewDisplay.style.width  = `${width}px`;
        previewDisplay.style.height = `${height}px`;
    }

    if ("next2d" in window) {
        window
            .next2d
            .createRootMovieClip(width, height, fps, {
                "tagId": "preview-display"
            }).then((root) =>
            {
                Util.$root = root;
                root.stage._$player.stop();

                Util.$javaScriptEditor.createEditor();
            });

        const { LoaderInfo } = window.next2d.display;
        Util.$loaderInfo = new LoaderInfo();
    }
    // load local data
    Util.$loadSaveData();

    // added event
    window.addEventListener("keydown", Util.$executeKeyCommand);

    // key reset
    window.addEventListener("keyup", () =>
    {
        Util.$shiftKey = false;
        Util.$ctrlKey  = false;
        Util.$altKey   = false;
    });

    window.addEventListener("beforeunload", (event) =>
    {
        if (Util.$updated) {

            event.preventDefault();
            event.stopPropagation();

            event.returnValue = "データ保存中...";

            // 保存を実行
            Util.$autoSave();

            return false;
        }
    });

    // フレームのデフォルト幅をセット
    document
        .documentElement
        .style
        .setProperty(
            "--timeline-frame-width",
            `${TimelineTool.DEFAULT_TIMELINE_WIDTH}px`
        );

    document
        .documentElement
        .style
        .setProperty(
            "--timeline-frame-height",
            `${TimelineTool.DEFAULT_TIMELINE_HEIGHT - 1}px`
        );

    document
        .documentElement
        .style
        .setProperty("--screen-height", `${window.innerHeight - 50}px`);

    const previewStop = document.getElementById("preview-stop");
    if (previewStop) {
        previewStop.addEventListener("click", Util.$hidePreview);
    }

    document
        .documentElement
        .style
        .setProperty("--ad", "280px");

    // clear
    Util.$initialize = null;
};
window.addEventListener("DOMContentLoaded", Util.$initialize);
window.addEventListener("resize", () =>
{
    if (Util.$saveProgress.active) {
        return ;
    }

    Util.$rebuildTimeline();
    Util.$rebuildRuler();
});

/**
 * @description 定規を現在のスケールで再構成
 *
 * @method
 * @static
 */
Util.$rebuildRuler = () =>
{
    const workSpace = Util.$currentWorkSpace();
    if (workSpace._$uiState.rulerX.length || workSpace._$uiState.rulerY.length) {
        Util.$screenRuler.rebuild();
    }
};

/**
 * @description タイムラインを現在の幅で再構成
 *
 * @method
 * @static
 */
Util.$rebuildTimeline = () =>
{
    // Check if workspace exists before rebuilding
    const workSpace = Util.$currentWorkSpace();
    if (!workSpace) {
        return;
    }

    // ヘッダーを再構成
    Util.$timelineHeader._$currentFrame = -1;
    Util.$timelineHeader.setWidth();
    Util.$timelineHeader.rebuild();

    // タイムラインを再構成
    Util.$timelineMarker.resetMarker();
    Util.$timelineLayer.moveTimeLine();
    Util.$timelineLayer.updateClientSize();
};

/**
 * @return {void}
 * @static
 */
Util.$showPreview = () =>
{
    // タイムライン側を停止
    Util
        .$timelinePlayer
        .executeTimelineStop();

    Util.$javaScriptEditor.save();

    Util.$previewMode = true;
    Util.$keyLock     = true;

    const element = document.getElementById("player-preview");
    element.style.display = "";
    element.style.zIndex  = "9999";

    const workSpace = Util.$currentWorkSpace();

    const preview = document.getElementById("preview-display");
    preview.style.width  = `${workSpace.stage.width}px`;
    preview.style.height = `${workSpace.stage.height}px`;

    const stopElement = document.getElementById("preview-stop");
    stopElement.style.top  = `${preview.offsetTop - 20}px`;
    stopElement.style.left = `${preview.offsetLeft + workSpace.stage.width}px`;
    stopElement.addEventListener("click", Util.$hidePreview);

    const stage = Util.$root.stage;
    const player  = stage._$player;

    stage.clearGlobalVariable();
    stage._$events = new Map();
    player._$broadcastEvents = new Map();

    const blob = Publish.toBlob();
    Util.$useIds.clear();

    if (!window.next2d || !window.next2d.display) {
        console.error("[Preview] next2d player not loaded");
        Util.$hidePreview();
        return;
    }

    const { Loader } = window.next2d.display;
    const { URLRequest } = window.next2d.net;
    const { Event } = window.next2d.events;

    const loader = new Loader();

    loader
        .contentLoaderInfo
        .addEventListener(Event.COMPLETE, (event) =>
        {
            const loaderInfo = event.currentTarget;

            const stage  = Util.$root.stage;
            const player = stage._$player;
            const data   = loaderInfo._$data;

            player.width  = data.stage.width;
            player.height = data.stage.height;
            player.stage._$frameRate = data.stage.fps;

            // fixed logic
            player._$resize();

            while (stage.numChildren) {
                stage.removeChildAt(0);
            }

            Util.$root = null;
            Util.$root = loaderInfo.content;
            stage.addChild(Util.$root);

            player._$setBackgroundColor(
                `0xff${data.stage.bgColor.slice(1)}` | 0
            );

            player.cacheStore.reset();
            player.play();
        });

    loader
        .contentLoaderInfo
        .addEventListener("ioError", (event) =>
        {
            console.error("[Preview] Loader IO error:", event);
        });

    loader.load(new URLRequest(
        URL.createObjectURL(blob)
    ));

    // setup clear
    player._$broadcastEvents.clear();
    window.next2d.media.SoundMixer.volume = 1;

    player._$loadStatus = 1;
    player._$updateLoadStatus();
};

/**
 * @return {void}
 * @static
 */
Util.$hidePreview = () =>
{
    const stopElement = document.getElementById("preview-stop");
    stopElement.removeEventListener("click", Util.$hidePreview);

    const element = document.getElementById("player-preview");
    element.style.display = "none";
    element.style.zIndex  = "0";

    Util.$previewMode = false;
    if (!Util.$activeScript) {
        Util.$keyLock = false;
    }

    const root = Util.$root;
    const player = root.stage._$player;
    while (Util.$root.numChildren) {
        root.removeChildAt(0);
    }

    player._$setBackgroundColor();
    player.stop();
};

/**
 * @return {string}
 * @static
 */
Util.$toJSON = () =>
{
    // cache WorkSpaceId
    const activeWorkSpaceId = Util.$activeWorkSpaceId;

    const children = document
        .getElementById("view-tab-area")
        .children;

    const data = [];
    for (let idx = 0; idx < children.length; ++idx) {

        const node = children[idx];

        const workSpace = Util.$workSpaces[node.dataset.tabId | 0];
        if (!workSpace) {
            continue;
        }

        Util.$activeWorkSpaceId = node.dataset.tabId | 0;

        data.push(workSpace.toJSON());

    }

    // reset
    Util.$activeWorkSpaceId = activeWorkSpaceId;

    return JSON.stringify(data);
};

/**
 * @return {Promise}
 * @static
 */
Util.$autoSave = () =>
{
    if (Util.$saveProgress.active) {
        return Promise.resolve();
    }

    Util.$javaScriptEditor.save();
    Util.$saveProgress.start();

    return new Promise((resolve) =>
    {
        Util.$saveProgress.createJson();

        setTimeout(() =>
        {
            resolve({
                "object": Util.$toJSON(),
                "type": "local"
            });
        }, 200);

    })
        .then((data) =>
        {
            Util.$saveProgress.zlibDeflate();

            if (Util.$zlibWorkerActive) {

                Util.$zlibQueues.push(data);

            } else {

                Util.$zlibWorkerActive = true;
                Util.$zlibWorker.postMessage(data);

            }
        });

};

/**
 * @param   {array} matrix
 * @returns {array}
 * @method
 * @static
 */
Util.$inverseMatrix = (matrix) =>
{
    const tx = matrix[2] * matrix[5] - matrix[3] * matrix[4];
    const ty = matrix[1] * matrix[4] - matrix[0] * matrix[5];

    let det = matrix[0] * matrix[3] - matrix[2] * matrix[1];
    if (!det || !isFinite(det)) {
        return [
            matrix[3],
            -matrix[1],
            -matrix[2],
            matrix[0] ,
            tx,
            ty
        ];
    }

    const rdet = 1 / det;
    return [
        matrix[3] * rdet,
        -matrix[1] * rdet,
        -matrix[2] * rdet,
        matrix[0] * rdet,
        tx * rdet,
        ty * rdet
    ];
};

/**
 * @param  {number} num
 * @return {number}
 */
Util.$toFixed4 = (num) =>
{
    const value = num.toString();
    const index = value.indexOf("e");
    if (index > -1) {
        num = +value.slice(0, index);
    }
    return +num.toFixed(4);
};

/**
 * @return {WorkSpace}
 * @static
 */
Util.$currentWorkSpace = () =>
{
    return Util.$workSpaces[Util.$activeWorkSpaceId];
};

/**
 * @return {void}
 * @static
 */
Util.$initializeEnd = () =>
{
    Util.$readStatus++;
    if (Util.$readStatus === Util.$readEnd) {

        // ローディング演出終了
        Util.$saveProgress.end();

        // HTML内に設定されたdata-detailの値を、モーダル出力するのに登録
        Util.$addModalEvent(document);

        // WorkSpaceを起動
        Util.$currentWorkSpace().run();
    }
};

/**
 * @param {number} id
 * @static
 */
Util.$changeWorkSpace = (id) =>
{
    // reset
    Util.$useIds.clear();
    Util.$symbols.clear();

    Util.$currentWorkSpace().stop();

    Util.$activeWorkSpaceId = id | 0;

    Util.$currentWorkSpace().run();
};

// ZLIB Inflate Worker
Util.$unZlibWorker = new Worker(URL.createObjectURL(
    new Blob(["/*! pako 2.1.0 https://github.com/nodeca/pako @license (MIT AND Zlib) */!function(e,t){\"object\"==typeof exports&&\"undefined\"!=typeof module?t(exports):\"function\"==typeof define&&define.amd?define([\"exports\"],t):t((e=\"undefined\"!=typeof globalThis?globalThis:e||self).pako={})}(this,function(e){\"use strict\";var t=function(e,t,i,a){for(var n=65535&e,r=e>>>16&65535,o=0;0!==i;){i-=o=i>2e3?2e3:i;do{r=r+(n=n+t[a++]|0)|0}while(--o);n%=65521,r%=65521}return n|r<<16},i=new Uint32Array(function(){for(var e,t=[],i=0;i<256;i++){e=i;for(var a=0;a<8;a++)e=1&e?3988292384^e>>>1:e>>>1;t[i]=e}return t}()),a=function(e,t,a,n){var r=i,o=n+a;e^=-1;for(var s=n;s<o;s++)e=e>>>8^r[255&(e^t[s])];return-1^e},n=16209,r=function(e,t){var i,a,r,o,s,d,l,f,h,c,u,w,b,m,k,_,g,v,p,y,x,E,A,R,Z=e.state;i=e.next_in,A=e.input,a=i+(e.avail_in-5),r=e.next_out,R=e.output,o=r-(t-e.avail_out),s=r+(e.avail_out-257),d=Z.dmax,l=Z.wsize,f=Z.whave,h=Z.wnext,c=Z.window,u=Z.hold,w=Z.bits,b=Z.lencode,m=Z.distcode,k=(1<<Z.lenbits)-1,_=(1<<Z.distbits)-1;e:do{w<15&&(u+=A[i++]<<w,w+=8,u+=A[i++]<<w,w+=8),g=b[u&k];t:for(;;){if(u>>>=v=g>>>24,w-=v,0==(v=g>>>16&255))R[r++]=65535&g;else{if(!(16&v)){if(!(64&v)){g=b[(65535&g)+(u&(1<<v)-1)];continue t}if(32&v){Z.mode=16191;break e}e.msg=\"invalid literal/length code\",Z.mode=n;break e}p=65535&g,(v&=15)&&(w<v&&(u+=A[i++]<<w,w+=8),p+=u&(1<<v)-1,u>>>=v,w-=v),w<15&&(u+=A[i++]<<w,w+=8,u+=A[i++]<<w,w+=8),g=m[u&_];i:for(;;){if(u>>>=v=g>>>24,w-=v,!(16&(v=g>>>16&255))){if(!(64&v)){g=m[(65535&g)+(u&(1<<v)-1)];continue i}e.msg=\"invalid distance code\",Z.mode=n;break e}if(y=65535&g,w<(v&=15)&&(u+=A[i++]<<w,(w+=8)<v&&(u+=A[i++]<<w,w+=8)),(y+=u&(1<<v)-1)>d){e.msg=\"invalid distance too far back\",Z.mode=n;break e}if(u>>>=v,w-=v,y>(v=r-o)){if((v=y-v)>f&&Z.sane){e.msg=\"invalid distance too far back\",Z.mode=n;break e}if(x=0,E=c,0===h){if(x+=l-v,v<p){p-=v;do{R[r++]=c[x++]}while(--v);x=r-y,E=R}}else if(h<v){if(x+=l+h-v,(v-=h)<p){p-=v;do{R[r++]=c[x++]}while(--v);if(x=0,h<p){p-=v=h;do{R[r++]=c[x++]}while(--v);x=r-y,E=R}}}else if(x+=h-v,v<p){p-=v;do{R[r++]=c[x++]}while(--v);x=r-y,E=R}for(;p>2;)R[r++]=E[x++],R[r++]=E[x++],R[r++]=E[x++],p-=3;p&&(R[r++]=E[x++],p>1&&(R[r++]=E[x++]))}else{x=r-y;do{R[r++]=R[x++],R[r++]=R[x++],R[r++]=R[x++],p-=3}while(p>2);p&&(R[r++]=R[x++],p>1&&(R[r++]=R[x++]))}break}}break}}while(i<a&&r<s);i-=p=w>>3,u&=(1<<(w-=p<<3))-1,e.next_in=i,e.next_out=r,e.avail_in=i<a?a-i+5:5-(i-a),e.avail_out=r<s?s-r+257:257-(r-s),Z.hold=u,Z.bits=w},o=new Uint16Array([3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0]),s=new Uint8Array([16,16,16,16,16,16,16,16,17,17,17,17,18,18,18,18,19,19,19,19,20,20,20,20,21,21,21,21,16,72,78]),d=new Uint16Array([1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,0,0]),l=new Uint8Array([16,16,16,16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26,27,27,28,28,29,29,64,64]),f=function(e,t,i,a,n,r,f,h){var c,u,w,b,m,k,_,g,v,p=h.bits,y=0,x=0,E=0,A=0,R=0,Z=0,S=0,T=0,O=0,U=0,D=null,B=new Uint16Array(16),C=new Uint16Array(16),N=null;for(y=0;y<=15;y++)B[y]=0;for(x=0;x<a;x++)B[t[i+x]]++;for(R=p,A=15;A>=1&&0===B[A];A--);if(R>A&&(R=A),0===A)return n[r++]=20971520,n[r++]=20971520,h.bits=1,0;for(E=1;E<A&&0===B[E];E++);for(R<E&&(R=E),T=1,y=1;y<=15;y++)if(T<<=1,(T-=B[y])<0)return-1;if(T>0&&(0===e||1!==A))return-1;for(C[1]=0,y=1;y<15;y++)C[y+1]=C[y]+B[y];for(x=0;x<a;x++)0!==t[i+x]&&(f[C[t[i+x]]++]=x);if(0===e?(D=N=f,k=20):1===e?(D=o,N=s,k=257):(D=d,N=l,k=0),U=0,x=0,y=E,m=r,Z=R,S=0,w=-1,b=(O=1<<R)-1,1===e&&O>852||2===e&&O>592)return 1;for(;;){_=y-S,f[x]+1<k?(g=0,v=f[x]):f[x]>=k?(g=N[f[x]-k],v=D[f[x]-k]):(g=96,v=0),c=1<<y-S,E=u=1<<Z;do{n[m+(U>>S)+(u-=c)]=_<<24|g<<16|v}while(0!==u);for(c=1<<y-1;U&c;)c>>=1;if(0!==c?(U&=c-1,U+=c):U=0,x++,0==--B[y]){if(y===A)break;y=t[i+f[x]]}if(y>R&&(U&b)!==w){for(0===S&&(S=R),m+=E,T=1<<(Z=y-S);Z+S<A&&!((T-=B[Z+S])<=0);)Z++,T<<=1;if(O+=1<<Z,1===e&&O>852||2===e&&O>592)return 1;n[w=U&b]=R<<24|Z<<16|m-r}}return 0!==U&&(n[m+U]=y-S<<24|64<<16),h.bits=R,0},h={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_MEM_ERROR:-4,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8},c=h.Z_FINISH,u=h.Z_BLOCK,w=h.Z_TREES,b=h.Z_OK,m=h.Z_STREAM_END,k=h.Z_NEED_DICT,_=h.Z_STREAM_ERROR,g=h.Z_DATA_ERROR,v=h.Z_MEM_ERROR,p=h.Z_BUF_ERROR,y=h.Z_DEFLATED,x=16180,E=16190,A=16191,R=16192,Z=16194,S=16199,T=16200,O=16206,U=16209,D=function(e){return(e>>>24&255)+(e>>>8&65280)+((65280&e)<<8)+((255&e)<<24)};function B(){this.strm=null,this.mode=0,this.last=!1,this.wrap=0,this.havedict=!1,this.flags=0,this.dmax=0,this.check=0,this.total=0,this.head=null,this.wbits=0,this.wsize=0,this.whave=0,this.wnext=0,this.window=null,this.hold=0,this.bits=0,this.length=0,this.offset=0,this.extra=0,this.lencode=null,this.distcode=null,this.lenbits=0,this.distbits=0,this.ncode=0,this.nlen=0,this.ndist=0,this.have=0,this.next=null,this.lens=new Uint16Array(320),this.work=new Uint16Array(288),this.lendyn=null,this.distdyn=null,this.sane=0,this.back=0,this.was=0}var C,N,I=function(e){if(!e)return 1;var t=e.state;return!t||t.strm!==e||t.mode<x||t.mode>16211?1:0},z=function(e){if(I(e))return _;var t=e.state;return e.total_in=e.total_out=t.total=0,e.msg=\"\",t.wrap&&(e.adler=1&t.wrap),t.mode=x,t.last=0,t.havedict=0,t.flags=-1,t.dmax=32768,t.head=null,t.hold=0,t.bits=0,t.lencode=t.lendyn=new Int32Array(852),t.distcode=t.distdyn=new Int32Array(592),t.sane=1,t.back=-1,b},F=function(e){if(I(e))return _;var t=e.state;return t.wsize=0,t.whave=0,t.wnext=0,z(e)},M=function(e,t){var i;if(I(e))return _;var a=e.state;return t<0?(i=0,t=-t):(i=5+(t>>4),t<48&&(t&=15)),t&&(t<8||t>15)?_:(null!==a.window&&a.wbits!==t&&(a.window=null),a.wrap=i,a.wbits=t,F(e))},L=function(e,t){if(!e)return _;var i=new B;e.state=i,i.strm=e,i.window=null,i.mode=x;var a=M(e,t);return a!==b&&(e.state=null),a},j=!0,H=function(e){if(j){C=new Int32Array(512),N=new Int32Array(32);for(var t=0;t<144;)e.lens[t++]=8;for(;t<256;)e.lens[t++]=9;for(;t<280;)e.lens[t++]=7;for(;t<288;)e.lens[t++]=8;for(f(1,e.lens,0,288,C,0,e.work,{bits:9}),t=0;t<32;)e.lens[t++]=5;f(2,e.lens,0,32,N,0,e.work,{bits:5}),j=!1}e.lencode=C,e.lenbits=9,e.distcode=N,e.distbits=5},P=function(e,t,i,a){var n,r=e.state;return null===r.window&&(r.wsize=1<<r.wbits,r.wnext=0,r.whave=0,r.window=new Uint8Array(r.wsize)),a>=r.wsize?(r.window.set(t.subarray(i-r.wsize,i),0),r.wnext=0,r.whave=r.wsize):((n=r.wsize-r.wnext)>a&&(n=a),r.window.set(t.subarray(i-a,i-a+n),r.wnext),(a-=n)?(r.window.set(t.subarray(i-a,i),0),r.wnext=a,r.whave=r.wsize):(r.wnext+=n,r.wnext===r.wsize&&(r.wnext=0),r.whave<r.wsize&&(r.whave+=n))),0},K=F,Y=L,X=function(e,i){var n,o,s,d,l,h,B,C,N,z,F,M,L,j,K,Y,X,G,W,q,J,Q,V,$,ee=0,te=new Uint8Array(4),ie=new Uint8Array([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]);if(I(e)||!e.output||!e.input&&0!==e.avail_in)return _;(n=e.state).mode===A&&(n.mode=R),l=e.next_out,s=e.output,B=e.avail_out,d=e.next_in,o=e.input,h=e.avail_in,C=n.hold,N=n.bits,z=h,F=B,Q=b;e:for(;;)switch(n.mode){case x:if(0===n.wrap){n.mode=R;break}for(;N<16;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(2&n.wrap&&35615===C){0===n.wbits&&(n.wbits=15),n.check=0,te[0]=255&C,te[1]=C>>>8&255,n.check=a(n.check,te,2,0),C=0,N=0,n.mode=16181;break}if(n.head&&(n.head.done=!1),!(1&n.wrap)||(((255&C)<<8)+(C>>8))%31){e.msg=\"incorrect header check\",n.mode=U;break}if((15&C)!==y){e.msg=\"unknown compression method\",n.mode=U;break}if(N-=4,J=8+(15&(C>>>=4)),0===n.wbits&&(n.wbits=J),J>15||J>n.wbits){e.msg=\"invalid window size\",n.mode=U;break}n.dmax=1<<n.wbits,n.flags=0,e.adler=n.check=1,n.mode=512&C?16189:A,C=0,N=0;break;case 16181:for(;N<16;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(n.flags=C,(255&n.flags)!==y){e.msg=\"unknown compression method\",n.mode=U;break}if(57344&n.flags){e.msg=\"unknown header flags set\",n.mode=U;break}n.head&&(n.head.text=C>>8&1),512&n.flags&&4&n.wrap&&(te[0]=255&C,te[1]=C>>>8&255,n.check=a(n.check,te,2,0)),C=0,N=0,n.mode=16182;case 16182:for(;N<32;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}n.head&&(n.head.time=C),512&n.flags&&4&n.wrap&&(te[0]=255&C,te[1]=C>>>8&255,te[2]=C>>>16&255,te[3]=C>>>24&255,n.check=a(n.check,te,4,0)),C=0,N=0,n.mode=16183;case 16183:for(;N<16;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}n.head&&(n.head.xflags=255&C,n.head.os=C>>8),512&n.flags&&4&n.wrap&&(te[0]=255&C,te[1]=C>>>8&255,n.check=a(n.check,te,2,0)),C=0,N=0,n.mode=16184;case 16184:if(1024&n.flags){for(;N<16;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}n.length=C,n.head&&(n.head.extra_len=C),512&n.flags&&4&n.wrap&&(te[0]=255&C,te[1]=C>>>8&255,n.check=a(n.check,te,2,0)),C=0,N=0}else n.head&&(n.head.extra=null);n.mode=16185;case 16185:if(1024&n.flags&&((M=n.length)>h&&(M=h),M&&(n.head&&(J=n.head.extra_len-n.length,n.head.extra||(n.head.extra=new Uint8Array(n.head.extra_len)),n.head.extra.set(o.subarray(d,d+M),J)),512&n.flags&&4&n.wrap&&(n.check=a(n.check,o,M,d)),h-=M,d+=M,n.length-=M),n.length))break e;n.length=0,n.mode=16186;case 16186:if(2048&n.flags){if(0===h)break e;M=0;do{J=o[d+M++],n.head&&J&&n.length<65536&&(n.head.name+=String.fromCharCode(J))}while(J&&M<h);if(512&n.flags&&4&n.wrap&&(n.check=a(n.check,o,M,d)),h-=M,d+=M,J)break e}else n.head&&(n.head.name=null);n.length=0,n.mode=16187;case 16187:if(4096&n.flags){if(0===h)break e;M=0;do{J=o[d+M++],n.head&&J&&n.length<65536&&(n.head.comment+=String.fromCharCode(J))}while(J&&M<h);if(512&n.flags&&4&n.wrap&&(n.check=a(n.check,o,M,d)),h-=M,d+=M,J)break e}else n.head&&(n.head.comment=null);n.mode=16188;case 16188:if(512&n.flags){for(;N<16;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(4&n.wrap&&C!==(65535&n.check)){e.msg=\"header crc mismatch\",n.mode=U;break}C=0,N=0}n.head&&(n.head.hcrc=n.flags>>9&1,n.head.done=!0),e.adler=n.check=0,n.mode=A;break;case 16189:for(;N<32;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}e.adler=n.check=D(C),C=0,N=0,n.mode=E;case E:if(0===n.havedict)return e.next_out=l,e.avail_out=B,e.next_in=d,e.avail_in=h,n.hold=C,n.bits=N,k;e.adler=n.check=1,n.mode=A;case A:if(i===u||i===w)break e;case R:if(n.last){C>>>=7&N,N-=7&N,n.mode=O;break}for(;N<3;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}switch(n.last=1&C,N-=1,3&(C>>>=1)){case 0:n.mode=16193;break;case 1:if(H(n),n.mode=S,i===w){C>>>=2,N-=2;break e}break;case 2:n.mode=16196;break;case 3:e.msg=\"invalid block type\",n.mode=U}C>>>=2,N-=2;break;case 16193:for(C>>>=7&N,N-=7&N;N<32;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if((65535&C)!=(C>>>16^65535)){e.msg=\"invalid stored block lengths\",n.mode=U;break}if(n.length=65535&C,C=0,N=0,n.mode=Z,i===w)break e;case Z:n.mode=16195;case 16195:if(M=n.length){if(M>h&&(M=h),M>B&&(M=B),0===M)break e;s.set(o.subarray(d,d+M),l),h-=M,d+=M,B-=M,l+=M,n.length-=M;break}n.mode=A;break;case 16196:for(;N<14;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(n.nlen=257+(31&C),C>>>=5,N-=5,n.ndist=1+(31&C),C>>>=5,N-=5,n.ncode=4+(15&C),C>>>=4,N-=4,n.nlen>286||n.ndist>30){e.msg=\"too many length or distance symbols\",n.mode=U;break}n.have=0,n.mode=16197;case 16197:for(;n.have<n.ncode;){for(;N<3;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}n.lens[ie[n.have++]]=7&C,C>>>=3,N-=3}for(;n.have<19;)n.lens[ie[n.have++]]=0;if(n.lencode=n.lendyn,n.lenbits=7,V={bits:n.lenbits},Q=f(0,n.lens,0,19,n.lencode,0,n.work,V),n.lenbits=V.bits,Q){e.msg=\"invalid code lengths set\",n.mode=U;break}n.have=0,n.mode=16198;case 16198:for(;n.have<n.nlen+n.ndist;){for(;Y=(ee=n.lencode[C&(1<<n.lenbits)-1])>>>16&255,X=65535&ee,!((K=ee>>>24)<=N);){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(X<16)C>>>=K,N-=K,n.lens[n.have++]=X;else{if(16===X){for($=K+2;N<$;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(C>>>=K,N-=K,0===n.have){e.msg=\"invalid bit length repeat\",n.mode=U;break}J=n.lens[n.have-1],M=3+(3&C),C>>>=2,N-=2}else if(17===X){for($=K+3;N<$;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}N-=K,J=0,M=3+(7&(C>>>=K)),C>>>=3,N-=3}else{for($=K+7;N<$;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}N-=K,J=0,M=11+(127&(C>>>=K)),C>>>=7,N-=7}if(n.have+M>n.nlen+n.ndist){e.msg=\"invalid bit length repeat\",n.mode=U;break}for(;M--;)n.lens[n.have++]=J}}if(n.mode===U)break;if(0===n.lens[256]){e.msg=\"invalid code -- missing end-of-block\",n.mode=U;break}if(n.lenbits=9,V={bits:n.lenbits},Q=f(1,n.lens,0,n.nlen,n.lencode,0,n.work,V),n.lenbits=V.bits,Q){e.msg=\"invalid literal/lengths set\",n.mode=U;break}if(n.distbits=6,n.distcode=n.distdyn,V={bits:n.distbits},Q=f(2,n.lens,n.nlen,n.ndist,n.distcode,0,n.work,V),n.distbits=V.bits,Q){e.msg=\"invalid distances set\",n.mode=U;break}if(n.mode=S,i===w)break e;case S:n.mode=T;case T:if(h>=6&&B>=258){e.next_out=l,e.avail_out=B,e.next_in=d,e.avail_in=h,n.hold=C,n.bits=N,r(e,F),l=e.next_out,s=e.output,B=e.avail_out,d=e.next_in,o=e.input,h=e.avail_in,C=n.hold,N=n.bits,n.mode===A&&(n.back=-1);break}for(n.back=0;Y=(ee=n.lencode[C&(1<<n.lenbits)-1])>>>16&255,X=65535&ee,!((K=ee>>>24)<=N);){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(Y&&!(240&Y)){for(G=K,W=Y,q=X;Y=(ee=n.lencode[q+((C&(1<<G+W)-1)>>G)])>>>16&255,X=65535&ee,!(G+(K=ee>>>24)<=N);){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}C>>>=G,N-=G,n.back+=G}if(C>>>=K,N-=K,n.back+=K,n.length=X,0===Y){n.mode=16205;break}if(32&Y){n.back=-1,n.mode=A;break}if(64&Y){e.msg=\"invalid literal/length code\",n.mode=U;break}n.extra=15&Y,n.mode=16201;case 16201:if(n.extra){for($=n.extra;N<$;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}n.length+=C&(1<<n.extra)-1,C>>>=n.extra,N-=n.extra,n.back+=n.extra}n.was=n.length,n.mode=16202;case 16202:for(;Y=(ee=n.distcode[C&(1<<n.distbits)-1])>>>16&255,X=65535&ee,!((K=ee>>>24)<=N);){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(!(240&Y)){for(G=K,W=Y,q=X;Y=(ee=n.distcode[q+((C&(1<<G+W)-1)>>G)])>>>16&255,X=65535&ee,!(G+(K=ee>>>24)<=N);){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}C>>>=G,N-=G,n.back+=G}if(C>>>=K,N-=K,n.back+=K,64&Y){e.msg=\"invalid distance code\",n.mode=U;break}n.offset=X,n.extra=15&Y,n.mode=16203;case 16203:if(n.extra){for($=n.extra;N<$;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}n.offset+=C&(1<<n.extra)-1,C>>>=n.extra,N-=n.extra,n.back+=n.extra}if(n.offset>n.dmax){e.msg=\"invalid distance too far back\",n.mode=U;break}n.mode=16204;case 16204:if(0===B)break e;if(M=F-B,n.offset>M){if((M=n.offset-M)>n.whave&&n.sane){e.msg=\"invalid distance too far back\",n.mode=U;break}M>n.wnext?(M-=n.wnext,L=n.wsize-M):L=n.wnext-M,M>n.length&&(M=n.length),j=n.window}else j=s,L=l-n.offset,M=n.length;M>B&&(M=B),B-=M,n.length-=M;do{s[l++]=j[L++]}while(--M);0===n.length&&(n.mode=T);break;case 16205:if(0===B)break e;s[l++]=n.length,B--,n.mode=T;break;case O:if(n.wrap){for(;N<32;){if(0===h)break e;h--,C|=o[d++]<<N,N+=8}if(F-=B,e.total_out+=F,n.total+=F,4&n.wrap&&F&&(e.adler=n.check=n.flags?a(n.check,s,F,l-F):t(n.check,s,F,l-F)),F=B,4&n.wrap&&(n.flags?C:D(C))!==n.check){e.msg=\"incorrect data check\",n.mode=U;break}C=0,N=0}n.mode=16207;case 16207:if(n.wrap&&n.flags){for(;N<32;){if(0===h)break e;h--,C+=o[d++]<<N,N+=8}if(4&n.wrap&&C!==(4294967295&n.total)){e.msg=\"incorrect length check\",n.mode=U;break}C=0,N=0}n.mode=16208;case 16208:Q=m;break e;case U:Q=g;break e;case 16210:return v;default:return _}return e.next_out=l,e.avail_out=B,e.next_in=d,e.avail_in=h,n.hold=C,n.bits=N,(n.wsize||F!==e.avail_out&&n.mode<U&&(n.mode<O||i!==c))&&P(e,e.output,e.next_out,F-e.avail_out),z-=e.avail_in,F-=e.avail_out,e.total_in+=z,e.total_out+=F,n.total+=F,4&n.wrap&&F&&(e.adler=n.check=n.flags?a(n.check,s,F,e.next_out-F):t(n.check,s,F,e.next_out-F)),e.data_type=n.bits+(n.last?64:0)+(n.mode===A?128:0)+(n.mode===S||n.mode===Z?256:0),(0===z&&0===F||i===c)&&Q===b&&(Q=p),Q},G=function(e){if(I(e))return _;var t=e.state;return t.window&&(t.window=null),e.state=null,b},W=function(e,t){if(I(e))return _;var i=e.state;return 2&i.wrap?(i.head=t,t.done=!1,b):_},q=function(e,i){var a,n=i.length;return I(e)||0!==(a=e.state).wrap&&a.mode!==E?_:a.mode===E&&t(1,i,n,0)!==a.check?g:P(e,i,n,n)?(a.mode=16210,v):(a.havedict=1,b)};function J(e){return J=\"function\"==typeof Symbol&&\"symbol\"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&\"function\"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?\"symbol\":typeof e},J(e)}var Q=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},V=!0;try{String.fromCharCode.apply(null,new Uint8Array(1))}catch(e){V=!1}for(var $=new Uint8Array(256),ee=0;ee<256;ee++)$[ee]=ee>=252?6:ee>=248?5:ee>=240?4:ee>=224?3:ee>=192?2:1;$[254]=$[254]=1;var te=function(e,t){var i,a,n=t||e.length;if(\"function\"==typeof TextDecoder&&TextDecoder.prototype.decode)return(new TextDecoder).decode(e.subarray(0,t));var r=new Array(2*n);for(a=0,i=0;i<n;){var o=e[i++];if(o<128)r[a++]=o;else{var s=$[o];if(s>4)r[a++]=65533,i+=s-1;else{for(o&=2===s?31:3===s?15:7;s>1&&i<n;)o=o<<6|63&e[i++],s--;s>1?r[a++]=65533:o<65536?r[a++]=o:(o-=65536,r[a++]=55296|o>>10&1023,r[a++]=56320|1023&o)}}}return function(e,t){if(t<65534&&e.subarray&&V)return String.fromCharCode.apply(null,e.length===t?e:e.subarray(0,t));for(var i=\"\",a=0;a<t;a++)i+=String.fromCharCode(e[a]);return i}(r,a)},ie=function(e,t){(t=t||e.length)>e.length&&(t=e.length);for(var i=t-1;i>=0&&128==(192&e[i]);)i--;return i<0||0===i?t:i+$[e[i]]>t?i:t},ae={2:\"need dictionary\",1:\"stream end\",0:\"\",\"-1\":\"file error\",\"-2\":\"stream error\",\"-3\":\"data error\",\"-4\":\"insufficient memory\",\"-5\":\"buffer error\",\"-6\":\"incompatible version\"},ne=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg=\"\",this.state=null,this.data_type=2,this.adler=0},re=function(){this.text=0,this.time=0,this.xflags=0,this.os=0,this.extra=null,this.extra_len=0,this.name=\"\",this.comment=\"\",this.hcrc=0,this.done=!1},oe=Object.prototype.toString,se=h.Z_NO_FLUSH,de=h.Z_FINISH,le=h.Z_OK,fe=h.Z_STREAM_END,he=h.Z_NEED_DICT,ce=h.Z_STREAM_ERROR,ue=h.Z_DATA_ERROR,we=h.Z_MEM_ERROR;function be(e){this.options=function(e){for(var t=Array.prototype.slice.call(arguments,1);t.length;){var i=t.shift();if(i){if(\"object\"!==J(i))throw new TypeError(i+\"must be non-object\");for(var a in i)Q(i,a)&&(e[a]=i[a])}}return e}({chunkSize:65536,windowBits:15,to:\"\"},e||{});var t=this.options;t.raw&&t.windowBits>=0&&t.windowBits<16&&(t.windowBits=-t.windowBits,0===t.windowBits&&(t.windowBits=-15)),!(t.windowBits>=0&&t.windowBits<16)||e&&e.windowBits||(t.windowBits+=32),t.windowBits>15&&t.windowBits<48&&!(15&t.windowBits)&&(t.windowBits|=15),this.err=0,this.msg=\"\",this.ended=!1,this.chunks=[],this.strm=new ne,this.strm.avail_out=0;var i=Y(this.strm,t.windowBits);if(i!==le)throw new Error(ae[i]);if(this.header=new re,W(this.strm,this.header),t.dictionary&&(\"string\"==typeof t.dictionary?t.dictionary=function(e){if(\"function\"==typeof TextEncoder&&TextEncoder.prototype.encode)return(new TextEncoder).encode(e);var t,i,a,n,r,o=e.length,s=0;for(n=0;n<o;n++)55296==(64512&(i=e.charCodeAt(n)))&&n+1<o&&56320==(64512&(a=e.charCodeAt(n+1)))&&(i=65536+(i-55296<<10)+(a-56320),n++),s+=i<128?1:i<2048?2:i<65536?3:4;for(t=new Uint8Array(s),r=0,n=0;r<s;n++)55296==(64512&(i=e.charCodeAt(n)))&&n+1<o&&56320==(64512&(a=e.charCodeAt(n+1)))&&(i=65536+(i-55296<<10)+(a-56320),n++),i<128?t[r++]=i:i<2048?(t[r++]=192|i>>>6,t[r++]=128|63&i):i<65536?(t[r++]=224|i>>>12,t[r++]=128|i>>>6&63,t[r++]=128|63&i):(t[r++]=240|i>>>18,t[r++]=128|i>>>12&63,t[r++]=128|i>>>6&63,t[r++]=128|63&i);return t}(t.dictionary):\"[object ArrayBuffer]\"===oe.call(t.dictionary)&&(t.dictionary=new Uint8Array(t.dictionary)),t.raw&&(i=q(this.strm,t.dictionary))!==le))throw new Error(ae[i])}function me(e,t){var i=new be(t);if(i.push(e),i.err)throw i.msg||ae[i.err];return i.result}be.prototype.push=function(e,t){var i,a,n,r=this.strm,o=this.options.chunkSize,s=this.options.dictionary;if(this.ended)return!1;for(a=t===~~t?t:!0===t?de:se,\"[object ArrayBuffer]\"===oe.call(e)?r.input=new Uint8Array(e):r.input=e,r.next_in=0,r.avail_in=r.input.length;;){for(0===r.avail_out&&(r.output=new Uint8Array(o),r.next_out=0,r.avail_out=o),(i=X(r,a))===he&&s&&((i=q(r,s))===le?i=X(r,a):i===ue&&(i=he));r.avail_in>0&&i===fe&&r.state.wrap>0&&0!==e[r.next_in];)K(r),i=X(r,a);switch(i){case ce:case ue:case he:case we:return this.onEnd(i),this.ended=!0,!1}if(n=r.avail_out,r.next_out&&(0===r.avail_out||i===fe))if(\"string\"===this.options.to){var d=ie(r.output,r.next_out),l=r.next_out-d,f=te(r.output,d);r.next_out=l,r.avail_out=o-l,l&&r.output.set(r.output.subarray(d,d+l),0),this.onData(f)}else this.onData(r.output.length===r.next_out?r.output:r.output.subarray(0,r.next_out));if(i!==le||0!==n){if(i===fe)return i=G(this.strm),this.onEnd(i),this.ended=!0,!0;if(0===r.avail_in)break}}return!0},be.prototype.onData=function(e){this.chunks.push(e)},be.prototype.onEnd=function(e){e===le&&(\"string\"===this.options.to?this.result=this.chunks.join(\"\"):this.result=function(e){for(var t=0,i=0,a=e.length;i<a;i++)t+=e[i].length;for(var n=new Uint8Array(t),r=0,o=0,s=e.length;r<s;r++){var d=e[r];n.set(d,o),o+=d.length}return n}(this.chunks)),this.chunks=[],this.err=e,this.msg=this.strm.msg};var ke=be,_e=me,ge=function(e,t){return(t=t||{}).raw=!0,me(e,t)},ve=me,pe=h,ye={Inflate:ke,inflate:_e,inflateRaw:ge,ungzip:ve,constants:pe};e.Inflate=ke,e.constants=pe,e.default=ye,e.inflate=_e,e.inflateRaw=ge,e.ungzip=ve,Object.defineProperty(e,\"__esModule\",{value:!0})}),this.addEventListener(\"message\",function(e){try{const t=pako.inflate(e.data.buffer);this.postMessage({buffer:t,name:e.data.name,type:e.data.type},[t.buffer])}catch(t){this.postMessage({error:t.message||String(t),name:e.data.name,type:e.data.type})}});"], { "type": "text/javascript" })
));

Util.$unZlibWorker.onerror = (event) =>
{
    console.error("[N2F] ZlibInflateWorker crashed:", event.message);
    Util.$saveProgress.end();
};

/**
 * @description Decode large buffer in chunks using TextDecoder
 * @param {Uint8Array} buffer
 * @return {string}
 * @method
 * @public
 */
Util.$decodeBufferChunked = function(buffer)
{
    const CHUNK_SIZE = 10 * 1024 * 1024; // 10MB chunks
    const totalChunks = Math.ceil(buffer.byteLength / CHUNK_SIZE);
    
    console.log(`[N2F] Decoding ${(buffer.byteLength / (1024 * 1024)).toFixed(2)}MB buffer in ${totalChunks} chunks...`);
    
    const decoder = new TextDecoder();
    const chunks = []; // Use array instead of string concatenation
    
    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, buffer.byteLength);
        const chunk = buffer.subarray(start, end);
        
        try {
            // Use stream: true for all but last chunk to handle multi-byte characters
            const isLastChunk = (i === totalChunks - 1);
            chunks.push(decoder.decode(chunk, { stream: !isLastChunk }));
            
            if ((i + 1) % 10 === 0) {
                console.log(`[N2F] Decoded ${i + 1}/${totalChunks} chunks (${Math.round((i + 1) / totalChunks * 100)}%)`);
            }
        } catch (e) {
            console.error(`[N2F] Chunk ${i} decode failed:`, e);
            console.error(`[N2F] Current chunks array length: ${chunks.length}, total size: ~${(chunks.join('').length / (1024 * 1024)).toFixed(2)}MB`);
            throw e;
        }
    }
    
    console.log(`[N2F] All chunks decoded, joining into single string...`);
    try {
        const result = chunks.join('');
        console.log(`[N2F] Buffer decode complete: ${(result.length / (1024 * 1024)).toFixed(2)}MB string`);
        return result;
    } catch (e) {
        console.error(`[N2F] Failed to join chunks into string:`, e);
        console.error(`[N2F] This file (${(buffer.byteLength / (1024 * 1024)).toFixed(0)}MB) exceeds browser string length limit (~500-1000MB)`);
        
        const errorMsg = 
            `FILE TOO LARGE FOR BROWSER\n\n` +
            `This file (${(buffer.byteLength / (1024 * 1024)).toFixed(0)}MB uncompressed) exceeds browser's maximum string length (~500-1000MB).\n\n` +
            `JavaScript cannot create strings larger than this limit.\n\n` +
            `Solutions:\n` +
            `• Split the SWF into multiple smaller files before conversion\n` +
            `• Remove unused assets/libraries from the SWF\n` +
            `• Use a different tool for files this large\n\n` +
            `This is a hard browser limitation, not a bug in the tool.`;
        
        alert(errorMsg);
        throw new Error(`File exceeds browser string length limit`);
    }
};

/**
 * @description Decode URI component in chunks for very large strings
 * @param {string} str
 * @return {string}
 * @method
 * @public
 */
Util.$decodeURIComponentChunked = function(str)
{
    const CHUNK_SIZE = 10 * 1024 * 1024; // 10MB chunks
    const totalChunks = Math.ceil(str.length / CHUNK_SIZE);
    
    if (totalChunks === 1) {
        return decodeURIComponent(str);
    }
    
    console.log(`[N2F] Decoding in ${totalChunks} chunks...`);
    let result = "";
    
    for (let i = 0; i < totalChunks; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, str.length);
        const chunk = str.substring(start, end);
        
        try {
            result += decodeURIComponent(chunk);
        } catch (e) {
            console.warn(`[N2F] Chunk ${i} decode failed, using raw chunk`);
            result += chunk;
        }
    }
    
    return result;
};

/**
 * @description Load large N2D workspace progressively to avoid UI freezing
 * @param {string} json
 * @param {string} name
 * @return {void}
 * @method
 * @public
 */

/**
 * @description Pre-validate library entries before loading.
 *              Logs detailed diagnostics for any entries that would fail.
 * @param {Array} libraries
 * @param {string} source - calling context for log messages
 * @private
 */
Util._$validateLibraries = function(libraries, source)
{
    if (!Array.isArray(libraries)) {
        console.error(`[N2F][${source}] libraries is not an array:`, typeof libraries);
        return;
    }
    let badCount = 0;
    for (let i = 0; i < libraries.length; i++) {
        const lib = libraries[i];
        if (!lib) {
            console.error(`[N2F][${source}] Library[${i}] is null/undefined`);
            badCount++;
            continue;
        }
        if (typeof lib !== 'object') {
            console.error(`[N2F][${source}] Library[${i}] is not an object: ${typeof lib}`);
            badCount++;
            continue;
        }
        if (typeof lib.id === 'undefined' || lib.id === null) {
            console.error(`[N2F][${source}] Library[${i}] MISSING id! type=${lib.type}, name=${lib.name}, keys=${Object.keys(lib).join(',')}`);
            // Log raw data (truncated for large entries)
            const raw = JSON.stringify(lib);
            console.error(`[N2F][${source}] Library[${i}] raw data (first 500 chars): ${raw.substring(0, 500)}`);
            badCount++;
        }
        if (!lib.type) {
            console.error(`[N2F][${source}] Library[${i}] MISSING type! id=${lib.id}, name=${lib.name}`);
            badCount++;
        }
    }
    if (badCount > 0) {
        console.error(`[N2F][${source}] ${badCount} invalid libraries out of ${libraries.length} total`);
    } else {
        console.log(`[N2F][${source}] All ${libraries.length} libraries pre-validated OK`);
    }
};

Util.$loadWorkSpaceProgressively = async function(json, name)
{
    console.time("[N2F] Progressive JSON.parse");
    
    try {
        // Parse the JSON (this is still the bottleneck, but we time it separately)
        const object = JSON.parse(json);
        console.timeEnd("[N2F] Progressive JSON.parse");
        
        console.log(`[N2F] Parsed object with ${object.libraries ? object.libraries.length : 0} libraries`);
        
        // Pre-validate libraries before loading
        Util._$validateLibraries(object.libraries, 'Progressive(JSON)');

        // Create workspace without libraries
        const workSpaces = new WorkSpace();
        workSpaces.name = name;
        
        // Load metadata first (fast)
        console.time("[N2F] Load metadata");
        workSpaces._$characterId = object.characterId | 0;
        workSpaces._$name = object.name;
        workSpaces._$stage = new Stage(object.stage);
        
        if (object.plugins) {
            for (let idx = 0; idx < object.plugins.length; ++idx) {
                const plugin = object.plugins[idx];
                workSpaces._$plugins.set(plugin.name, plugin);
            }
        }
        
        if (object.setting) {
            workSpaces._$timelineHeight = object.setting.timelineHeight;
            workSpaces._$controllerWidth = object.setting.controllerWidth;
            workSpaces._$ruler = !!object.setting.ruler;
            workSpaces._$rulerX = object.setting.rulerX || [];
            workSpaces._$rulerY = object.setting.rulerY || [];
        }
        console.timeEnd("[N2F] Load metadata");
        
        // Add workspace to array early so UI can show something
        Util.$workSpaces.push(workSpaces);
        Util.$screenTab.createElement(workSpaces, Util.$workSpaces.length - 1);
        Util.$screenTab.activeTab({
            "currentTarget": {
                "dataset": {
                    "tabId": Util.$workSpaces.length - 1
                }
            }
        });
        
        // Load libraries in chunks to avoid blocking UI and memory issues
        const libraries = object.libraries || [];
        
        // Use smaller chunks for very large files to reduce memory pressure
        let CHUNK_SIZE = 50;
        let DELAY_MS = 0;
        if (libraries.length > 3000) {
            CHUNK_SIZE = 25; // Smaller chunks for huge files
            DELAY_MS = 10; // Give GC more time between chunks
            console.log(`[N2F] Large file detected (${libraries.length} libraries), using conservative loading...`);
        }
        
        const totalChunks = Math.ceil(libraries.length / CHUNK_SIZE);
        
        console.log(`[N2F] Loading ${libraries.length} libraries in ${totalChunks} chunks (${CHUNK_SIZE} per chunk)...`);
        console.time("[N2F] Load all libraries");
        
        let loadErrors = 0;
        for (let chunkIdx = 0; chunkIdx < totalChunks; chunkIdx++) {
            const start = chunkIdx * CHUNK_SIZE;
            const end = Math.min(start + CHUNK_SIZE, libraries.length);
            
            // Process chunk with delay to allow UI updates and GC
            await new Promise(resolve => setTimeout(resolve, DELAY_MS));
            
            // Load this chunk of libraries
            for (let idx = start; idx < end; idx++) {
                const libData = libraries[idx];
                try {
                    if (!libData || typeof libData.id === 'undefined' || libData.id === null) {
                        console.error(`[N2F] Library[${idx}] has no id! type=${libData ? libData.type : 'null'}, keys=${libData ? Object.keys(libData).join(',') : 'N/A'}`);
                        loadErrors++;
                        continue;
                    }
                    workSpaces.addLibrary(libData);
                } catch (libErr) {
                    loadErrors++;
                    console.error(`[N2F] addLibrary FAILED at index ${idx}: ${libErr.message}`);
                    console.error(`[N2F]   id=${libData ? libData.id : '?'}, type=${libData ? libData.type : '?'}, name=${libData ? libData.name : '?'}`);
                    console.error(`[N2F]   keys: ${libData ? Object.keys(libData).join(', ') : 'N/A'}`);
                    try { console.error(`[N2F]   raw:`, JSON.stringify(libData).substring(0, 500)); } catch(e) {}
                }
            }
            
            // Update progress
            const progress = Math.round((end / libraries.length) * 100);
            console.log(`[N2F] Loaded ${end}/${libraries.length} libraries (${progress}%)`);
        }
        
        if (loadErrors > 0) {
            console.warn(`[N2F] ${loadErrors} libraries failed to load (skipped)`);
        }
        console.timeEnd("[N2F] Load all libraries");
        console.log("[N2F] Progressive loading complete!");;
        
        // Re-initialize UI now that libraries are loaded
        console.log("[N2F] Refreshing UI with loaded libraries...");
        try {
            workSpaces.initialize(workSpaces.root);
            console.log("[N2F] UI refresh complete!");
        } catch (e) {
            console.warn("[N2F] Scene rendering failed (common with complex graphics):", e.message);
            console.log("[N2F] Setting up UI manually (skipping scene rendering)...");
            
            // Manually set up UI components without triggering scene rendering
            try {
                // Set scene directly without triggering setter/initialize
                workSpaces._$scene = workSpaces.root;
                
                // Clear active library
                Util.$libraryController.clearActive();
                
                // Reload library panel with all libraries
                Util.$libraryController.reload(
                    Array.from(workSpaces._$libraries.values())
                );
                
                // Initialize javascript controller
                Util.$javascriptController.reload();
                
                // Initialize plugins
                Util.$pluginController.reload(
                    Array.from(workSpaces._$plugins.values())
                );
                
                // Set up timeline WITHOUT rendering
                Util.$sceneChange.reload();
                
                console.log("[N2F] UI setup complete! Library panel and timeline are now populated.");
                console.log("[N2F] Note: Stage preview may not render due to complex graphics.");
            } catch (uiError) {
                console.error("[N2F] UI setup failed:", uiError);
            }
        }
        
        // Clear the libraries array to free memory (do this AFTER initialize)
        object.libraries = null;
        
        // Initialize the workspace
        Util.$saveProgress.end();
        
    } catch (e) {
        console.error("[N2F] Progressive loading failed:", e);
        console.error("[N2F] Error stack:", e.stack);
        throw e;
    }
};

/**
 * @description Load large N2D workspace progressively from object (MessagePack path - no JSON.parse needed!)
 * @param {object} object - Already parsed object
 * @param {string} name
 * @return {void}
 * @method
 * @public
 */
Util.$loadWorkSpaceProgressivelyFromObject = async function(object, name)
{
    console.log(`[N2F] Progressive loading from object with ${object.libraries ? object.libraries.length : 0} libraries`);
    
    // Pre-validate libraries before loading
    Util._$validateLibraries(object.libraries, 'Progressive(Object)');

    try {
        // Create workspace without libraries
        const workSpaces = new WorkSpace();
        workSpaces.name = name;
        
        // Load metadata first (fast)
        console.time("[N2F] Load metadata");
        workSpaces._$characterId = object.characterId | 0;
        workSpaces._$name = object.name;
        workSpaces._$stage = new Stage(object.stage);
        
        if (object.plugins) {
            for (let idx = 0; idx < object.plugins.length; ++idx) {
                const plugin = object.plugins[idx];
                workSpaces._$plugins.set(plugin.name, plugin);
            }
        }
        
        if (object.setting) {
            workSpaces._$timelineHeight = object.setting.timelineHeight;
            workSpaces._$controllerWidth = object.setting.controllerWidth;
            workSpaces._$ruler = !!object.setting.ruler;
            workSpaces._$rulerX = object.setting.rulerX || [];
            workSpaces._$rulerY = object.setting.rulerY || [];
        }
        console.timeEnd("[N2F] Load metadata");
        
        // Add workspace to array early so UI can show something
        Util.$workSpaces.push(workSpaces);
        Util.$screenTab.createElement(workSpaces, Util.$workSpaces.length - 1);
        Util.$screenTab.activeTab({
            "currentTarget": {
                "dataset": {
                    "tabId": Util.$workSpaces.length - 1
                }
            }
        });
        
        // Load libraries in chunks to avoid blocking UI and memory issues
        const libraries = object.libraries || [];
        
        // Use smaller chunks for very large files to reduce memory pressure
        let CHUNK_SIZE = 50;
        let DELAY_MS = 0;
        if (libraries.length > 3000) {
            CHUNK_SIZE = 25; // Smaller chunks for huge files
            DELAY_MS = 10; // Give GC more time between chunks
            console.log(`[N2F] Large file detected (${libraries.length} libraries), using conservative loading...`);
        }
        
        const totalChunks = Math.ceil(libraries.length / CHUNK_SIZE);
        
        console.log(`[N2F] Loading ${libraries.length} libraries in ${totalChunks} chunks (${CHUNK_SIZE} per chunk)...`);
        console.time("[N2F] Load all libraries");
        
        let loadErrors = 0;
        for (let chunkIdx = 0; chunkIdx < totalChunks; chunkIdx++) {
            const start = chunkIdx * CHUNK_SIZE;
            const end = Math.min(start + CHUNK_SIZE, libraries.length);
            
            // Process chunk with delay to allow UI updates and GC
            await new Promise(resolve => setTimeout(resolve, DELAY_MS));
            
            // Load this chunk of libraries
            for (let idx = start; idx < end; idx++) {
                const libData = libraries[idx];
                try {
                    if (!libData || typeof libData.id === 'undefined' || libData.id === null) {
                        console.error(`[N2F] Library[${idx}] has no id! type=${libData ? libData.type : 'null'}, keys=${libData ? Object.keys(libData).join(',') : 'N/A'}`);
                        loadErrors++;
                        continue;
                    }
                    workSpaces.addLibrary(libData);
                } catch (libErr) {
                    loadErrors++;
                    console.error(`[N2F] addLibrary FAILED at index ${idx}: ${libErr.message}`);
                    console.error(`[N2F]   id=${libData ? libData.id : '?'}, type=${libData ? libData.type : '?'}, name=${libData ? libData.name : '?'}`);
                    console.error(`[N2F]   keys: ${libData ? Object.keys(libData).join(', ') : 'N/A'}`);
                    try { console.error(`[N2F]   raw:`, JSON.stringify(libData).substring(0, 500)); } catch(e) {}
                }
            }
            
            // Update progress
            const progress = Math.round((end / libraries.length) * 100);
            console.log(`[N2F] Loaded ${end}/${libraries.length} libraries (${progress}%)`);
        }
        
        if (loadErrors > 0) {
            console.warn(`[N2F] ${loadErrors} libraries failed to load (skipped)`);
        }
        console.timeEnd("[N2F] Load all libraries");
        console.log("[N2F] Progressive loading complete!");
        
        // Re-initialize UI now that libraries are loaded
        console.log("[N2F] Refreshing UI with loaded libraries...");
        try {
            workSpaces.initialize(workSpaces.root);
            console.log("[N2F] UI refresh complete!");
        } catch (e) {
            console.warn("[N2F] Scene rendering failed (common with complex graphics):", e.message);
            console.log("[N2F] Setting up UI manually (skipping scene rendering)...");
            
            // Manually set up UI components without triggering scene rendering
            try {
                // Set scene directly without triggering setter/initialize
                workSpaces._$scene = workSpaces.root;
                
                // Clear active library
                Util.$libraryController.clearActive();
                
                // Reload library panel with all libraries
                Util.$libraryController.reload(
                    Array.from(workSpaces._$libraries.values())
                );
                
                // Initialize javascript controller
                Util.$javascriptController.reload();
                
                // Initialize plugins
                Util.$pluginController.reload(
                    Array.from(workSpaces._$plugins.values())
                );
                
                // Set up timeline WITHOUT rendering
                Util.$sceneChange.reload();
                
                console.log("[N2F] UI setup complete! Library panel and timeline are now populated.");
                console.log("[N2F] Note: Stage preview may not render due to complex graphics.");
            } catch (uiError) {
                console.error("[N2F] UI setup failed:", uiError);
            }
        }
        
        // Clear the libraries array to free memory (do this AFTER initialize)
        object.libraries = null;
        
        // Initialize the workspace
        Util.$saveProgress.end();
        
    } catch (e) {
        console.error("[N2F] Progressive loading from object failed:", e);
        console.error("[N2F] Error stack:", e.stack);
        throw e;
    }
};

/**
 * @param {MessageEvent} event
 * @public
 */
Util.$unZlibWorker.onmessage = (event) =>
{
    if (event.data.error) {
        console.error("[N2F] ZlibInflateWorker error:", event.data.error);
        Util.$saveProgress.end();
        return;
    }

    try {

        // Check decompressed size before processing
        const sizeInMB = event.data.buffer.byteLength / (1024 * 1024);
        console.log(`[N2F] Decompressed size: ${sizeInMB.toFixed(2)} MB`);
        console.log(`[N2F] Buffer details: byteLength=${event.data.buffer.byteLength}, type=${event.data.buffer.constructor.name}`);

        // Warn if file is very large (may cause performance issues)
        if (sizeInMB > 300) {
            console.warn(`[N2F] Large file detected (${sizeInMB.toFixed(0)}MB). This may take a while...`);
            if (sizeInMB > 500) {
                const proceed = confirm(
                    `WARNING: File is extremely large (${sizeInMB.toFixed(0)}MB).\n\n` +
                    `This may cause browser slowdown or crash.\n\n` +
                    `Recommendations:\n` +
                    `• Split the SWF into smaller files before conversion\n` +
                    `• Remove unused library items\n` +
                    `• Close other browser tabs\n\n` +
                    `Continue loading?`
                );
                if (!proceed) {
                    console.log("[N2F] User cancelled large file load");
                    Util.$saveProgress.end();
                    return;
                }
            }
        }

        console.time("[N2F] TextDecoder.decode");
        let json;
        try {
            // For buffers >100MB, TextDecoder can fail or return empty string
            // Use chunked decoding for large buffers
            if (event.data.buffer.byteLength > 100 * 1024 * 1024) {
                console.log("[N2F] Using chunked TextDecoder for large buffer...");
                json = Util.$decodeBufferChunked(event.data.buffer);
            } else {
                json = new TextDecoder().decode(event.data.buffer);
            }
        } catch (e) {
            console.error("[N2F] TextDecoder failed:", e);
            alert("Failed to decode file: " + e.message);
            Util.$saveProgress.end();
            return;
        }
        console.timeEnd("[N2F] TextDecoder.decode");
        console.log(`[N2F] Decoded string length: ${(json.length / (1024 * 1024)).toFixed(2)} MB (${json.length} chars)`);
        
        // Validate TextDecoder output
        if (!json || json.length === 0) {
            console.error("[N2F] TextDecoder returned empty string!");
            alert("File decode failed: TextDecoder returned empty result. File may be corrupted or too large for browser.");
            Util.$saveProgress.end();
            return;
        }

        if (event.data.type === "n2d") {

            Util.$saveProgress.loadN2D();

            console.time("[N2F] decodeURIComponent");
            let decodedJson;
            try {
                // Check if string is actually URL-encoded (contains % characters)
                const hasEncoding = json.includes('%');
                console.log(`[N2F] String appears ${hasEncoding ? '' : 'NOT '}to be URL-encoded`);
                
                if (!hasEncoding) {
                    // Not URL-encoded, use as-is
                    console.log("[N2F] Skipping decodeURIComponent (no encoding detected)");
                    decodedJson = json;
                } else if (json.length > 100 * 1024 * 1024) {
                    // For very large strings (>100MB), decodeURIComponent can fail silently
                    // Try chunked decoding for large files
                    console.log("[N2F] Using chunked URI decoding for large string...");
                    decodedJson = Util.$decodeURIComponentChunked(json);
                } else {
                    decodedJson = decodeURIComponent(json);
                }
                
                // Validate result
                if (!decodedJson || decodedJson.length === 0) {
                    console.warn("[N2F] decodeURIComponent returned empty, using raw string");
                    decodedJson = json;
                }
            } catch (e) {
                console.error("[N2F] decodeURIComponent failed:", e.message);
                console.log("[N2F] Using raw decoded string instead");
                decodedJson = json;
            }
            console.timeEnd("[N2F] decodeURIComponent");
            console.log(`[N2F] Final JSON length: ${(decodedJson.length / (1024 * 1024)).toFixed(2)} MB`);

            // For large files, use progressive/chunked loading
            if (sizeInMB > 300) {
                console.log("[N2F] Using progressive loading for large file...");
                Util.$loadWorkSpaceProgressively(decodedJson, event.data.name);
            } else {
                console.time("[N2F] WorkSpace constructor");
                const workSpaces = new WorkSpace(decodedJson);
                console.timeEnd("[N2F] WorkSpace constructor");

                workSpaces.name = event.data.name;

                Util
                    .$workSpaces
                    .push(workSpaces);

                Util
                    .$screenTab
                    .createElement(workSpaces, Util.$workSpaces.length - 1);

                Util
                    .$screenTab
                    .activeTab({
                        "currentTarget": {
                            "dataset": {
                                "tabId": Util.$workSpaces.length - 1
                            }
                        }
                    });

                Util.$saveProgress.end();
            }

        } else {

            Util.$saveProgress.loadJson();

            const values = JSON.parse(decodeURIComponent(json));

            for (let idx = 0; idx < values.length; ++idx) {
                Util.$workSpaces.push(new WorkSpace(values[idx]));
            }

            if (!Util.$workSpaces.length) {
                Util.$workSpaces.push(new WorkSpace());
            }

            // タブセット
            Util.$screenTab.run();

            // end
            Util.$initializeEnd();

        }

    } catch (e) {
        console.error("[N2F] Failed to process inflated data:", e);
        console.error("[N2F] Error stack:", e.stack);
        
        // Provide helpful error message based on error type
        let errorMsg = "Failed to load file: " + e.message;
        if (e.name === "RangeError" || e.message.includes("memory")) {
            errorMsg = "File too large for browser memory. Try:\n" +
                      "• Split SWF into smaller parts\n" +
                      "• Remove unused assets\n" +
                      "• Use a 64-bit browser with more RAM";
        } else if (e instanceof SyntaxError) {
            errorMsg = "File data corrupted or invalid JSON format";
        }
        
        alert(errorMsg);
        Util.$saveProgress.end();
    }
};

// ZLIB Deflate Worker
Util.$zlibWorker = new Worker(URL.createObjectURL(
    new Blob(["/*! pako 2.1.0 https://github.com/nodeca/pako @license (MIT AND Zlib) */!function(t,e){\"object\"==typeof exports&&\"undefined\"!=typeof module?e(exports):\"function\"==typeof define&&define.amd?define([\"exports\"],e):e((t=\"undefined\"!=typeof globalThis?globalThis:t||self).pako={})}(this,function(t){\"use strict\";function e(t){for(var e=t.length;--e>=0;)t[e]=0}var a=new Uint8Array([0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0]),n=new Uint8Array([0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13]),r=new Uint8Array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7]),i=new Uint8Array([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]),s=new Array(576);e(s);var _=new Array(60);e(_);var h=new Array(512);e(h);var o=new Array(256);e(o);var l=new Array(29);e(l);var d,u,f,c=new Array(30);function p(t,e,a,n,r){this.static_tree=t,this.extra_bits=e,this.extra_base=a,this.elems=n,this.max_length=r,this.has_stree=t&&t.length}function g(t,e){this.dyn_tree=t,this.max_code=0,this.stat_desc=e}e(c);var w=function(t){return t<256?h[t]:h[256+(t>>>7)]},m=function(t,e){t.pending_buf[t.pending++]=255&e,t.pending_buf[t.pending++]=e>>>8&255},b=function(t,e,a){t.bi_valid>16-a?(t.bi_buf|=e<<t.bi_valid&65535,m(t,t.bi_buf),t.bi_buf=e>>16-t.bi_valid,t.bi_valid+=a-16):(t.bi_buf|=e<<t.bi_valid&65535,t.bi_valid+=a)},v=function(t,e,a){b(t,a[2*e],a[2*e+1])},y=function(t,e){var a=0;do{a|=1&t,t>>>=1,a<<=1}while(--e>0);return a>>>1},z=function(t,e,a){var n,r,i=new Array(16),s=0;for(n=1;n<=15;n++)s=s+a[n-1]<<1,i[n]=s;for(r=0;r<=e;r++){var _=t[2*r+1];0!==_&&(t[2*r]=y(i[_]++,_))}},k=function(t){var e;for(e=0;e<286;e++)t.dyn_ltree[2*e]=0;for(e=0;e<30;e++)t.dyn_dtree[2*e]=0;for(e=0;e<19;e++)t.bl_tree[2*e]=0;t.dyn_ltree[512]=1,t.opt_len=t.static_len=0,t.sym_next=t.matches=0},x=function(t){t.bi_valid>8?m(t,t.bi_buf):t.bi_valid>0&&(t.pending_buf[t.pending++]=t.bi_buf),t.bi_buf=0,t.bi_valid=0},A=function(t,e,a,n){var r=2*e,i=2*a;return t[r]<t[i]||t[r]===t[i]&&n[e]<=n[a]},E=function(t,e,a){for(var n=t.heap[a],r=a<<1;r<=t.heap_len&&(r<t.heap_len&&A(e,t.heap[r+1],t.heap[r],t.depth)&&r++,!A(e,n,t.heap[r],t.depth));)t.heap[a]=t.heap[r],a=r,r<<=1;t.heap[a]=n},Z=function(t,e,r){var i,s,_,h,d=0;if(0!==t.sym_next)do{i=255&t.pending_buf[t.sym_buf+d++],i+=(255&t.pending_buf[t.sym_buf+d++])<<8,s=t.pending_buf[t.sym_buf+d++],0===i?v(t,s,e):(_=o[s],v(t,_+256+1,e),0!==(h=a[_])&&(s-=l[_],b(t,s,h)),i--,_=w(i),v(t,_,r),0!==(h=n[_])&&(i-=c[_],b(t,i,h)))}while(d<t.sym_next);v(t,256,e)},U=function(t,e){var a,n,r,i=e.dyn_tree,s=e.stat_desc.static_tree,_=e.stat_desc.has_stree,h=e.stat_desc.elems,o=-1;for(t.heap_len=0,t.heap_max=573,a=0;a<h;a++)0!==i[2*a]?(t.heap[++t.heap_len]=o=a,t.depth[a]=0):i[2*a+1]=0;for(;t.heap_len<2;)i[2*(r=t.heap[++t.heap_len]=o<2?++o:0)]=1,t.depth[r]=0,t.opt_len--,_&&(t.static_len-=s[2*r+1]);for(e.max_code=o,a=t.heap_len>>1;a>=1;a--)E(t,i,a);r=h;do{a=t.heap[1],t.heap[1]=t.heap[t.heap_len--],E(t,i,1),n=t.heap[1],t.heap[--t.heap_max]=a,t.heap[--t.heap_max]=n,i[2*r]=i[2*a]+i[2*n],t.depth[r]=(t.depth[a]>=t.depth[n]?t.depth[a]:t.depth[n])+1,i[2*a+1]=i[2*n+1]=r,t.heap[1]=r++,E(t,i,1)}while(t.heap_len>=2);t.heap[--t.heap_max]=t.heap[1],function(t,e){var a,n,r,i,s,_,h=e.dyn_tree,o=e.max_code,l=e.stat_desc.static_tree,d=e.stat_desc.has_stree,u=e.stat_desc.extra_bits,f=e.stat_desc.extra_base,c=e.stat_desc.max_length,p=0;for(i=0;i<=15;i++)t.bl_count[i]=0;for(h[2*t.heap[t.heap_max]+1]=0,a=t.heap_max+1;a<573;a++)(i=h[2*h[2*(n=t.heap[a])+1]+1]+1)>c&&(i=c,p++),h[2*n+1]=i,n>o||(t.bl_count[i]++,s=0,n>=f&&(s=u[n-f]),_=h[2*n],t.opt_len+=_*(i+s),d&&(t.static_len+=_*(l[2*n+1]+s)));if(0!==p){do{for(i=c-1;0===t.bl_count[i];)i--;t.bl_count[i]--,t.bl_count[i+1]+=2,t.bl_count[c]--,p-=2}while(p>0);for(i=c;0!==i;i--)for(n=t.bl_count[i];0!==n;)(r=t.heap[--a])>o||(h[2*r+1]!==i&&(t.opt_len+=(i-h[2*r+1])*h[2*r],h[2*r+1]=i),n--)}}(t,e),z(i,o,t.bl_count)},R=function(t,e,a){var n,r,i=-1,s=e[1],_=0,h=7,o=4;for(0===s&&(h=138,o=3),e[2*(a+1)+1]=65535,n=0;n<=a;n++)r=s,s=e[2*(n+1)+1],++_<h&&r===s||(_<o?t.bl_tree[2*r]+=_:0!==r?(r!==i&&t.bl_tree[2*r]++,t.bl_tree[32]++):_<=10?t.bl_tree[34]++:t.bl_tree[36]++,_=0,i=r,0===s?(h=138,o=3):r===s?(h=6,o=3):(h=7,o=4))},S=function(t,e,a){var n,r,i=-1,s=e[1],_=0,h=7,o=4;for(0===s&&(h=138,o=3),n=0;n<=a;n++)if(r=s,s=e[2*(n+1)+1],!(++_<h&&r===s)){if(_<o)do{v(t,r,t.bl_tree)}while(0!=--_);else 0!==r?(r!==i&&(v(t,r,t.bl_tree),_--),v(t,16,t.bl_tree),b(t,_-3,2)):_<=10?(v(t,17,t.bl_tree),b(t,_-3,3)):(v(t,18,t.bl_tree),b(t,_-11,7));_=0,i=r,0===s?(h=138,o=3):r===s?(h=6,o=3):(h=7,o=4)}},L=!1,O=function(t,e,a,n){b(t,0+(n?1:0),3),x(t),m(t,a),m(t,~a),a&&t.pending_buf.set(t.window.subarray(e,e+a),t.pending),t.pending+=a},T=function(t){L||(function(){var t,e,i,g,w,m=new Array(16);for(i=0,g=0;g<28;g++)for(l[g]=i,t=0;t<1<<a[g];t++)o[i++]=g;for(o[i-1]=g,w=0,g=0;g<16;g++)for(c[g]=w,t=0;t<1<<n[g];t++)h[w++]=g;for(w>>=7;g<30;g++)for(c[g]=w<<7,t=0;t<1<<n[g]-7;t++)h[256+w++]=g;for(e=0;e<=15;e++)m[e]=0;for(t=0;t<=143;)s[2*t+1]=8,t++,m[8]++;for(;t<=255;)s[2*t+1]=9,t++,m[9]++;for(;t<=279;)s[2*t+1]=7,t++,m[7]++;for(;t<=287;)s[2*t+1]=8,t++,m[8]++;for(z(s,287,m),t=0;t<30;t++)_[2*t+1]=5,_[2*t]=y(t,5);d=new p(s,a,257,286,15),u=new p(_,n,0,30,15),f=new p(new Array(0),r,0,19,7)}(),L=!0),t.l_desc=new g(t.dyn_ltree,d),t.d_desc=new g(t.dyn_dtree,u),t.bl_desc=new g(t.bl_tree,f),t.bi_buf=0,t.bi_valid=0,k(t)},F=O,N=function(t,e,a,n){var r,h,o=0;t.level>0?(2===t.strm.data_type&&(t.strm.data_type=function(t){var e,a=4093624447;for(e=0;e<=31;e++,a>>>=1)if(1&a&&0!==t.dyn_ltree[2*e])return 0;if(0!==t.dyn_ltree[18]||0!==t.dyn_ltree[20]||0!==t.dyn_ltree[26])return 1;for(e=32;e<256;e++)if(0!==t.dyn_ltree[2*e])return 1;return 0}(t)),U(t,t.l_desc),U(t,t.d_desc),o=function(t){var e;for(R(t,t.dyn_ltree,t.l_desc.max_code),R(t,t.dyn_dtree,t.d_desc.max_code),U(t,t.bl_desc),e=18;e>=3&&0===t.bl_tree[2*i[e]+1];e--);return t.opt_len+=3*(e+1)+5+5+4,e}(t),r=t.opt_len+3+7>>>3,(h=t.static_len+3+7>>>3)<=r&&(r=h)):r=h=a+5,a+4<=r&&-1!==e?O(t,e,a,n):4===t.strategy||h===r?(b(t,2+(n?1:0),3),Z(t,s,_)):(b(t,4+(n?1:0),3),function(t,e,a,n){var r;for(b(t,e-257,5),b(t,a-1,5),b(t,n-4,4),r=0;r<n;r++)b(t,t.bl_tree[2*i[r]+1],3);S(t,t.dyn_ltree,e-1),S(t,t.dyn_dtree,a-1)}(t,t.l_desc.max_code+1,t.d_desc.max_code+1,o+1),Z(t,t.dyn_ltree,t.dyn_dtree)),k(t),n&&x(t)},D=function(t,e,a){return t.pending_buf[t.sym_buf+t.sym_next++]=e,t.pending_buf[t.sym_buf+t.sym_next++]=e>>8,t.pending_buf[t.sym_buf+t.sym_next++]=a,0===e?t.dyn_ltree[2*a]++:(t.matches++,e--,t.dyn_ltree[2*(o[a]+256+1)]++,t.dyn_dtree[2*w(e)]++),t.sym_next===t.sym_end},C=function(t){b(t,2,3),v(t,256,s),function(t){16===t.bi_valid?(m(t,t.bi_buf),t.bi_buf=0,t.bi_valid=0):t.bi_valid>=8&&(t.pending_buf[t.pending++]=255&t.bi_buf,t.bi_buf>>=8,t.bi_valid-=8)}(t)},I=function(t,e,a,n){for(var r=65535&t,i=t>>>16&65535,s=0;0!==a;){a-=s=a>2e3?2e3:a;do{i=i+(r=r+e[n++]|0)|0}while(--s);r%=65521,i%=65521}return r|i<<16},B=new Uint32Array(function(){for(var t,e=[],a=0;a<256;a++){t=a;for(var n=0;n<8;n++)t=1&t?3988292384^t>>>1:t>>>1;e[a]=t}return e}()),M=function(t,e,a,n){var r=B,i=n+a;t^=-1;for(var s=n;s<i;s++)t=t>>>8^r[255&(t^e[s])];return-1^t},H={2:\"need dictionary\",1:\"stream end\",0:\"\",\"-1\":\"file error\",\"-2\":\"stream error\",\"-3\":\"data error\",\"-4\":\"insufficient memory\",\"-5\":\"buffer error\",\"-6\":\"incompatible version\"},j={Z_NO_FLUSH:0,Z_PARTIAL_FLUSH:1,Z_SYNC_FLUSH:2,Z_FULL_FLUSH:3,Z_FINISH:4,Z_BLOCK:5,Z_TREES:6,Z_OK:0,Z_STREAM_END:1,Z_NEED_DICT:2,Z_ERRNO:-1,Z_STREAM_ERROR:-2,Z_DATA_ERROR:-3,Z_MEM_ERROR:-4,Z_BUF_ERROR:-5,Z_NO_COMPRESSION:0,Z_BEST_SPEED:1,Z_BEST_COMPRESSION:9,Z_DEFAULT_COMPRESSION:-1,Z_FILTERED:1,Z_HUFFMAN_ONLY:2,Z_RLE:3,Z_FIXED:4,Z_DEFAULT_STRATEGY:0,Z_BINARY:0,Z_TEXT:1,Z_UNKNOWN:2,Z_DEFLATED:8},P=T,K=F,Y=N,X=D,G=C,W=j.Z_NO_FLUSH,J=j.Z_PARTIAL_FLUSH,q=j.Z_FULL_FLUSH,Q=j.Z_FINISH,V=j.Z_BLOCK,$=j.Z_OK,tt=j.Z_STREAM_END,et=j.Z_STREAM_ERROR,at=j.Z_DATA_ERROR,nt=j.Z_BUF_ERROR,rt=j.Z_DEFAULT_COMPRESSION,it=j.Z_FILTERED,st=j.Z_HUFFMAN_ONLY,_t=j.Z_RLE,ht=j.Z_FIXED,ot=j.Z_UNKNOWN,lt=j.Z_DEFLATED,dt=258,ut=262,ft=42,ct=113,pt=666,gt=function(t,e){return t.msg=H[e],e},wt=function(t){return 2*t-(t>4?9:0)},mt=function(t){for(var e=t.length;--e>=0;)t[e]=0},bt=function(t){var e,a,n,r=t.w_size;n=e=t.hash_size;do{a=t.head[--n],t.head[n]=a>=r?a-r:0}while(--e);n=e=r;do{a=t.prev[--n],t.prev[n]=a>=r?a-r:0}while(--e)},vt=function(t,e,a){return(e<<t.hash_shift^a)&t.hash_mask},yt=function(t){var e=t.state,a=e.pending;a>t.avail_out&&(a=t.avail_out),0!==a&&(t.output.set(e.pending_buf.subarray(e.pending_out,e.pending_out+a),t.next_out),t.next_out+=a,e.pending_out+=a,t.total_out+=a,t.avail_out-=a,e.pending-=a,0===e.pending&&(e.pending_out=0))},zt=function(t,e){Y(t,t.block_start>=0?t.block_start:-1,t.strstart-t.block_start,e),t.block_start=t.strstart,yt(t.strm)},kt=function(t,e){t.pending_buf[t.pending++]=e},xt=function(t,e){t.pending_buf[t.pending++]=e>>>8&255,t.pending_buf[t.pending++]=255&e},At=function(t,e,a,n){var r=t.avail_in;return r>n&&(r=n),0===r?0:(t.avail_in-=r,e.set(t.input.subarray(t.next_in,t.next_in+r),a),1===t.state.wrap?t.adler=I(t.adler,e,r,a):2===t.state.wrap&&(t.adler=M(t.adler,e,r,a)),t.next_in+=r,t.total_in+=r,r)},Et=function(t,e){var a,n,r=t.max_chain_length,i=t.strstart,s=t.prev_length,_=t.nice_match,h=t.strstart>t.w_size-ut?t.strstart-(t.w_size-ut):0,o=t.window,l=t.w_mask,d=t.prev,u=t.strstart+dt,f=o[i+s-1],c=o[i+s];t.prev_length>=t.good_match&&(r>>=2),_>t.lookahead&&(_=t.lookahead);do{if(o[(a=e)+s]===c&&o[a+s-1]===f&&o[a]===o[i]&&o[++a]===o[i+1]){i+=2,a++;do{}while(o[++i]===o[++a]&&o[++i]===o[++a]&&o[++i]===o[++a]&&o[++i]===o[++a]&&o[++i]===o[++a]&&o[++i]===o[++a]&&o[++i]===o[++a]&&o[++i]===o[++a]&&i<u);if(n=dt-(u-i),i=u-dt,n>s){if(t.match_start=e,s=n,n>=_)break;f=o[i+s-1],c=o[i+s]}}}while((e=d[e&l])>h&&0!=--r);return s<=t.lookahead?s:t.lookahead},Zt=function(t){var e,a,n,r=t.w_size;do{if(a=t.window_size-t.lookahead-t.strstart,t.strstart>=r+(r-ut)&&(t.window.set(t.window.subarray(r,r+r-a),0),t.match_start-=r,t.strstart-=r,t.block_start-=r,t.insert>t.strstart&&(t.insert=t.strstart),bt(t),a+=r),0===t.strm.avail_in)break;if(e=At(t.strm,t.window,t.strstart+t.lookahead,a),t.lookahead+=e,t.lookahead+t.insert>=3)for(n=t.strstart-t.insert,t.ins_h=t.window[n],t.ins_h=vt(t,t.ins_h,t.window[n+1]);t.insert&&(t.ins_h=vt(t,t.ins_h,t.window[n+3-1]),t.prev[n&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=n,n++,t.insert--,!(t.lookahead+t.insert<3)););}while(t.lookahead<ut&&0!==t.strm.avail_in)},Ut=function(t,e){var a,n,r,i=t.pending_buf_size-5>t.w_size?t.w_size:t.pending_buf_size-5,s=0,_=t.strm.avail_in;do{if(a=65535,r=t.bi_valid+42>>3,t.strm.avail_out<r)break;if(r=t.strm.avail_out-r,a>(n=t.strstart-t.block_start)+t.strm.avail_in&&(a=n+t.strm.avail_in),a>r&&(a=r),a<i&&(0===a&&e!==Q||e===W||a!==n+t.strm.avail_in))break;s=e===Q&&a===n+t.strm.avail_in?1:0,K(t,0,0,s),t.pending_buf[t.pending-4]=a,t.pending_buf[t.pending-3]=a>>8,t.pending_buf[t.pending-2]=~a,t.pending_buf[t.pending-1]=~a>>8,yt(t.strm),n&&(n>a&&(n=a),t.strm.output.set(t.window.subarray(t.block_start,t.block_start+n),t.strm.next_out),t.strm.next_out+=n,t.strm.avail_out-=n,t.strm.total_out+=n,t.block_start+=n,a-=n),a&&(At(t.strm,t.strm.output,t.strm.next_out,a),t.strm.next_out+=a,t.strm.avail_out-=a,t.strm.total_out+=a)}while(0===s);return(_-=t.strm.avail_in)&&(_>=t.w_size?(t.matches=2,t.window.set(t.strm.input.subarray(t.strm.next_in-t.w_size,t.strm.next_in),0),t.strstart=t.w_size,t.insert=t.strstart):(t.window_size-t.strstart<=_&&(t.strstart-=t.w_size,t.window.set(t.window.subarray(t.w_size,t.w_size+t.strstart),0),t.matches<2&&t.matches++,t.insert>t.strstart&&(t.insert=t.strstart)),t.window.set(t.strm.input.subarray(t.strm.next_in-_,t.strm.next_in),t.strstart),t.strstart+=_,t.insert+=_>t.w_size-t.insert?t.w_size-t.insert:_),t.block_start=t.strstart),t.high_water<t.strstart&&(t.high_water=t.strstart),s?4:e!==W&&e!==Q&&0===t.strm.avail_in&&t.strstart===t.block_start?2:(r=t.window_size-t.strstart,t.strm.avail_in>r&&t.block_start>=t.w_size&&(t.block_start-=t.w_size,t.strstart-=t.w_size,t.window.set(t.window.subarray(t.w_size,t.w_size+t.strstart),0),t.matches<2&&t.matches++,r+=t.w_size,t.insert>t.strstart&&(t.insert=t.strstart)),r>t.strm.avail_in&&(r=t.strm.avail_in),r&&(At(t.strm,t.window,t.strstart,r),t.strstart+=r,t.insert+=r>t.w_size-t.insert?t.w_size-t.insert:r),t.high_water<t.strstart&&(t.high_water=t.strstart),r=t.bi_valid+42>>3,i=(r=t.pending_buf_size-r>65535?65535:t.pending_buf_size-r)>t.w_size?t.w_size:r,((n=t.strstart-t.block_start)>=i||(n||e===Q)&&e!==W&&0===t.strm.avail_in&&n<=r)&&(a=n>r?r:n,s=e===Q&&0===t.strm.avail_in&&a===n?1:0,K(t,t.block_start,a,s),t.block_start+=a,yt(t.strm)),s?3:1)},Rt=function(t,e){for(var a,n;;){if(t.lookahead<ut){if(Zt(t),t.lookahead<ut&&e===W)return 1;if(0===t.lookahead)break}if(a=0,t.lookahead>=3&&(t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart),0!==a&&t.strstart-a<=t.w_size-ut&&(t.match_length=Et(t,a)),t.match_length>=3)if(n=X(t,t.strstart-t.match_start,t.match_length-3),t.lookahead-=t.match_length,t.match_length<=t.max_lazy_match&&t.lookahead>=3){t.match_length--;do{t.strstart++,t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart}while(0!=--t.match_length);t.strstart++}else t.strstart+=t.match_length,t.match_length=0,t.ins_h=t.window[t.strstart],t.ins_h=vt(t,t.ins_h,t.window[t.strstart+1]);else n=X(t,0,t.window[t.strstart]),t.lookahead--,t.strstart++;if(n&&(zt(t,!1),0===t.strm.avail_out))return 1}return t.insert=t.strstart<2?t.strstart:2,e===Q?(zt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(zt(t,!1),0===t.strm.avail_out)?1:2},St=function(t,e){for(var a,n,r;;){if(t.lookahead<ut){if(Zt(t),t.lookahead<ut&&e===W)return 1;if(0===t.lookahead)break}if(a=0,t.lookahead>=3&&(t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart),t.prev_length=t.match_length,t.prev_match=t.match_start,t.match_length=2,0!==a&&t.prev_length<t.max_lazy_match&&t.strstart-a<=t.w_size-ut&&(t.match_length=Et(t,a),t.match_length<=5&&(t.strategy===it||3===t.match_length&&t.strstart-t.match_start>4096)&&(t.match_length=2)),t.prev_length>=3&&t.match_length<=t.prev_length){r=t.strstart+t.lookahead-3,n=X(t,t.strstart-1-t.prev_match,t.prev_length-3),t.lookahead-=t.prev_length-1,t.prev_length-=2;do{++t.strstart<=r&&(t.ins_h=vt(t,t.ins_h,t.window[t.strstart+3-1]),a=t.prev[t.strstart&t.w_mask]=t.head[t.ins_h],t.head[t.ins_h]=t.strstart)}while(0!=--t.prev_length);if(t.match_available=0,t.match_length=2,t.strstart++,n&&(zt(t,!1),0===t.strm.avail_out))return 1}else if(t.match_available){if((n=X(t,0,t.window[t.strstart-1]))&&zt(t,!1),t.strstart++,t.lookahead--,0===t.strm.avail_out)return 1}else t.match_available=1,t.strstart++,t.lookahead--}return t.match_available&&(n=X(t,0,t.window[t.strstart-1]),t.match_available=0),t.insert=t.strstart<2?t.strstart:2,e===Q?(zt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(zt(t,!1),0===t.strm.avail_out)?1:2};function Lt(t,e,a,n,r){this.good_length=t,this.max_lazy=e,this.nice_length=a,this.max_chain=n,this.func=r}var Ot=[new Lt(0,0,0,0,Ut),new Lt(4,4,8,4,Rt),new Lt(4,5,16,8,Rt),new Lt(4,6,32,32,Rt),new Lt(4,4,16,16,St),new Lt(8,16,32,32,St),new Lt(8,16,128,128,St),new Lt(8,32,128,256,St),new Lt(32,128,258,1024,St),new Lt(32,258,258,4096,St)];function Tt(){this.strm=null,this.status=0,this.pending_buf=null,this.pending_buf_size=0,this.pending_out=0,this.pending=0,this.wrap=0,this.gzhead=null,this.gzindex=0,this.method=lt,this.last_flush=-1,this.w_size=0,this.w_bits=0,this.w_mask=0,this.window=null,this.window_size=0,this.prev=null,this.head=null,this.ins_h=0,this.hash_size=0,this.hash_bits=0,this.hash_mask=0,this.hash_shift=0,this.block_start=0,this.match_length=0,this.prev_match=0,this.match_available=0,this.strstart=0,this.match_start=0,this.lookahead=0,this.prev_length=0,this.max_chain_length=0,this.max_lazy_match=0,this.level=0,this.strategy=0,this.good_match=0,this.nice_match=0,this.dyn_ltree=new Uint16Array(1146),this.dyn_dtree=new Uint16Array(122),this.bl_tree=new Uint16Array(78),mt(this.dyn_ltree),mt(this.dyn_dtree),mt(this.bl_tree),this.l_desc=null,this.d_desc=null,this.bl_desc=null,this.bl_count=new Uint16Array(16),this.heap=new Uint16Array(573),mt(this.heap),this.heap_len=0,this.heap_max=0,this.depth=new Uint16Array(573),mt(this.depth),this.sym_buf=0,this.lit_bufsize=0,this.sym_next=0,this.sym_end=0,this.opt_len=0,this.static_len=0,this.matches=0,this.insert=0,this.bi_buf=0,this.bi_valid=0}var Ft=function(t){if(!t)return 1;var e=t.state;return!e||e.strm!==t||e.status!==ft&&57!==e.status&&69!==e.status&&73!==e.status&&91!==e.status&&103!==e.status&&e.status!==ct&&e.status!==pt?1:0},Nt=function(t){if(Ft(t))return gt(t,et);t.total_in=t.total_out=0,t.data_type=ot;var e=t.state;return e.pending=0,e.pending_out=0,e.wrap<0&&(e.wrap=-e.wrap),e.status=2===e.wrap?57:e.wrap?ft:ct,t.adler=2===e.wrap?0:1,e.last_flush=-2,P(e),$},Dt=function(t){var e,a=Nt(t);return a===$&&((e=t.state).window_size=2*e.w_size,mt(e.head),e.max_lazy_match=Ot[e.level].max_lazy,e.good_match=Ot[e.level].good_length,e.nice_match=Ot[e.level].nice_length,e.max_chain_length=Ot[e.level].max_chain,e.strstart=0,e.block_start=0,e.lookahead=0,e.insert=0,e.match_length=e.prev_length=2,e.match_available=0,e.ins_h=0),a},Ct=function(t,e,a,n,r,i){if(!t)return et;var s=1;if(e===rt&&(e=6),n<0?(s=0,n=-n):n>15&&(s=2,n-=16),r<1||r>9||a!==lt||n<8||n>15||e<0||e>9||i<0||i>ht||8===n&&1!==s)return gt(t,et);8===n&&(n=9);var _=new Tt;return t.state=_,_.strm=t,_.status=ft,_.wrap=s,_.gzhead=null,_.w_bits=n,_.w_size=1<<_.w_bits,_.w_mask=_.w_size-1,_.hash_bits=r+7,_.hash_size=1<<_.hash_bits,_.hash_mask=_.hash_size-1,_.hash_shift=~~((_.hash_bits+3-1)/3),_.window=new Uint8Array(2*_.w_size),_.head=new Uint16Array(_.hash_size),_.prev=new Uint16Array(_.w_size),_.lit_bufsize=1<<r+6,_.pending_buf_size=4*_.lit_bufsize,_.pending_buf=new Uint8Array(_.pending_buf_size),_.sym_buf=_.lit_bufsize,_.sym_end=3*(_.lit_bufsize-1),_.level=e,_.strategy=i,_.method=a,Dt(t)},It=Ct,Bt=function(t,e){return Ft(t)||2!==t.state.wrap?et:(t.state.gzhead=e,$)},Mt=function(t,e){if(Ft(t)||e>V||e<0)return t?gt(t,et):et;var a=t.state;if(!t.output||0!==t.avail_in&&!t.input||a.status===pt&&e!==Q)return gt(t,0===t.avail_out?nt:et);var n=a.last_flush;if(a.last_flush=e,0!==a.pending){if(yt(t),0===t.avail_out)return a.last_flush=-1,$}else if(0===t.avail_in&&wt(e)<=wt(n)&&e!==Q)return gt(t,nt);if(a.status===pt&&0!==t.avail_in)return gt(t,nt);if(a.status===ft&&0===a.wrap&&(a.status=ct),a.status===ft){var r=lt+(a.w_bits-8<<4)<<8;if(r|=(a.strategy>=st||a.level<2?0:a.level<6?1:6===a.level?2:3)<<6,0!==a.strstart&&(r|=32),xt(a,r+=31-r%31),0!==a.strstart&&(xt(a,t.adler>>>16),xt(a,65535&t.adler)),t.adler=1,a.status=ct,yt(t),0!==a.pending)return a.last_flush=-1,$}if(57===a.status)if(t.adler=0,kt(a,31),kt(a,139),kt(a,8),a.gzhead)kt(a,(a.gzhead.text?1:0)+(a.gzhead.hcrc?2:0)+(a.gzhead.extra?4:0)+(a.gzhead.name?8:0)+(a.gzhead.comment?16:0)),kt(a,255&a.gzhead.time),kt(a,a.gzhead.time>>8&255),kt(a,a.gzhead.time>>16&255),kt(a,a.gzhead.time>>24&255),kt(a,9===a.level?2:a.strategy>=st||a.level<2?4:0),kt(a,255&a.gzhead.os),a.gzhead.extra&&a.gzhead.extra.length&&(kt(a,255&a.gzhead.extra.length),kt(a,a.gzhead.extra.length>>8&255)),a.gzhead.hcrc&&(t.adler=M(t.adler,a.pending_buf,a.pending,0)),a.gzindex=0,a.status=69;else if(kt(a,0),kt(a,0),kt(a,0),kt(a,0),kt(a,0),kt(a,9===a.level?2:a.strategy>=st||a.level<2?4:0),kt(a,3),a.status=ct,yt(t),0!==a.pending)return a.last_flush=-1,$;if(69===a.status){if(a.gzhead.extra){for(var i=a.pending,s=(65535&a.gzhead.extra.length)-a.gzindex;a.pending+s>a.pending_buf_size;){var _=a.pending_buf_size-a.pending;if(a.pending_buf.set(a.gzhead.extra.subarray(a.gzindex,a.gzindex+_),a.pending),a.pending=a.pending_buf_size,a.gzhead.hcrc&&a.pending>i&&(t.adler=M(t.adler,a.pending_buf,a.pending-i,i)),a.gzindex+=_,yt(t),0!==a.pending)return a.last_flush=-1,$;i=0,s-=_}var h=new Uint8Array(a.gzhead.extra);a.pending_buf.set(h.subarray(a.gzindex,a.gzindex+s),a.pending),a.pending+=s,a.gzhead.hcrc&&a.pending>i&&(t.adler=M(t.adler,a.pending_buf,a.pending-i,i)),a.gzindex=0}a.status=73}if(73===a.status){if(a.gzhead.name){var o,l=a.pending;do{if(a.pending===a.pending_buf_size){if(a.gzhead.hcrc&&a.pending>l&&(t.adler=M(t.adler,a.pending_buf,a.pending-l,l)),yt(t),0!==a.pending)return a.last_flush=-1,$;l=0}o=a.gzindex<a.gzhead.name.length?255&a.gzhead.name.charCodeAt(a.gzindex++):0,kt(a,o)}while(0!==o);a.gzhead.hcrc&&a.pending>l&&(t.adler=M(t.adler,a.pending_buf,a.pending-l,l)),a.gzindex=0}a.status=91}if(91===a.status){if(a.gzhead.comment){var d,u=a.pending;do{if(a.pending===a.pending_buf_size){if(a.gzhead.hcrc&&a.pending>u&&(t.adler=M(t.adler,a.pending_buf,a.pending-u,u)),yt(t),0!==a.pending)return a.last_flush=-1,$;u=0}d=a.gzindex<a.gzhead.comment.length?255&a.gzhead.comment.charCodeAt(a.gzindex++):0,kt(a,d)}while(0!==d);a.gzhead.hcrc&&a.pending>u&&(t.adler=M(t.adler,a.pending_buf,a.pending-u,u))}a.status=103}if(103===a.status){if(a.gzhead.hcrc){if(a.pending+2>a.pending_buf_size&&(yt(t),0!==a.pending))return a.last_flush=-1,$;kt(a,255&t.adler),kt(a,t.adler>>8&255),t.adler=0}if(a.status=ct,yt(t),0!==a.pending)return a.last_flush=-1,$}if(0!==t.avail_in||0!==a.lookahead||e!==W&&a.status!==pt){var f=0===a.level?Ut(a,e):a.strategy===st?function(t,e){for(var a;;){if(0===t.lookahead&&(Zt(t),0===t.lookahead)){if(e===W)return 1;break}if(t.match_length=0,a=X(t,0,t.window[t.strstart]),t.lookahead--,t.strstart++,a&&(zt(t,!1),0===t.strm.avail_out))return 1}return t.insert=0,e===Q?(zt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(zt(t,!1),0===t.strm.avail_out)?1:2}(a,e):a.strategy===_t?function(t,e){for(var a,n,r,i,s=t.window;;){if(t.lookahead<=dt){if(Zt(t),t.lookahead<=dt&&e===W)return 1;if(0===t.lookahead)break}if(t.match_length=0,t.lookahead>=3&&t.strstart>0&&(n=s[r=t.strstart-1])===s[++r]&&n===s[++r]&&n===s[++r]){i=t.strstart+dt;do{}while(n===s[++r]&&n===s[++r]&&n===s[++r]&&n===s[++r]&&n===s[++r]&&n===s[++r]&&n===s[++r]&&n===s[++r]&&r<i);t.match_length=dt-(i-r),t.match_length>t.lookahead&&(t.match_length=t.lookahead)}if(t.match_length>=3?(a=X(t,1,t.match_length-3),t.lookahead-=t.match_length,t.strstart+=t.match_length,t.match_length=0):(a=X(t,0,t.window[t.strstart]),t.lookahead--,t.strstart++),a&&(zt(t,!1),0===t.strm.avail_out))return 1}return t.insert=0,e===Q?(zt(t,!0),0===t.strm.avail_out?3:4):t.sym_next&&(zt(t,!1),0===t.strm.avail_out)?1:2}(a,e):Ot[a.level].func(a,e);if(3!==f&&4!==f||(a.status=pt),1===f||3===f)return 0===t.avail_out&&(a.last_flush=-1),$;if(2===f&&(e===J?G(a):e!==V&&(K(a,0,0,!1),e===q&&(mt(a.head),0===a.lookahead&&(a.strstart=0,a.block_start=0,a.insert=0))),yt(t),0===t.avail_out))return a.last_flush=-1,$}return e!==Q?$:a.wrap<=0?tt:(2===a.wrap?(kt(a,255&t.adler),kt(a,t.adler>>8&255),kt(a,t.adler>>16&255),kt(a,t.adler>>24&255),kt(a,255&t.total_in),kt(a,t.total_in>>8&255),kt(a,t.total_in>>16&255),kt(a,t.total_in>>24&255)):(xt(a,t.adler>>>16),xt(a,65535&t.adler)),yt(t),a.wrap>0&&(a.wrap=-a.wrap),0!==a.pending?$:tt)},Ht=function(t){if(Ft(t))return et;var e=t.state.status;return t.state=null,e===ct?gt(t,at):$},jt=function(t,e){var a=e.length;if(Ft(t))return et;var n=t.state,r=n.wrap;if(2===r||1===r&&n.status!==ft||n.lookahead)return et;if(1===r&&(t.adler=I(t.adler,e,a,0)),n.wrap=0,a>=n.w_size){0===r&&(mt(n.head),n.strstart=0,n.block_start=0,n.insert=0);var i=new Uint8Array(n.w_size);i.set(e.subarray(a-n.w_size,a),0),e=i,a=n.w_size}var s=t.avail_in,_=t.next_in,h=t.input;for(t.avail_in=a,t.next_in=0,t.input=e,Zt(n);n.lookahead>=3;){var o=n.strstart,l=n.lookahead-2;do{n.ins_h=vt(n,n.ins_h,n.window[o+3-1]),n.prev[o&n.w_mask]=n.head[n.ins_h],n.head[n.ins_h]=o,o++}while(--l);n.strstart=o,n.lookahead=2,Zt(n)}return n.strstart+=n.lookahead,n.block_start=n.strstart,n.insert=n.lookahead,n.lookahead=0,n.match_length=n.prev_length=2,n.match_available=0,t.next_in=_,t.input=h,t.avail_in=s,n.wrap=r,$};function Pt(t){return Pt=\"function\"==typeof Symbol&&\"symbol\"==typeof Symbol.iterator?function(t){return typeof t}:function(t){return t&&\"function\"==typeof Symbol&&t.constructor===Symbol&&t!==Symbol.prototype?\"symbol\":typeof t},Pt(t)}var Kt=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)};try{String.fromCharCode.apply(null,new Uint8Array(1))}catch(t){}for(var Yt=new Uint8Array(256),Xt=0;Xt<256;Xt++)Yt[Xt]=Xt>=252?6:Xt>=248?5:Xt>=240?4:Xt>=224?3:Xt>=192?2:1;Yt[254]=Yt[254]=1;var Gt=function(t){if(\"function\"==typeof TextEncoder&&TextEncoder.prototype.encode)return(new TextEncoder).encode(t);var e,a,n,r,i,s=t.length,_=0;for(r=0;r<s;r++)55296==(64512&(a=t.charCodeAt(r)))&&r+1<s&&56320==(64512&(n=t.charCodeAt(r+1)))&&(a=65536+(a-55296<<10)+(n-56320),r++),_+=a<128?1:a<2048?2:a<65536?3:4;for(e=new Uint8Array(_),i=0,r=0;i<_;r++)55296==(64512&(a=t.charCodeAt(r)))&&r+1<s&&56320==(64512&(n=t.charCodeAt(r+1)))&&(a=65536+(a-55296<<10)+(n-56320),r++),a<128?e[i++]=a:a<2048?(e[i++]=192|a>>>6,e[i++]=128|63&a):a<65536?(e[i++]=224|a>>>12,e[i++]=128|a>>>6&63,e[i++]=128|63&a):(e[i++]=240|a>>>18,e[i++]=128|a>>>12&63,e[i++]=128|a>>>6&63,e[i++]=128|63&a);return e},Wt=function(){this.input=null,this.next_in=0,this.avail_in=0,this.total_in=0,this.output=null,this.next_out=0,this.avail_out=0,this.total_out=0,this.msg=\"\",this.state=null,this.data_type=2,this.adler=0},Jt=Object.prototype.toString,qt=j.Z_NO_FLUSH,Qt=j.Z_SYNC_FLUSH,Vt=j.Z_FULL_FLUSH,$t=j.Z_FINISH,te=j.Z_OK,ee=j.Z_STREAM_END,ae=j.Z_DEFAULT_COMPRESSION,ne=j.Z_DEFAULT_STRATEGY,re=j.Z_DEFLATED;function ie(t){this.options=function(t){for(var e=Array.prototype.slice.call(arguments,1);e.length;){var a=e.shift();if(a){if(\"object\"!==Pt(a))throw new TypeError(a+\"must be non-object\");for(var n in a)Kt(a,n)&&(t[n]=a[n])}}return t}({level:ae,method:re,chunkSize:16384,windowBits:15,memLevel:8,strategy:ne},t||{});var e=this.options;e.raw&&e.windowBits>0?e.windowBits=-e.windowBits:e.gzip&&e.windowBits>0&&e.windowBits<16&&(e.windowBits+=16),this.err=0,this.msg=\"\",this.ended=!1,this.chunks=[],this.strm=new Wt,this.strm.avail_out=0;var a=It(this.strm,e.level,e.method,e.windowBits,e.memLevel,e.strategy);if(a!==te)throw new Error(H[a]);if(e.header&&Bt(this.strm,e.header),e.dictionary){var n;if(n=\"string\"==typeof e.dictionary?Gt(e.dictionary):\"[object ArrayBuffer]\"===Jt.call(e.dictionary)?new Uint8Array(e.dictionary):e.dictionary,(a=jt(this.strm,n))!==te)throw new Error(H[a]);this._dict_set=!0}}function se(t,e){var a=new ie(e);if(a.push(t,!0),a.err)throw a.msg||H[a.err];return a.result}ie.prototype.push=function(t,e){var a,n,r=this.strm,i=this.options.chunkSize;if(this.ended)return!1;for(n=e===~~e?e:!0===e?$t:qt,\"string\"==typeof t?r.input=Gt(t):\"[object ArrayBuffer]\"===Jt.call(t)?r.input=new Uint8Array(t):r.input=t,r.next_in=0,r.avail_in=r.input.length;;)if(0===r.avail_out&&(r.output=new Uint8Array(i),r.next_out=0,r.avail_out=i),(n===Qt||n===Vt)&&r.avail_out<=6)this.onData(r.output.subarray(0,r.next_out)),r.avail_out=0;else{if((a=Mt(r,n))===ee)return r.next_out>0&&this.onData(r.output.subarray(0,r.next_out)),a=Ht(this.strm),this.onEnd(a),this.ended=!0,a===te;if(0!==r.avail_out){if(n>0&&r.next_out>0)this.onData(r.output.subarray(0,r.next_out)),r.avail_out=0;else if(0===r.avail_in)break}else this.onData(r.output)}return!0},ie.prototype.onData=function(t){this.chunks.push(t)},ie.prototype.onEnd=function(t){t===te&&(this.result=function(t){for(var e=0,a=0,n=t.length;a<n;a++)e+=t[a].length;for(var r=new Uint8Array(e),i=0,s=0,_=t.length;i<_;i++){var h=t[i];r.set(h,s),s+=h.length}return r}(this.chunks)),this.chunks=[],this.err=t,this.msg=this.strm.msg};var _e=ie,he=se,oe=function(t,e){return(e=e||{}).raw=!0,se(t,e)},le=function(t,e){return(e=e||{}).gzip=!0,se(t,e)},de=j,ue={Deflate:_e,deflate:he,deflateRaw:oe,gzip:le,constants:de};t.Deflate=_e,t.constants=de,t.default=ue,t.deflate=he,t.deflateRaw=oe,t.gzip=le,Object.defineProperty(t,\"__esModule\",{value:!0})}),this.addEventListener(\"message\",function(t){const e=encodeURIComponent(t.data.object),a=new Uint8Array(e.length);for(let t=0;t<e.length;++t)a[t]=e[t].charCodeAt(0);const n=t.data.type;if(\"json\"===n)this.postMessage({json:JSON.stringify({buffer:Array.from(pako.deflate(a)),type:\"zlib\"}),type:n});else{const t=pako.deflate(a);this.postMessage({buffer:t,type:n},[t.buffer])}});"], { "type": "text/javascript" })
));

/**
 * @param {MessageEvent} event
 * @public
 */
Util.$zlibWorker.onmessage = (event) =>
{
    const type = event.data.type;
    switch (type) {

        case "json":
        case "n2d":
            Util.$saveProgress.createFile();

            setTimeout(() =>
            {
                const anchor = document.getElementById("save-anchor");
                if (anchor.href) {
                    URL.revokeObjectURL(anchor.href);
                }

                anchor.download = `${Util.$currentWorkSpace().name}.${type}`;

                anchor.href = type === "json"
                    ? URL.createObjectURL(new Blob([event.data.json],   { "type" : "application/json" }))
                    : URL.createObjectURL(new Blob([event.data.buffer], { "type" : "text/plain" }));

                anchor.click();

                Util.$saveProgress.end();

            }, 200);
            break;

        case "local":
            {
                const buffer = event.data.buffer;

                new Promise((resolve) =>
                {
                    window.requestAnimationFrame(() =>
                    {
                        Util.$saveProgress.createBinary();

                        let binary = "";
                        for (let idx = 0; idx < buffer.length; idx += 4096) {
                            binary += String.fromCharCode.apply(
                                null, buffer.slice(idx, idx + 4096)
                            );
                        }

                        resolve(binary);
                    });
                })
                    .then((data) =>
                    {

                        Util.$saveProgress.launchDatabase(90);

                        const request = Util.$launchDB();

                        request.onsuccess = (event) =>
                        {
                            const db = event.target.result;
                            const transaction = db.transaction(
                                `${Util.DATABASE_NAME}`, "readwrite"
                            );

                            const store = transaction
                                .objectStore(`${Util.DATABASE_NAME}`);

                            store.put(data, Util.STORE_KEY);

                            transaction.oncomplete = (event) =>
                            {
                                event.target.db.close();
                                Util.$updated = false;
                                Util.$saveProgress.end();
                            };

                            Util.$saveProgress.commit();
                            transaction.commit();
                        };
                    });
            }

            break;

    }

    if (Util.$zlibQueues.length) {

        Util.$zlibWorker.postMessage(Util.$zlibQueues.pop());

    } else {

        Util.$zlibWorkerActive = false;

    }
};

Util.$zlibQueues       = [];
Util.$zlibWorkerActive = false;

// Unzip Worker
Util.$unzipURL = URL.createObjectURL(
    new Blob(["const Util={};Util.$Uint8Array=Uint8Array,Util.$Uint16Array=Uint16Array,Util.$Int16Array=Int16Array,Util.$ArrayBuffer=ArrayBuffer,Util.$max=Math.max,Util.$min=Math.min,Util.$potArrayBuffers=new Map,Util.$codeTables=[],Util.$getCodeTable=function(t,e){const i=Util.$codeTables.pop()||{key:null,value:null};return i.key=t,i.value=e,i},Util.$poolCodeTable=function(t){Util.$codeTables.push(t)},Util.$poolTypedArrayBuffer=function(t){const e=t.buffer,i=e.byteLength;if(!i||i!==Util.$upperPowerOfTwo(i))return;let r=Util.$potArrayBuffers.get(i);r||(r=[],Util.$potArrayBuffers.set(i,r)),r.push(e)},Util.$upperPowerOfTwo=function(t){return t--,t|=t>>1,t|=t>>2,t|=t>>4,t|=t>>8,t|=t>>16,++t},Util.$getUint8Array=function(t){let e;const i=Util.$upperPowerOfTwo(t),r=Util.$potArrayBuffers.get(i),l=r&&r.pop();return l?(e=new Util.$Uint8Array(l,0,t),e.fill(0)):e=new Util.$Uint8Array(new Util.$ArrayBuffer(i),0,t),e},Util.$getUint16Array=function(t){let e;const i=Util.$upperPowerOfTwo(2*t),r=Util.$potArrayBuffers.get(i),l=r&&r.pop();return l?(e=new Util.$Uint16Array(l,0,t),e.fill(0)):e=new Util.$Uint16Array(new Util.$ArrayBuffer(i),0,t),e},Util.$fixedDistTable={key:new Util.$Uint16Array([5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]),value:new Util.$Uint16Array([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31])},Util.$fixedLitTable={key:new Util.$Uint16Array([7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9,9]),value:new Util.$Uint16Array([256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,280,281,282,283,284,285,286,287,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255])},Util.$ORDER=new Util.$Uint8Array([16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]),Util.$LEXT=new Util.$Uint8Array([0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0,99,99]),Util.$LENS=new Util.$Int16Array([3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258,0,0]),Util.$DEXT=new Util.$Uint8Array([0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13]),Util.$DISTS=new Util.$Int16Array([1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577]);class ByteStream{constructor(){this.initialization()}initialization(){this.data=null,this.bit_offset=0,this.byte_offset=0,this.bit_buffer=null}byteAlign(){this.bit_offset&&(this.byte_offset=this.byte_offset+(this.bit_offset+7)/8|0,this.bit_offset=0)}getData(t){this.byteAlign();const e=this.byte_offset+t,i=this.data.slice(this.byte_offset,e);return this.byte_offset=e,i}setOffset(t,e){this.byte_offset=t,this.bit_offset=e}unzip(t,e=0){let i=e;const r=Util.$getUint8Array(19);let l=null,a=null;for(;;){const e=this.readUB(1),s=this.readUB(2);if(l&&(Util.$poolCodeTable(l),Util.$poolCodeTable(a)),l=null,a=null,s){if(1===s)l=Util.$fixedDistTable,a=Util.$fixedLitTable;else{const t=this.readUB(5)+257,e=this.readUB(5)+1,i=this.readUB(4)+4;for(let t=0;t<i;++t)r[Util.$ORDER[t]]=this.readUB(3);const s=this.buildHuffTable(r);r.fill(0);const f=t+e|0,o=Util.$getUint8Array(f);let n=0;for(let t=0;t<f;){const e=this.decodeSymbol(s.key,s.value);switch(e){case 0:case 1:case 2:case 3:case 4:case 5:case 6:case 7:case 8:case 9:case 10:case 11:case 12:case 13:case 14:case 15:o[t++]=e,n=e;break;case 16:{let e=this.readUB(2)+3|0;for(;e;)--e,o[t++]=n}break;case 17:{let e=this.readUB(3)+3|0;for(;e;)--e,o[t++]=0}break;case 18:{let e=this.readUB(7)+11|0;for(;e;)--e,o[t++]=0}}}Util.$poolCodeTable(s),l=this.buildHuffTable(o.subarray(t)),a=this.buildHuffTable(o.subarray(0,t)),Util.$poolTypedArrayBuffer(o),Util.$poolTypedArrayBuffer(s.key),Util.$poolTypedArrayBuffer(s.value)}for(;;){const e=0|this.decodeSymbol(a.key,a.value);if(256===e)break;if(e<256)t[i++]=e;else{const r=e-257|0;let a=Util.$LENS[r]+this.readUB(Util.$LEXT[r])|0;const s=this.decodeSymbol(l.key,l.value);let f=i-(Util.$DISTS[s]+this.readUB(Util.$DEXT[s])|0)|0;for(;a;)--a,t[i++]=t[f++]}}}else{this.bit_offset=8,this.bit_buffer=null;const e=0|this.readNumber(2);this.byte_offset+=2;for(let r=0;r<e;++r)t[i++]=this.readNumber(1)}if(e)break}Util.$poolTypedArrayBuffer(r)}buildHuffTable(t){const e=t.length,i=Util.$max.apply(null,t),r=Util.$getUint8Array(i),l=Util.$getUint16Array(i+1);let a=0,s=0,f=e;for(;f;)s=t[--f],s&&++r[s];let o=0;for(let t=0;t<i;)a=a+r[t++]<<1,l[t]=a,o=Util.$max(o,a);const n=o+e,U=Util.$getUint16Array(n),u=Util.$getUint16Array(n);for(let i=0;i<e;++i)if(s=t[i],s){const t=l[s];U[t]=s,u[t]=i,l[s]=t+1|0}return Util.$poolTypedArrayBuffer(r),Util.$poolTypedArrayBuffer(l),Util.$getCodeTable(U,u)}decodeSymbol(t,e){let i=0,r=0;for(;;)if(i=i<<1|this.readUB(1),++r,t[i]===r)return e[i]}readUB(t){let e=0;for(let i=0;i<t;++i)8===this.bit_offset&&(this.bit_buffer=this.readNumber(1),this.bit_offset=0),e|=(this.bit_buffer&1<<this.bit_offset++?1:0)<<i;return e}readNumber(t){let e=0;const i=this.byte_offset;let r=i+t|0;for(;r>i;)e=e<<8|this.data[--r];return this.byte_offset+=t,e}}Util.$byteStream=new ByteStream,Util.$lossless=function(t,e,i,r,l,a){const s=new Util.$Uint8Array(e*i*4);if(3===r){const r=(e+3&-4)-e;let f=0;if(a){let a=4*l;for(let l=0;l<i;++l){for(let i=0;i<e;++i){const e=4*t[a++],i=t[e+3];if(0===i){s[f++]=0,s[f++]=0,s[f++]=0,s[f++]=0;continue}const r=t[e],l=t[e+1],o=t[e+2];255!==i?(s[f++]=255&Util.$min(r/i*255,255),s[f++]=255&Util.$min(l/i*255,255),s[f++]=255&Util.$min(o/i*255,255),s[f++]=i):(s[f++]=r,s[f++]=l,s[f++]=o,s[f++]=i)}a+=r}return s}let o=3*l;for(let l=0;l<i;++l){for(let i=0;i<e;++i){const e=3*t[o++];s[f++]=t[e],s[f++]=t[e+1],s[f++]=t[e+2],s[f++]=255}o+=r}return s}const f=e*i;if(a){for(let e=0;e<f;++e){const i=4*e,r=i,l=i+1,a=i+2,f=i+3,o=t[r];0!==o?255!==o?(s[r]=255&Util.$min(t[l]/o*255,255),s[l]=255&Util.$min(t[a]/o*255,255),s[a]=255&Util.$min(t[f]/o*255,255),s[f]=o):(s[r]=t[l],s[l]=t[a],s[a]=t[f],s[f]=o):(s[r]=0,s[l]=0,s[a]=0,s[f]=0)}return s}for(let e=0;e<f;++e){const i=4*e,r=i+1,l=i+2,a=i+3;s[i]=t[r],s[r]=t[l],s[l]=t[a],s[a]=255}return s},this.addEventListener(\"message\",function(t){const e=Util.$byteStream;switch(t.data.mode){case\"swf\":{e.data=t.data.buffer;const i=t.data.fileSize,r=new Util.$Uint8Array(i),l=e.getData(8);e.setOffset(10,8),r.set(l,0),e.unzip(r,8),this.postMessage({buffer:r,mode:t.data.mode},[r.buffer])}break;case\"lossless\":{const i=t.data,r=new Util.$Uint8Array(i.fileSize);e.data=t.data.buffer,e.setOffset(2,8),e.unzip(r,0);const l=Util.$lossless(r,i.width,i.height,i.format,i.tableSize,i.isAlpha);this.postMessage({buffer:l,mode:t.data.mode},[l.buffer])}break;case\"jpegAlpha\":{const i=t.data.width*t.data.height,r=new Util.$Uint8Array(i);e.data=t.data.alphaData,e.setOffset(2,8),e.unzip(r,0),t.data.alphaData=r,this.postMessage(t.data,[t.data.buffer.buffer,t.data.alphaData.buffer])}}Util.$byteStream.initialization()});"], { "type": "text/javascript" }
    ));
Util.$unzipWorker       = null;
Util.$unzipQueues       = [];
Util.$unzipWorkerActive = false;

/**
 * @return {IDBOpenDBRequest}
 * @static
 */
Util.$launchDB = () =>
{
    const request = indexedDB.open(
        `${Util.PREFIX}@${Util.DATABASE_NAME}`
    );

    request.onupgradeneeded = (event) =>
    {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(`${Util.DATABASE_NAME}`)) {
            db.createObjectStore(`${Util.DATABASE_NAME}`);
        }
    };

    return request;
};

/**
 * @param  {object} event
 * @return void
 * @static
 */
Util.$unzipHandler = function (event)
{
    const worker = event.target;

    // event end
    worker.onmessage = null;

    // setup
    switch (event.data.mode) {

        case "swf":
            this._$byteStream._$buffer = event.data.buffer;
            this.parseAndBuild();
            break;

        case "lossless":
            {
                const workSpace    = Util.$currentWorkSpace();
                const instance     = workSpace.getLibrary(this.libraryId);
                instance._$buffer  = event.data.buffer;
                instance._$command = null;
            }
            break;

        case "jpegAlpha":
            {
                const buffer    = event.data.buffer;
                const alphaData = event.data.alphaData;

                let index = 0;
                for (let idx = 0; idx < buffer.length; idx += 4) {
                    buffer[idx + 3] = alphaData[index++];
                }

                const workSpace    = Util.$currentWorkSpace();
                const instance     = workSpace.getLibrary(this.libraryId);
                instance._$buffer  = buffer;
                instance._$command = null;
            }
            break;

    }

    // next
    if (Util.$unzipQueues.length) {
        const object = Util.$unzipQueues.shift();
        worker.onmessage = Util.$unzipHandler.bind(object);
        switch (object.mode) {

            case "swf":
                {
                    const buffer = object._$byteStream._$buffer;
                    worker.postMessage({
                        "fileSize": object.fileSize,
                        "mode":     object.mode,
                        "buffer":   buffer
                    }, [buffer.buffer]);
                }
                break;

            case "lossless":
                worker.postMessage(object, [object.buffer.buffer]);
                break;

            case "jpegAlpha":
                worker.postMessage(object, [
                    object.buffer.buffer,
                    object.alphaData.buffer
                ]);
                break;

        }

    } else {

        Util.$unzipWorkerActive = false;

    }

};

Util.$unlzmaWorkerURL = URL.createObjectURL(
    new Blob(["const LZMA={init:function(e){const t=[];t.push(e[12],e[13],e[14],e[15],e[16],e[4],e[5],e[6],e[7]);let s=8;for(let e=5;e<9;++e){if(t[e]>=s){t[e]=t[e]-s|0;break}t[e]=256+t[e]-s|0,s=1}return t.push(0,0,0,0),e.set(t,4),e.subarray(4)},reverseDecode2:function(e,t,s,i){let r=1,o=0,d=0;for(;d<i;++d){const i=s.decodeBit(e,t+r);r=r<<1|i,o|=i<<d}return o},decompress:function(e,t){const s=new Decoder,i=s.decodeHeader(e),r=i.uncompressedSize;if(s.setProperties(i),!s.decodeBody(e,t,r))throw new Error(\"Error in lzma data stream\");return t}};class OutWindow{constructor(){this._buffer=null,this._stream=null,this._pos=0,this._streamPos=0,this._windowSize=0}create(e){this._buffer&&this._windowSize===e||(this._buffer=new Uint8Array(e)),this._windowSize=e}flush(){const e=this._pos-this._streamPos;e&&(this._stream.writeBytes(this._buffer,e),this._pos>=this._windowSize&&(this._pos=0),this._streamPos=this._pos)}releaseStream(){this.flush(),this._stream=null}setStream(e){this._stream=e}init(e=!1){e||(this._streamPos=0,this._pos=0)}copyBlock(e,t){let s=this._pos-e-1;for(s<0&&(s+=this._windowSize);t--;)s>=this._windowSize&&(s=0),this._buffer[this._pos++]=this._buffer[s++],this._pos>=this._windowSize&&this.flush()}putByte(e){this._buffer[this._pos++]=e,this._pos>=this._windowSize&&this.flush()}getByte(e){let t=this._pos-e-1;return t<0&&(t+=this._windowSize),this._buffer[t]}}class RangeDecoder{constructor(){this._stream=null,this._code=0,this._range=-1}setStream(e){this._stream=e}releaseStream(){this._stream=null}init(){let e=5;for(this._code=0,this._range=-1;e--;)this._code=this._code<<8|this._stream.readByte()}decodeDirectBits(e){let t=0,s=e;for(;s--;){this._range>>>=1;const e=this._code-this._range>>>31;this._code-=this._range&e-1,t=t<<1|1-e,4278190080&this._range||(this._code=this._code<<8|this._stream.readByte(),this._range<<=8)}return t}decodeBit(e,t){const s=e[t],i=(this._range>>>11)*s;return(2147483648^this._code)<(2147483648^i)?(this._range=i,e[t]+=2048-s>>>5,4278190080&this._range||(this._code=this._code<<8|this._stream.readByte(),this._range<<=8),0):(this._range-=i,this._code-=i,e[t]-=s>>>5,4278190080&this._range||(this._code=this._code<<8|this._stream.readByte(),this._range<<=8),1)}}class BitTreeDecoder{constructor(e){this._models=Array(1<<e).fill(1024),this._numBitLevels=e}decode(e){let t=1,s=this._numBitLevels;for(;s--;)t=t<<1|e.decodeBit(this._models,t);return t-(1<<this._numBitLevels)}reverseDecode(e){let t=1,s=0,i=0;for(;i<this._numBitLevels;++i){const r=e.decodeBit(this._models,t);t=t<<1|r,s|=r<<i}return s}}class LenDecoder{constructor(){this._choice=[1024,1024],this._lowCoder=[],this._midCoder=[],this._highCoder=new BitTreeDecoder(8),this._numPosStates=0}create(e){for(;this._numPosStates<e;++this._numPosStates)this._lowCoder[this._numPosStates]=new BitTreeDecoder(3),this._midCoder[this._numPosStates]=new BitTreeDecoder(3)}decode(e,t){return 0===e.decodeBit(this._choice,0)?this._lowCoder[t].decode(e):0===e.decodeBit(this._choice,1)?8+this._midCoder[t].decode(e):16+this._highCoder.decode(e)}}class Decoder2{constructor(){this._decoders=Array(768).fill(1024)}decodeNormal(e){let t=1;do{t=t<<1|e.decodeBit(this._decoders,t)}while(t<256);return 255&t}decodeWithMatchByte(e,t){let s=1;do{const i=t>>7&1;t<<=1;const r=e.decodeBit(this._decoders,(1+i<<8)+s);if(s=s<<1|r,i!==r){for(;s<256;)s=s<<1|e.decodeBit(this._decoders,s);break}}while(s<256);return 255&s}}class LiteralDecoder{create(e,t){if(this._coders&&this._numPrevBits===t&&this._numPosBits===e)return;this._numPosBits=e,this._posMask=(1<<e)-1,this._numPrevBits=t,this._coders=[];let s=1<<this._numPrevBits+this._numPosBits;for(;s--;)this._coders[s]=new Decoder2}getDecoder(e,t){return this._coders[((e&this._posMask)<<this._numPrevBits)+((255&t)>>>8-this._numPrevBits)]}}class Decoder{constructor(){this._outWindow=new OutWindow,this._rangeDecoder=new RangeDecoder,this._isMatchDecoders=Array(192).fill(1024),this._isRepDecoders=Array(12).fill(1024),this._isRepG0Decoders=Array(12).fill(1024),this._isRepG1Decoders=Array(12).fill(1024),this._isRepG2Decoders=Array(12).fill(1024),this._isRep0LongDecoders=Array(192).fill(1024),this._posDecoders=Array(114).fill(1024),this._posAlignDecoder=new BitTreeDecoder(4),this._lenDecoder=new LenDecoder,this._repLenDecoder=new LenDecoder,this._literalDecoder=new LiteralDecoder,this._dictionarySize=-1,this._dictionarySizeCheck=-1,this._posSlotDecoder=[new BitTreeDecoder(6),new BitTreeDecoder(6),new BitTreeDecoder(6),new BitTreeDecoder(6)]}setDictionarySize(e){return!(e<0)&&(this._dictionarySize!==e&&(this._dictionarySize=e,this._dictionarySizeCheck=Math.max(this._dictionarySize,1),this._outWindow.create(Math.max(this._dictionarySizeCheck,4096))),!0)}setLcLpPb(e,t,s){if(e>8||t>4||s>4)return!1;const i=1<<s;return this._literalDecoder.create(t,e),this._lenDecoder.create(i),this._repLenDecoder.create(i),this._posStateMask=i-1,!0}setProperties(e){if(!this.setLcLpPb(e.lc,e.lp,e.pb))throw Error(\"Incorrect stream properties\");if(!this.setDictionarySize(e.dictionarySize))throw Error(\"Invalid dictionary size\")}decodeHeader(e){if(e._$size<13)return!1;let t=e.readByte();const s=t%9;t=~~(t/9);const i=t%5,r=~~(t/5);let o=e.readByte();o|=e.readByte()<<8,o|=e.readByte()<<16,o+=16777216*e.readByte();let d=e.readByte();return d|=e.readByte()<<8,d|=e.readByte()<<16,d+=16777216*e.readByte(),e.readByte(),e.readByte(),e.readByte(),e.readByte(),{lc:s,lp:i,pb:r,dictionarySize:o,uncompressedSize:d}}decodeBody(e,t,s){let i,r,o=0,d=0,h=0,c=0,n=0,_=0,a=0;for(this._rangeDecoder.setStream(e),this._rangeDecoder.init(),this._outWindow.setStream(t),this._outWindow.init(!1);_<s;){const e=_&this._posStateMask;if(0===this._rangeDecoder.decodeBit(this._isMatchDecoders,(o<<4)+e)){const e=this._literalDecoder.getDecoder(_++,a);a=o>=7?e.decodeWithMatchByte(this._rangeDecoder,this._outWindow.getByte(d)):e.decodeNormal(this._rangeDecoder),this._outWindow.putByte(a),o=o<4?0:o-(o<10?3:6)}else{if(1===this._rangeDecoder.decodeBit(this._isRepDecoders,o))i=0,0===this._rangeDecoder.decodeBit(this._isRepG0Decoders,o)?0===this._rangeDecoder.decodeBit(this._isRep0LongDecoders,(o<<4)+e)&&(o=o<7?9:11,i=1):(0===this._rangeDecoder.decodeBit(this._isRepG1Decoders,o)?r=h:(0===this._rangeDecoder.decodeBit(this._isRepG2Decoders,o)?r=c:(r=n,n=c),c=h),h=d,d=r),0===i&&(i=2+this._repLenDecoder.decode(this._rangeDecoder,e),o=o<7?8:11);else{n=c,c=h,h=d,i=2+this._lenDecoder.decode(this._rangeDecoder,e),o=o<7?7:10;const t=this._posSlotDecoder[i<=5?i-2:3].decode(this._rangeDecoder);if(t>=4){const e=(t>>1)-1;if(d=(2|1&t)<<e,t<14)d+=LZMA.reverseDecode2(this._posDecoders,d-t-1,this._rangeDecoder,e);else if(d+=this._rangeDecoder.decodeDirectBits(e-4)<<4,d+=this._posAlignDecoder.reverseDecode(this._rangeDecoder),d<0){if(-1===d)break;return!1}}else d=t}if(d>=_||d>=this._dictionarySizeCheck)return!1;this._outWindow.copyBlock(d,i),_+=i,a=this._outWindow.getByte(0)}}return this._outWindow.releaseStream(),this._rangeDecoder.releaseStream(),!0}}class InStream{constructor(e){this._$data=e,this._$size=e.length,this._$offset=0}readByte(){return this._$data[this._$offset++]}}class OutStream{constructor(e){this.size=8,this.buffers=e}writeBytes(e,t){e.length===t?this.buffers.set(e,this.size):this.buffers.set(e.subarray(0,t),this.size),this.size+=t}}this.addEventListener(\"message\",function(e){const t=e.data.fileSize,s=e.data.buffer,i=new Uint8Array(t+8);i.set(s.slice(0,8),0),LZMA.decompress(new InStream(LZMA.init(s)),new OutStream(i)),this.postMessage(i,[i.buffer]),this.close()});"], { "type": "text/javascript" })
);
Util.$unlzmaQueues       = [];
Util.$unlzmaWorkerActive = false;

Util.$parserURL = URL.createObjectURL(
    new Blob(["const Util={$tagObjects:[]};Util.$installed=new Map,Util.$swfParser=null,Util.$Rad2Deg=180/Math.PI,Util.$JCT11280=Function('var a=\"zKV33~jZ4zN=~ji36XazM93y!{~k2y!o~k0ZlW6zN?3Wz3W?{EKzK[33[`y|;-~j^YOTz$!~kNy|L1$353~jV3zKk3~k-4P4zK_2+~jY4y!xYHR~jlz$_~jk4z$e3X5He<0y!wy|X3[:~l|VU[F3VZ056Hy!nz/m1XD61+1XY1E1=1y|bzKiz!H034zKj~mEz#c5ZA3-3X$1~mBz$$3~lyz#,4YN5~mEz#{ZKZ3V%7Y}!J3X-YEX_J(3~mAz =V;kE0/y|F3y!}~m>z/U~mI~j_2+~mA~jp2;~m@~k32;~m>V}2u~mEX#2x~mBy+x2242(~mBy,;2242(~may->2&XkG2;~mIy-_2&NXd2;~mGz,{4<6:.:B*B:XC4>6:.>B*BBXSA+A:X]E&E<~r#z+625z s2+zN=`HXI@YMXIAXZYUM8X4K/:Q!Z&33 3YWX[~mB`{zKt4z (zV/z 3zRw2%Wd39]S11z$PAXH5Xb;ZQWU1ZgWP%3~o@{Dgl#gd}T){Uo{y5_d{e@}C(} WU9|cB{w}bzvV|)[} H|zT}d||0~{]Q|(l{|x{iv{dw}(5}[Z|kuZ }cq{{y|ij}.I{idbof%cu^d}Rj^y|-M{ESYGYfYsZslS`?ZdYO__gLYRZ&fvb4oKfhSf^d<Yeasc1f&a=hnYG{QY{D`Bsa|u,}Dl|_Q{C%xK|Aq}C>|c#ryW=}eY{L+`)][YF_Ub^h4}[X|?r|u_ex}TL@YR]j{SrXgo*|Gv|rK}B#mu{R1}hs|dP{C7|^Qt3|@P{YVV |8&}#D}ef{e/{Rl|>Hni}R1{Z#{D[}CQlQ||E}[s{SG_+i8eplY[=[|ec[$YXn#`hcm}YR|{Ci(_[ql|?8p3]-}^t{wy}4la&pc|3e{Rp{LqiJ],] `kc(]@chYnrM`O^,ZLYhZB]ywyfGY~aex!_Qww{a!|)*lHrM{N+n&YYj~Z b c#e_[hZSon|rOt`}hBXa^i{lh|<0||r{KJ{kni)|x,|0auY{D!^Sce{w;|@S|cA}Xn{C1h${E]Z-XgZ*XPbp]^_qbH^e[`YM|a||+=]!Lc}]vdBc=j-YSZD]YmyYLYKZ9Z>Xcczc2{Yh}9Fc#Z.l{}(D{G{{mRhC|L3b#|xK[Bepj#ut`H[,{E9Yr}1b{[e]{ZFk7[ZYbZ0XL]}Ye[(`d}c!|*y`Dg=b;gR]Hm=hJho}R-[n}9;{N![7k_{UbmN]rf#pTe[x8}!Qcs_rs[m`|>N}^V})7{^r|/E}),}HH{OYe2{Skx)e<_.cj.cjoMhc^d}0uYZd!^J_@g,[[[?{i@][|3S}Yl3|!1|eZ|5IYw|1D}e7|Cv{OHbnx-`wvb[6[4} =g+k:{C:}ed{S]|2M]-}WZ|/q{LF|dYu^}Gs^c{Z=}h>|/i|{W]:|ip{N:|zt|S<{DH[p_tvD{N<[8Axo{X4a.^o^X>Yfa59`#ZBYgY~_t^9`jZHZn`>G[oajZ;X,i)Z.^~YJe ZiZF^{][[#Zt^|]Fjx]&_5dddW]P0C[-]}]d|y {C_jUql] |OpaA[Z{lp|rz}:Mu#]_Yf6{Ep?f5`$[6^D][^u[$[6^.Z8]]ePc2U/=]K^_+^M{q*|9tYuZ,s(dS{i=|bNbB{uG}0jZOa:[-]dYtu3]:]<{DJ_SZIqr_`l=Yt`gkTnXb3d@kiq0a`Z{|!B|}e}Ww{Sp,^Z|0>_Z}36|]A|-t}lt{R6pi|v8hPu#{C>YOZHYmg/Z4nicK[}hF_Bg|YRZ7c|crkzYZY}_iXcZ.|)U|L5{R~qi^Uga@Y[xb}&qdbd6h5|Btw[}c<{Ds53[Y7]?Z<|e0{L[ZK]mXKZ#Z2^tavf0`PE[OSOaP`4gi`qjdYMgys/?[nc,}EEb,eL]g[n{E_b/vcvgb.{kcwi`~v%|0:|iK{Jh_vf5lb}KL|(oi=LrzhhY_^@`zgf[~g)[J_0fk_V{T)}I_{D&_/d9W/|MU[)f$xW}?$xr4<{Lb{y4}&u{XJ|cm{Iu{jQ}CMkD{CX|7A}G~{kt)nB|d5|<-}WJ}@||d@|Iy}Ts|iL|/^|no|0;}L6{Pm]7}$zf:|r2}?C_k{R(}-w|`G{Gy[g]bVje=_0|PT{^Y^yjtT[[[l!Ye_`ZN]@[n_)j3nEgMa]YtYpZy].d-Y_cjb~Y~[nc~sCi3|zg}B0}do{O^{|$`_|D{}U&|0+{J3|8*]iayx{a{xJ_9|,c{Ee]QXlYb]$[%YMc*]w[aafe]aVYi[fZEii[xq2YQZHg]Y~h#|Y:thre^@^|_F^CbTbG_1^qf7{L-`VFx Zr|@EZ;gkZ@slgko`[e}T:{Cu^pddZ_`yav^Ea+[#ZBbSbO`elQfLui}.F|txYcbQ`XehcGe~fc^RlV{D_0ZAej[l&jShxG[ipB_=u:eU}3e8[=j|{D(}dO{Do[BYUZ0/]AYE]ALYhZcYlYP/^-^{Yt_1_-;YT`P4BZG=IOZ&]H[e]YYd[9^F[1YdZxZ?Z{Z<]Ba2[5Yb[0Z4l?]d_;_)a?YGEYiYv`_XmZs4ZjY^Zb]6gqGaX^9Y}dXZr[g|]Y}K aFZp^k^F]M`^{O1Ys]ZCgCv4|E>}8eb7}l`{L5[Z_faQ|c2}Fj}hw^#|Ng|B||w2|Sh{v+[G}aB|MY}A{|8o}X~{E8paZ:]i^Njq]new)`-Z>haounWhN}c#{DfZ|fK]KqGZ=:u|fqoqcv}2ssm}.r{]{nIfV{JW)[K|,Z{Uxc|]l_KdCb%]cfobya3`p}G^|LZiSC]U|(X|kBlVg[kNo({O:g:|-N|qT}9?{MBiL}Sq{`P|3a|u.{Uaq:{_o|^S}jX{Fob0`;|#y_@[V[K|cw[<_ }KU|0F}d3|et{Q7{LuZttsmf^kYZ`Af`}$x}U`|Ww}d]| >}K,r&|XI|*e{C/a-bmr1fId4[;b>tQ_:]hk{b-pMge]gfpo.|(w[jgV{EC1Z,YhaY^q,_G[c_g[J0YX]`[h^hYK^_Yib,` {i6vf@YM^hdOKZZn(jgZ>bzSDc^Z%[[o9[2=/YHZ(_/Gu_`*|8z{DUZxYt^vuvZjhi^lc&gUd4|<UiA`z]$b/Z?l}YI^jaHxe|;F}l${sQ}5g}hA|e4}?o{ih}Uz{C)jPe4]H^J[Eg[|AMZMlc}:,{iz}#*|gc{Iq|/:|zK{l&}#u|myd{{M&v~nV};L|(g|I]ogddb0xsd7^V})$uQ{HzazsgxtsO^l}F>ZB]r|{7{j@cU^{{CbiYoHlng]f+nQ[bkTn/}<-d9q {KXadZYo+n|l[|lc}V2{[a{S4Zam~Za^`{HH{xx_SvF|ak=c^[v^7_rYT`ld@]:_ub%[$[m](Shu}G2{E.ZU_L_R{tz`vj(f?^}hswz}GdZ}{S:h`aD|?W|`dgG|if{a8|J1{N,}-Ao3{H#{mfsP|[ bzn+}_Q{MT{u4kHcj_q`eZj[8o0jy{p7}C|[}l){MuYY{|Ff!Ykn3{rT|m,^R|,R}$~Ykgx{P!]>iXh6[l[/}Jgcg{JYZ.^qYfYIZl[gZ#Xj[Pc7YyZD^+Yt;4;`e8YyZVbQ7YzZxXja.7SYl[s]2^/Ha$[6ZGYrb%XiYdf2]H]kZkZ*ZQ[ZYS^HZXcCc%Z|[(bVZ]]:OJQ_DZCg<[,]%Zaa [g{C00HY[c%[ChyZ,Z_`PbXa+eh`^&jPi0a[ggvhlekL]w{Yp^v}[e{~;k%a&k^|nR_z_Qng}[E}*Wq:{k^{FJZpXRhmh3^p>de^=_7`|ZbaAZtdhZ?n4ZL]u`9ZNc3g%[6b=e.ZVfC[ZZ^^^hD{E(9c(kyZ=bb|Sq{k`|vmr>izlH[u|e`}49}Y%}FT{[z{Rk}Bz{TCc/lMiAqkf(m$hDc;qooi[}^o:c^|Qm}a_{mrZ(pA`,}<2sY| adf_%|}`}Y5U;}/4|D>|$X{jw{C<|F.hK|*A{MRZ8Zsm?imZm_?brYWZrYx`yVZc3a@f?aK^ojEd {bN}/3ZH]/$YZhm^&j 9|(S|b]mF}UI{q&aM]LcrZ5^.|[j`T_V_Gak}9J[ ZCZD|^h{N9{~&[6Zd{}B}2O|cv]K}3s}Uy|l,fihW{EG`j_QOp~Z$F^zexS`dcISfhZBXP|.vn|_HYQ|)9|cr]<`&Z6]m_(ZhPcSg>`Z]5`~1`0Xcb4k1{O!bz|CN_T{LR|a/gFcD|j<{Z._[f)mPc:1`WtIaT1cgYkZOaVZOYFrEe[}T$}Ch}mk{K-^@]fH{Hdi`c*Z&|Kt{if[C{Q;{xYB`dYIX:ZB[}]*[{{p9|4GYRh2ao{DS|V+[zd$`F[ZXKadb*A] Ys]Maif~a/Z2bmclb8{Jro_rz|x9cHojbZ{GzZx_)]:{wAayeDlx}<=`g{H1{l#}9i|)=|lP{Qq}.({La|!Y{i2EZfp=c*}Cc{EDvVB|;g}2t{W4av^Bn=]ri,|y?|3+}T*ckZ*{Ffr5e%|sB{lx^0]eZb]9[SgAjS_D|uHZx]dive[c.YPkcq/}db{EQh&hQ|eg}G!ljil|BO]X{Qr_GkGl~YiYWu=c3eb}29v3|D|}4i||.{Mv})V{SP1{FX}CZW6{cm|vO{pS|e#}A~|1i}81|Mw}es|5[}3w{C`h9aL]o{}p[G`>i%a1Z@`Ln2bD[$_h`}ZOjhdTrH{[j_:k~kv[Sdu]CtL}41{I |[[{]Zp$]XjxjHt_eThoa#h>sSt8|gK|TVi[Y{t=}Bs|b7Zpr%{gt|Yo{CS[/{iteva|cf^hgn}($_c^wmb^Wm+|55jrbF|{9^ q6{C&c+ZKdJkq_xOYqZYSYXYl`8]-cxZAq/b%b*_Vsa[/Ybjac/OaGZ4fza|a)gY{P?| I|Y |,pi1n7}9bm9ad|=d{aV|2@[(}B`d&|Uz}B}{`q|/H|!JkM{FU|CB|.{}Az}#P|lk}K{|2rk7{^8^?`/|k>|Ka{Sq}Gz}io{DxZh[yK_#}9<{TRdgc]`~Z>JYmYJ]|`!ZKZ]gUcx|^E[rZCd`f9oQ[NcD_$ZlZ;Zr}mX|=!|$6ZPZYtIo%fj}CpcN|B,{VDw~gb}@hZg`Q{LcmA[(bo`<|@$|o1|Ss}9Z_}tC|G`{F/|9nd}i=}V-{L8aaeST]daRbujh^xlpq8|}zs4bj[S`J|]?G{P#{rD{]I`OlH{Hm]VYuSYUbRc*6[j`8]pZ[bt_/^Jc*[<Z?YE|Xb|?_Z^Vcas]h{t9|Uwd)_(=0^6Zb{Nc} E[qZAeX[a]P^|_J>e8`W^j_Y}R{{Jp__]Ee#e:iWb9q_wKbujrbR}CY`,{mJ}gz{Q^{t~N|? gSga`V_||:#mi}3t|/I`X{N*|ct|2g{km}gi|{={jC}F;|E}{ZZjYf*frmu}8Tdroi{T[|+~}HG{cJ}DM{Lp{Ctd&}$hi3|FZ| m}Kr|38}^c|m_|Tr{Qv|36}?Up>|;S{DV{k_as}BK{P}}9p|t`jR{sAm4{D=b4pWa[}Xi{EjwEkI}3S|E?u=X0{jf} S|NM|JC{qo^3cm]-|JUx/{Cj{s>{Crt[UXuv|D~|j|d{YXZR}Aq}0r}(_{pJfi_z}0b|-vi)Z mFe,{f4|q`b{}^Z{HM{rbeHZ|^x_o|XM|L%|uFXm}@C_{{Hhp%a7|0p[Xp+^K}9U{bP}: tT}B|}+$|b2|[^|~h{FAby[`{}xgygrt~h1[li`c4vz|,7p~b(|mviN}^pg[{N/|g3|^0c,gE|f%|7N{q[|tc|TKA{LU}I@|AZp(}G-sz{F |qZ{}F|f-}RGn6{Z]_5})B}UJ{FFb2]4ZI@v=k,]t_Dg5Bj]Z-]L]vrpdvdGlk|gF}G]|IW}Y0[G| /bo|Te^,_B}#n^^{QHYI[?hxg{[`]D^IYRYTb&kJ[cri[g_9]Ud~^_]<p@_e_XdNm-^/|5)|h_{J;{kacVopf!q;asqd}n)|.m|bf{QW|U)}b+{tL|w``N|to{t ZO|T]jF}CB|0Q{e5Zw|k |We}5:{HO{tPwf_uajjBfX}-V_C_{{r~gg|Ude;s+}KNXH}! `K}eW{Upwbk%ogaW}9EYN}YY|&v|SL{C3[5s.]Y]I]u{M6{pYZ`^,`ZbCYR[1mNg>rsk0Ym[jrE]RYiZTr*YJ{Ge|%-lf|y(`=[t}E6{k!|3)}Zk} ][G{E~cF{u3U.rJ|a9p#o#ZE|?|{sYc#vv{E=|LC}cu{N8`/`3`9rt[4|He{cq|iSYxY`}V |(Q|t4{C?]k_Vlvk)BZ^r<{CL}#h}R+[<|i=}X|{KAo]|W<`K{NW|Zx}#;|fe{IMr<|K~tJ_x}AyLZ?{GvbLnRgN}X&{H7|x~}Jm{]-| GpNu0}.ok>|c4{PYisrDZ|fwh9|hfo@{H~XSbO]Odv]%`N]b1Y]]|eIZ}_-ZA]aj,>eFn+j[aQ_+]h[J_m_g]%_wf.`%k1e#Z?{CvYu_B^|gk`Xfh^M3`afGZ-Z|[m{L}|k3cp[it ^>YUi~d>{T*}YJ{Q5{Jxa$hg|%4`}|LAgvb }G}{P=|<;Ux{_skR{cV|-*|s-{Mp|XP|$G|_J}c6cM{_=_D|*9^$ec{V;|4S{qO|w_|.7}d0|/D}e}|0G{Dq]Kdp{}dfDi>}B%{Gd|nl}lf{C-{y}|ANZr}#={T~|-(}c&{pI|ft{lsVP}){|@u}!W|bcmB{d?|iW|:dxj{PSkO|Hl]Li:}VYk@|2={fnWt{M3`cZ6|)}|Xj}BYa?vo{e4|L7|B7{L7|1W|lvYO}W8nJ|$Vih|{T{d*_1|:-n2dblk``fT{Ky|-%}m!|Xy|-a{Pz}[l{kFjz|iH}9N{WE{x,|jz}R {P|{D)c=nX|Kq|si}Ge{sh|[X{RF{t`|jsr*fYf,rK|/9}$}}Nf{y!1|<Std}4Wez{W${Fd_/^O[ooqaw_z[L`Nbv[;l7V[ii3_PeM}.h^viqYjZ*j1}+3{bt{DR[;UG}3Og,rS{JO{qw{d<_zbAh<R[1_r`iZTbv^^a}c{iEgQZ<exZFg.^Rb+`Uj{a+{z<[~r!]`[[|rZYR|?F|qppp]L|-d|}K}YZUM|=Y|ktm*}F]{D;g{uI|7kg^}%?Z%ca{N[_<q4xC]i|PqZC]n}.bDrnh0Wq{tr|OMn6tM|!6|T`{O`|>!]ji+]_bTeU}Tq|ds}n|{Gm{z,f)}&s{DPYJ`%{CGd5v4tvb*hUh~bf]z`jajiFqAii]bfy^U{Or|m+{I)cS|.9k:e3`^|xN}@Dnlis`B|Qo{`W|>||kA}Y}{ERYuYx`%[exd`]|OyiHtb}HofUYbFo![5|+]gD{NIZR|Go}.T{rh^4]S|C9_}xO^i`vfQ}C)bK{TL}cQ|79iu}9a];sj{P.o!f[Y]pM``Jda^Wc9ZarteBZClxtM{LW}l9|a.mU}KX}4@{I+f1}37|8u}9c|v${xGlz}jP{Dd1}e:}31}%3X$|22i<v+r@~mf{sN{C67G97855F4YL5}8f{DT|xy{sO{DXB334@55J1)4.G9A#JDYtXTYM4, YQD9;XbXm9SX]IB^4UN=Xn<5(;(F3YW@XkH-X_VM[DYM:5XP!T&Y`6|,^{IS-*D.H>:LXjYQ0I3XhAF:9:(==.F*3F1189K/7163D,:@|e2{LS36D4hq{Lw/84443@4.933:0307::6D7}&l{Mx657;89;,K5678H&93D(H<&<>0B90X^I;}Ag1{P%3A+>><975}[S{PZE453?4|T2{Q+5187;>447:81{C=hL6{Me^:=7ii{R=.=F<81;48?|h8}Uh{SE|,VxL{ST,7?9Y_5Xk3A#:$%YSYdXeKXOD8+TXh7(@>(YdXYHXl9J6X_5IXaL0N?3YK7Xh!1?XgYz9YEXhXaYPXhC3X`-YLY_XfVf[EGXZ5L8BXL9YHX]SYTXjLXdJ: YcXbQXg1PX]Yx4|Jr{Ys4.8YU+XIY`0N,<H%-H;:0@,74/:8546I=9177154870UC]d<C3HXl7ALYzXFXWP<<?E!88E5@03YYXJ?YJ@6YxX-YdXhYG|9o{`iXjY_>YVXe>AYFX[/(I@0841?):-B=14337:8=|14{c&93788|di{cW-0>0<097/A;N{FqYpugAFT%X/Yo3Yn,#=XlCYHYNX[Xk3YN:YRT4?)-YH%A5XlYF3C1=NWyY}>:74-C673<69545v {iT85YED=64=.F4..9878/D4378?48B3:7:7/1VX[f4{D,{l<5E75{dAbRB-8-@+;DBF/$ZfW8S<4YhXA.(5@*11YV8./S95C/0R-A4AXQYI7?68167B95HA1*<M3?1/@;/=54XbYP36}lc{qzSS38:19?,/39193574/66878Yw1X-87E6=;964X`T734:>86>1/=0;(I-1::7ALYGXhF+Xk[@W%TYbX7)KXdYEXi,H-XhYMRXfYK?XgXj.9HX_SX]YL1XmYJ>Y}WwIXiI-3-GXcYyXUYJ$X`Vs[7;XnYEZ;XF! 3;%8;PXX(N3Y[)Xi1YE&/ :;74YQ6X`33C;-(>Xm0(TYF/!YGXg8 9L5P01YPXO-5%C|qd{{/K/E6,=0144:361:955;6443@?B7*7:F89&F35YaX-CYf,XiFYRXE_e{}sF 0*7XRYPYfXa5YXXY8Xf8Y~XmA[9VjYj*#YMXIYOXk,HHX40YxYMXU8OXe;YFXLYuPXP?EB[QV0CXfY{:9XV[FWE0D6X^YVP*$4%OXiYQ(|xp|%c3{}V`1>Y`XH00:8/M6XhQ1:;3414|TE|&o@1*=81G8<3}6<|(f6>>>5-5:8;093B^3U*+*^*UT30XgYU&7*O1953)5@E78--F7YF*B&0:%P68W9Zn5974J9::3}Vk|-,C)=)1AJ4+<3YGXfY[XQXmT1M-XcYTYZXCYZXEYXXMYN,17>XIG*SaS|/eYJXbI?XdNZ+WRYP<F:R PXf;0Xg`$|1GX9YdXjLYxWX!ZIXGYaXNYm6X9YMX?9EXmZ&XZ#XQ>YeXRXfAY[4 ;0X!Zz0XdN$XhYL XIY^XGNXUYS/1YFXhYk.TXn4DXjB{jg|4DEX]:XcZMW=A.+QYL<LKXc[vV$+&PX*Z3XMYIXUQ:ZvW< YSXFZ,XBYeXMM)?Xa XiZ4/EXcP3%}&-|6~:1(-+YT$@XIYRBC<}&,|7aJ6}bp|8)K1|Xg|8C}[T|8Q.89;-964I38361<=/;883651467<7:>?1:.}le|:Z=39;1Y^)?:J=?XfLXbXi=Q0YVYOXaXiLXmJXO5?.SFXiCYW}-;|=u&D-X`N0X^,YzYRXO(QX_YW9`I|>hZ:N&X)DQXP@YH#XmNXi$YWX^=!G6YbYdX>XjY|XlX^XdYkX>YnXUXPYF)FXT[EVTMYmYJXmYSXmNXi#GXmT3X8HOX[ZiXN]IU2>8YdX1YbX<YfWuZ8XSXcZU%0;1XnXkZ_WTG,XZYX5YSX Yp 05G?XcYW(IXg6K/XlYP4XnI @XnO1W4Zp-9C@%QDYX+OYeX9>--YSXkD.YR%Q/Yo YUX].Xi<HYEZ2WdCE6YMXa7F)=,D>-@9/8@5=?7164;35387?N<618=6>7D+C50<6B03J0{Hj|N9$D,9I-,.KB3}m |NzE0::/81YqXjMXl7YG; [.W=Z0X4XQY]:MXiR,XgM?9$9>:?E;YE77VS[Y564760391?14941:0=:8B:;/1DXjFA-564=0B3XlH1+D85:0Q!B#:-6&N/:9<-R3/7Xn<*3J4.H:+334B.=>30H.;3833/76464665755:/83H6633:=;.>5645}&E|Y)?1/YG-,93&N3AE@5 <L1-G/8A0D858/30>8<549=@B8] V0[uVQYlXeD(P#ID&7T&7;Xi0;7T-$YE)E=1:E1GR):--0YI7=E<}n9|aT6783A>D7&4YG7=391W;Zx<5+>F#J39}o/|cc;6=A050EQXg8A1-}D-|d^5548083563695D?-.YOXd37I$@LYLWeYlX<Yd+YR A$;3-4YQ-9XmA0!9/XLY_YT(=5XdDI>YJ5XP1ZAW{9>X_6R(XhYO65&J%DA)C-!B:97#A9;@?F;&;(9=11/=657/H,<8}bz|j^5446>.L+&Y^8Xb6?(CYOXb*YF(8X`FYR(XPYVXmPQ%&DD(XmZXW??YOXZXfCYJ79,O)XnYF7K0!QXmXi4IYFRXS,6<%-:YO(+:-3Q!1E1:W,Zo}Am|n~;3580534*?3Zc4=9334361693:30C<6/717:<1/;>59&:4}6!|rS36=1?75<8}[B|s809983579I.A.>84758=108564741H*9E{L{|u%YQ<%6XfH.YUXe4YL@,>N}Tv|ve*G0X)Z;/)3@A74(4P&A1X:YVH97;,754*A66:1 D739E3553545558E4?-?K17/770843XAYf838A7K%N!YW4.$T19Z`WJ*0XdYJXTYOXNZ 1XaN1A+I&Xi.Xk3Z3GB&5%WhZ1+5#Y[X<4YMXhQYoQXVXbYQ8XSYUX4YXBXWDMG0WxZA[8V+Z8X;D],Va$%YeX?FXfX[XeYf<X:Z[WsYz8X_Y]%XmQ(!7BXIZFX]&YE3F$(1XgYgYE& +[+W!<YMYFXc;+PXCYI9YrWxGXY9DY[!GXiI7::)OC;*$.>N*HA@{C|}&k=:<TB83X`3YL+G4XiK]i}(fYK<=5$.FYE%4*5*H*6XkCYL=*6Xi6!Yi1KXR4YHXbC8Xj,B9ZbWx/XbYON#5B}Ue}+QKXnF1&YV5XmYQ0!*3IXBYb71?1B75XmF;0B976;H/RXU:YZX;BG-NXj;XjI>A#D3B636N;,*%<D:0;YRXY973H5)-4FXOYf0:0;/7759774;7;:/855:543L43<?6=E,.A4:C=L)%4YV!1(YE/4YF+ F3%;S;&JC:%/?YEXJ4GXf/YS-EXEYW,9;E}X$}547EXiK=51-?71C%?57;5>463553Zg90;6447?<>4:9.7538XgN{|!}9K/E&3-:D+YE1)YE/3;37/:05}n<}:UX8Yj4Yt864@JYK..G=.(A Q3%6K>3(P3#AYE$-6H/456*C=.XHY[#S.<780191;057C)=6HXj?955B:K1 E>-B/9,;5.!L?:0>/.@//:;7833YZ56<4:YE=/:7Z_WGC%3I6>XkC*&NA16X=Yz2$X:Y^&J48<99k8}CyB-61<18K946YO4{|N}E)YIB9K0L>4=46<1K0+R;6-=1883:478;4,S+3YJX`GJXh.Yp+Xm6MXcYpX(>7Yo,/:X=Z;Xi0YTYHXjYmXiXj;*;I-8S6N#XgY}.3XfYGO3C/$XjL$*NYX,1 6;YH&<XkK9C#I74.>}Hd`A748X[T450[n75<4439:18A107>|ET}Rf<1;14876/Yb983E<5.YNXd4149>,S=/4E/<306443G/06}0&}UkYSXFYF=44=-5095=88;63844,9E6644{PL}WA8:>)7+>763>>0/B3A545CCnT}Xm|dv}Xq1L/YNXk/H8;;.R63351YY747@15YE4J8;46;.38.>4A369.=-83,;Ye3?:3@YE.4-+N353;/;@(X[YYD>@/05-I*@.:551741Yf5>6A443<3535;.58/86=D4753442$635D1>0359NQ @73:3:>><Xn?;43C14 ?Y|X611YG1&<+,4<*,YLXl<1/AIXjF*N89A4Z576K1XbJ5YF.ZOWN.YGXO/YQ01:4G38Xl1;KI0YFXB=R<7;D/,/4>;$I,YGXm94@O35Yz66695385.>:6A#5}W7n^4336:4157597434433<3|XA}m`>=D>:4A.337370?-6Q96{`E|4A}C`|Qs{Mk|J+~r>|o,wHv>Vw}!c{H!|Gb|*Ca5}J||,U{t+{CN[!M65YXOY_*B,Y[Z9XaX[QYJYLXPYuZ%XcZ8LY[SYPYKZM<LMYG9OYqSQYM~[e{UJXmQYyZM_)>YjN1~[f3{aXFY|Yk:48YdH^NZ0|T){jVFYTZNFY^YTYN~[h{nPYMYn3I]`EYUYsYIZEYJ7Yw)YnXPQYH+Z.ZAZY]^Z1Y`YSZFZyGYHXLYG 8Yd#4~[i|+)YH9D?Y^F~Y7|-eYxZ^WHYdYfZQ~[j|3>~[k|3oYmYqY^XYYO=Z*4[]Z/OYLXhZ1YLZIXgYIHYEYK,<Y`YEXIGZI[3YOYcB4SZ!YHZ*&Y{Xi3~[l|JSY`Zz?Z,~[m|O=Yi>??XnYWXmYS617YVYIHZ(Z4[~L4/=~[n|Yu{P)|];YOHHZ}~[o33|a>~[r|aE]DH~[s|e$Zz~[t|kZFY~XhYXZB[`Y}~[u|{SZ&OYkYQYuZ2Zf8D~[v}% ~[w3},Q[X]+YGYeYPIS~[y}4aZ!YN^!6PZ*~[z}?E~[{3}CnZ=~[}}EdDZz/9A3(3S<,YR8.D=*XgYPYcXN3Z5 4)~[~}JW=$Yu.XX~] }KDX`PXdZ4XfYpTJLY[F5]X~[2Yp}U+DZJ::<446[m@~]#3}]1~]%}^LZwZQ5Z`/OT<Yh^ -~]&}jx[ ~m<z!%2+~ly4VY-~o>}p62yz!%2+Xf2+~ly4VY-zQ`z (=] 2z~o2\",C={\" \":0,\"!\":1},c=34,i=2,p,s=\"\",u=String.fromCharCode,t=u(12539);for(;++c<127;)C[u(c)]=c^39&&c^92?i++:0;i=0;for(;0<=(c=C[a.charAt(i++)]);)if(16===c)if((c=C[a.charAt(i++)])<87){if(86===c)c=1879;for(;c--;)s+=u(++p)}else s+=s.substr(8272,360);else if(c<86)s+=u(p+=c<51?c-16:(c-55)*92+C[a.charAt(i++)]);else if((c=((c-86)*92+C[a.charAt(i++)])*92+C[a.charAt(i++)])<49152)s+=u(p=c<40960?c:c|57344);else{c&=511;for(;c--;)s+=t;p=12539}return s')(),Util.$decodeToShiftJis=function(t){return t.replace(/%(8[1-9A-F]|[9E][0-9A-F]|F[0-9A-C])(%[4-689A-F][0-9A-F]|%7[0-9A-E]|[@-~])|%([0-7][0-9A-F]|A[1-9A-F]|[B-D][0-9A-F])/gi,function(t){let e=parseInt(t.substring(1,3),16);const s=t.length;return 3===s?String.fromCharCode(e<160?e:e+65216):Util.$JCT11280.charAt(188*(e<160?e-129:e-193)+(4===s?t.charCodeAt(3)-64:(e=parseInt(t.substring(4),16))<127?e-64:e-65))})},Util.$getTagObject=function(){return Util.$tagObjects.pop()||{placeObjects:[],sounds:[],removeObjects:[],frameLabel:[]}},Util.$poolTagObject=function(t){t.placeObjects.length=0,t.sounds.length=0,t.removeObjects.length=0,t.frameLabel.length=0,Util.$tagObjects.push(t)},Util.$createMovieClip=function(){const t={_$characterId:0,_$name:\"MovieClip\",_$controller:[],_$placeObjects:[],_$placeMap:[],_$labels:[],_$dictionary:[],_$sounds:[]};return t},Util.$getControllerAt=function(t,e,s){return s in t._$controller[e]?t._$controller[e][s]:null},Util.$addDictionary=function(t,e){const s=t._$dictionary.length,a={CharacterId:e.CharacterId,Depth:e.Depth,Name:null,ClipDepth:0,PlaceFlagHasImage:0|e.PlaceFlagHasImage,StartFrame:0|e.StartFrame,EndFrame:0|e.EndFrame};return e.PlaceFlagHasName&&(a.Name=e.Name),e.PlaceFlagHasClipDepth&&(a.ClipDepth=e.ClipDepth),t._$dictionary[s]=a,s},Util.$getBlendName=function(t){switch(t){case 1:case\"normal\":default:return\"normal\";case 2:case\"layer\":return\"layer\";case 3:case\"multiply\":return\"multiply\";case 4:case\"screen\":return\"screen\";case 5:case\"lighten\":return\"lighten\";case 6:case\"darken\":return\"darken\";case 7:case\"difference\":return\"difference\";case 8:case\"add\":return\"add\";case 9:case\"subtract\":return\"subtract\";case 10:case\"invert\":return\"invert\";case 11:case\"alpha\":return\"alpha\";case 12:case\"erase\":return\"erase\";case 13:case\"overlay\":return\"overlay\";case 14:case\"hardlight\":return\"hardlight\"}};class ByteStream{constructor(){this.clear()}clear(){this.data=null,this.bit_offset=0,this.byte_offset=0,this.bit_buffer=null}setData(t){this.data=t}getData(t){this.byteAlign();const e=this.byte_offset+t,s=this.data.subarray(this.byte_offset,e);return this.byte_offset=e,s}byteAlign(){this.bit_offset&&(this.byte_offset=this.byte_offset+(this.bit_offset+7)/8|0,this.bit_offset=0)}getDataUntil(t=0){this.byteAlign();let e=\"\";for(;;){const t=this.data[this.byte_offset++];if(!t)break;if(10===t||13===t){e+=\"\\n\";continue}let s=t.toString(16);1===s.length&&(s=\"0\"+s),e+=\"%\"+s}if(!e.length)return\"\";if(e.length>5&&\"\\n\"===e.substr(-5)&&(e=e.slice(0,-5)),t)return Util.$decodeToShiftJis(e);try{return decodeURIComponent(e)}catch(t){return Util.$decodeToShiftJis(e)}}byteCarry(){if(this.bit_offset>7)this.byte_offset=this.byte_offset+(0|(this.bit_offset+7)/8),this.bit_offset&=7;else for(;this.bit_offset<0;)--this.byte_offset,this.bit_offset+=8}getUIBits(t){let e=0;for(;t;)e<<=1,e|=this.getUIBit(),--t;return e}getUIBit(){return this.byteCarry(),this.data[this.byte_offset]>>7-this.bit_offset++&1}getSIBits(t){const e=this.getUIBits(t),s=e&1<<t-1;return s?-(e^2*s-1)-1:e}getUI8(){return this.byteAlign(),this.data[this.byte_offset++]}getUI16(){return this.byteAlign(),this.getUI8()|this.getUI8()<<8}getUI32(){return this.byteAlign(),this.getUI8()|(this.getUI8()|(this.getUI8()|this.getUI8()<<8)<<8)<<8}getFloat16(){const t=this.data[this.byte_offset++];let e=0;return e|=this.data[this.byte_offset++]<<8,e|=t|0,e}getFloat32(){const t=this.data[this.byte_offset++],e=this.data[this.byte_offset++],s=this.data[this.byte_offset++];let a=0;a|=this.data[this.byte_offset++]<<24,a|=s<<16,a|=e<<8,a|=t|0;const i=a>>23&255;return a&&2147483648!==a?(2147483648&a?-1:1)*(8388608|8388607&a)*Math.pow(2,i-127-23):0}incrementOffset(t,e){this.byte_offset+=t,this.bit_offset+=e,this.byteCarry()}setOffset(t,e){this.byte_offset=t,this.bit_offset=e}}class SwfParser{constructor(){this.byteStream=new ByteStream,this.currentPosition={x:0,y:0},this.jpegTables=null,this.characters=[],this.frameInfo=[],this.fonts=new Map,this.textSettings=new Map,this.grids=new Map,this.version=0}clear(){this.byteStream.clear(),this.currentPosition.x=0,this.currentPosition.y=0,this.jpegTables=null,this.characters.length=0,this.frameInfo.length=0,this.version=0}getCharacter(t){return this.characters[t]}setCharacter(t,e,s){this.characters[t]=e,globalThis.postMessage({infoKey:\"character\",characterId:t,piece:e},s)}getFont(t){return this.fonts.get(t)}setFont(t,e){this.fonts.set(t,e)}setTextSetting(t,e){this.textSettings.set(t,e)}setGrid(t,e){this.grids.set(t,e)}showFrame(t,e,s,a){let i,r;const h=s-1|0,o=e.frameLabel;i=o.length;for(let e=0;e<i;++e){const a=o[e];a.name in this.frameInfo&&(a.frame=this.frameInfo[\"@\"+a.name]),t._$labels.push({label:a.name,frame:a.frame||s})}const n=e.sounds;i=0|n.length,i&&t._$sounds.push({frame:s,data:n.slice(0)});const l=e.removeObjects;i=l.length;for(let e=0;e<i;++e){const a=l[e],i=Util.$getControllerAt(t,h,a.Depth);t._$dictionary[i].EndFrame=s,Util.$installed.set(a.Depth,1)}s in a||(a[s]=[]),s in t._$controller||(t._$controller[s]=[]),s in t._$placeMap||(t._$placeMap[s]=[]);const c=e.placeObjects,b=h?a[h]:null;i=c.length;for(let e=0;e<i;++e){let i=null;const r=c[e];let o=null;h&&r.Depth in b&&(o=b[r.Depth]),0===r.PlaceFlagHasCharacter&&o&&(r.CharacterId=o.CharacterId);let n=!1;if((0===r.PlaceFlagMove||1===r.PlaceFlagMove&&1===r.PlaceFlagHasCharacter)&&(n=!0),h&&!n&&(i=Util.$getControllerAt(t,h,r.Depth),null===i&&(n=!0)),1===r.PlaceFlagMove&&o&&(1!==o.PlaceFlagHasMatrix||r.PlaceFlagHasMatrix||(r.PlaceFlagHasMatrix=1,r.Matrix=o.Matrix),1!==o.PlaceFlagHasColorTransform||r.PlaceFlagHasColorTransform||(r.PlaceFlagHasColorTransform=1,r.ColorTransform=o.ColorTransform),1!==o.PlaceFlagHasClipDepth||r.PlaceFlagHasClipDepth||(r.PlaceFlagHasClipDepth=1,r.ClipDepth=o.ClipDepth),1!==o.PlaceFlagHasRatio||r.PlaceFlagHasRatio||(r.PlaceFlagHasRatio=1,r.Ratio=o.Ratio),1!==o.PlaceFlagHasFilterList||r.PlaceFlagHasFilterList||(r.PlaceFlagHasFilterList=1,r.SurfaceFilterList=o.SurfaceFilterList),1!==o.PlaceFlagHasBlendMode||r.PlaceFlagHasBlendMode||(r.PlaceFlagHasBlendMode=1,r.BlendMode=o.BlendMode)),h&&!Util.$installed.has(r.Depth)){const e=Util.$getControllerAt(t,h,r.Depth);if(null!==e){const a=t._$dictionary[e];!a||0!==r.PlaceFlagMove&&1!==r.PlaceFlagHasCharacter||(a.EndFrame=0|s,t._$dictionary[e]=a,n=!0)}}if(n){if(r.StartFrame=0|s,r.EndFrame=0,1===r.PlaceFlagHasCharacter&&1===r.PlaceFlagMove){const e=Util.$getControllerAt(t,h,r.Depth),a=t._$dictionary[e];a.EndFrame=0|s,t._$dictionary[e]=a}i=Util.$addDictionary(t,r)}t._$controller[s][r.Depth]=i;const l=t._$placeObjects.length;t._$placeObjects[l]=this.buildPlaceObject(r),t._$placeMap[s][r.Depth]=l,Util.$installed.set(r.Depth,1),a[s][r.Depth]=r}if(h){let e;const o=t._$controller[h];r=Object.keys(o),i=r.length;for(let n=0;n<i;++n)e=0|r[n],Util.$installed.has(e)||(a[s][e]=a[h][e],t._$controller[s][e]=o[e]);const n=t._$placeMap[h];r=Object.keys(n),i=r.length;for(let a=0;a<i;++a)e=r[a],e in t._$placeMap[s]||(t._$placeMap[s][e]=n[e])}Util.$installed.clear()}buildPlaceObject(t){const e={matrix:[1,0,0,1,0,0],colorTransform:[1,1,1,1,0,0,0,0],filters:null,blendMode:\"normal\"};return t.PlaceFlagHasMatrix&&(e.matrix=t.Matrix),t.PlaceFlagHasColorTransform&&(e.colorTransform=t.ColorTransform),t.PlaceFlagHasFilterList&&(e.surfaceFilterList=t.SurfaceFilterList),t.PlaceFlagHasBlendMode&&(e.blendMode=Util.$getBlendName(t.BlendMode)),t.PlaceFlagHasRatio&&(e.ratio=t.Ratio||0),e}postData(t){if(this.textSettings.size){for(let[t,e]of this.textSettings){const s=this.characters[t];s&&(s._$textSetting=e,globalThis.postMessage({infoKey:\"character\",characterId:t,piece:s}))}this.textSettings.clear()}if(this.grids.size){for(let[t,e]of this.grids){const s=this.characters[t];s&&(s._$grid=e,globalThis.postMessage({infoKey:\"character\",characterId:t,piece:s}))}this.grids.clear()}if(this.fonts.size){for(let[t,e]of this.fonts){if(!e._$hasLayout){globalThis.postMessage({infoKey:\"font\",index:t,piece:e});continue}const s=e._$glyphShapeTable,a=e._$zoneTable;e._$glyphShapeTable=[],e._$zoneTable=a?[]:null,globalThis.postMessage({infoKey:\"font\",index:t,piece:e},[e._$advanceTable.buffer,e._$codeTable.buffer]);const i=s.length;if(i){const e=[],a=[];for(let r=0;r<i;++r){const i=s[r];e.push(i),a.push(i.records.buffer),e.length>256&&(globalThis.postMessage({infoKey:\"font_shape\",index:t,pieces:e},a),a.length=0,e.length=0)}e.length&&globalThis.postMessage({infoKey:\"font_shape\",index:t,pieces:e},a)}if(a)for(;a.length;){const e=Math.min(256,a.length);globalThis.postMessage({infoKey:\"font_zone\",index:t,pieces:a.splice(0,e)})}}this.fonts.clear()}for(let e=1;e<t._$controller.length;++e){const s=t._$controller[e];t._$controller[e]=s.filter(()=>!0)}this.setCharacter(0,t)}parseTags(t,e){const s=Util.$getTagObject();let a=1;const i=[],r=this.byteStream;for(;r.byte_offset<t;){const h=r.byte_offset;if(h+2>t)break;const o=r.getUI16(),n=o>>6;let l=63&o;if(63===l){if(h+6>t){r.byte_offset=h,r.bit_offset=0;break}l=r.getUI32()}const c=r.byte_offset;this.parseTag(n,l,e,a,s,i),1===n&&(++a,s.placeObjects.length=0,s.sounds.length=0,s.removeObjects.length=0,s.frameLabel.length=0);const b=r.byte_offset-c|0;b!==l&&b<l&&(r.byte_offset=r.byte_offset+(l-b)),r.bit_offset=0}Util.$poolTagObject(s)}parseTag(t,e,s,a,i,r){switch(t){case 28:i.removeObjects.push({Frame:a,Depth:this.byteStream.getUI16()});break;case 4:case 26:case 70:i.placeObjects.push(this.parsePlaceObject(t,e));break;case 39:{const t=this.byteStream.byte_offset+e,s=this.byteStream.getUI16();this.byteStream.getUI16();const a=Util.$createMovieClip();a._$characterId=s,this.parseTags(t,a);for(let t=1;t<a._$controller.length;++t){const e=a._$controller[t];a._$controller[t]=e.filter(()=>!0)}this.setCharacter(s,a)}break;case 1:this.showFrame(s,i,a,r);break;case 2:case 22:case 32:case 83:e<10?this.byteStream.byte_offset+=e:this.parseDefineShape(t);break;case 20:case 36:this.parseDefineBitsLossLess(t,e);break;case 6:case 21:case 35:case 90:this.parseDefineBits(t,e,this.jpegTables);break;case 15:case 89:i.sounds.push(this.parseStartSound(t));break;case 10:case 48:case 75:this.parseDefineFont(t,e);break;case 14:this.parseDefineSound(e);break;case 13:case 62:this.parseDefineFontInfo(t,e);break;case 43:i.frameLabel.push(this.parseFrameLabel());break;case 11:case 33:this.parseDefineText(t);break;case 37:this.parseDefineEditText(t);break;case 7:case 34:this.parseDefineButton(t,e);break;case 88:this.parseDefineFontName();break;case 8:e&&(this.jpegTables=this.parseJPEGTables(e));break;case 46:case 84:this.parseDefineMorphShape(t);break;case 18:case 45:this.parseSoundStreamHead(t);break;case 17:this.parseDefineButtonSound();break;case 73:this.parseDefineFontAlignZones();break;case 74:this.parseCSMTextSettings(t);break;case 19:this.parseSoundStreamBlock(t,e);break;case 78:this.parseDefineScalingGrid();break;case 5:console.log(\"TODO RemoveObject type 5.\"),i.removeObjects.push({CharacterId:this.byteStream.getUI16(),Depth:this.byteStream.getUI16()});break;case 76:this.parseSymbolClass();break;case 0:case 27:case 30:case 67:case 68:case 79:case 80:case 81:case 85:case 92:default:break;case 86:case 56:case 9:case 40:case 24:case 63:case 64:case 69:case 65:case 77:case 60:case 61:case 41:case 87:case 59:case 12:case 72:case 82:this.byteStream.byte_offset+=e;break;case 3:case 16:case 23:case 25:case 29:case 31:case 38:case 42:case 44:case 47:case 49:case 52:case 53:case 54:case 55:case 57:case 58:case 66:case 71:case 91:case 93:console.log(\"[TODO] tagType -> \"+t)}}parseSymbolClass(){const t=this.byteStream.getUI16();if(t){const e=[];for(let s=0;s<t;++s){const t=this.byteStream.getUI16(),s=this.byteStream.getDataUntil();e[e.length]={tagId:t,ns:s},128===e.length&&(globalThis.postMessage({infoKey:\"_$symbols\",pieces:e}),e.length=0)}e.length&&globalThis.postMessage({infoKey:\"_$symbols\",pieces:e})}}parseDefineShape(t){const e=0|this.byteStream.getUI16(),s=this.rect();if(83===t){const t={};this.rect(),this.byteStream.getUIBits(5),t.UsesFillWindingRule=this.byteStream.getUIBits(1),t.UsesNonScalingStrokes=this.byteStream.getUIBits(1),t.UsesScalingStrokes=this.byteStream.getUIBits(1)}const a=this.shapeWithStyle(t);this.setCharacter(e,{_$records:a,_$name:\"Shape\",_$bounds:s,_$characterId:e},[a.ShapeData.records.buffer])}rect(){this.byteStream.byteAlign();const t=this.byteStream.getUIBits(5);return{xMin:this.byteStream.getSIBits(t)/20,xMax:this.byteStream.getSIBits(t)/20,yMin:this.byteStream.getSIBits(t)/20,yMax:this.byteStream.getSIBits(t)/20}}shapeWithStyle(t){const e={};switch(t){case 46:case 84:break;default:e.fillStyles=this.fillStyleArray(t),e.lineStyles=this.lineStyleArray(t)}const s=this.byteStream.getUI8(),a=s>>4,i=15&s;return e.ShapeData=this.shapeRecords(t,{FillBits:a,LineBits:i}),e}fillStyleArray(t){let e=0|this.byteStream.getUI8();t>2&&255===e&&(e=this.byteStream.getUI16());const s=[];for(let a=0;a<e;++a)s[s.length]=this.fillStyle(t);return s}fillStyle(t){const e=this.byteStream.getUI8(),s={};switch(s.fillStyleType=e,e){case 0:switch(t){case 32:case 83:s.Color=this.rgba();break;case 46:case 84:s.StartColor=this.rgba(),s.EndColor=this.rgba();break;default:s.Color=this.rgb()}break;case 16:case 18:switch(t){case 46:case 84:s.startGradientMatrix=this.matrix(),s.endGradientMatrix=this.matrix(),s.gradient=this.gradient(t);break;default:s.gradientMatrix=this.matrix(),s.gradient=this.gradient(t)}break;case 19:s.gradientMatrix=this.matrix(),s.gradient=this.focalGradient(t);break;case 64:case 65:case 66:case 67:switch(s.bitmapId=this.byteStream.getUI16(),t){case 46:case 84:s.startBitmapMatrix=this.matrix(),s.endBitmapMatrix=this.matrix();break;default:s.bitmapMatrix=this.matrix()}}return s}rgb(){return{R:0|this.byteStream.getUI8(),G:0|this.byteStream.getUI8(),B:0|this.byteStream.getUI8(),A:1}}rgba(){return{R:this.byteStream.getUI8(),G:this.byteStream.getUI8(),B:this.byteStream.getUI8(),A:this.byteStream.getUI8()/255}}matrix(){this.byteStream.byteAlign();const t=[1,0,0,1,0,0];if(this.byteStream.getUIBit()){const e=this.byteStream.getUIBits(5);t[0]=this.byteStream.getSIBits(e)/65536,t[3]=this.byteStream.getSIBits(e)/65536}if(this.byteStream.getUIBit()){const e=this.byteStream.getUIBits(5);t[1]=this.byteStream.getSIBits(e)/65536,t[2]=this.byteStream.getSIBits(e)/65536}const e=this.byteStream.getUIBits(5);return t[4]=this.byteStream.getSIBits(e)/20,t[5]=this.byteStream.getSIBits(e)/20,t}gradient(t){let e,s=0,a=0;switch(this.byteStream.byteAlign(),t){case 46:case 84:e=this.byteStream.getUI8();break;default:s=this.byteStream.getUIBits(2),a=this.byteStream.getUIBits(2),e=this.byteStream.getUIBits(4)}const i=[];for(let s=0;s<e;++s)i[i.length]=this.gradientRecord(t);return{SpreadMode:s,InterpolationMode:a,GradientRecords:i,FocalPoint:0}}gradientRecord(t){switch(t){case 46:case 84:return{StartRatio:this.byteStream.getUI8()/255,StartColor:this.rgba(),EndRatio:this.byteStream.getUI8()/255,EndColor:this.rgba()};default:return{Ratio:this.byteStream.getUI8()/255,Color:t<32?this.rgb():this.rgba()}}}focalGradient(t){this.byteStream.byteAlign();const e=this.byteStream.getUIBits(2),s=this.byteStream.getUIBits(2),a=this.byteStream.getUIBits(4),i=[];for(let e=0;e<a;++e)i[i.length]=this.gradientRecord(t);return{SpreadMode:e,InterpolationMode:s,GradientRecords:i,FocalPoint:this.byteStream.getFloat16()}}lineStyleArray(t){let e=this.byteStream.getUI8();t>2&&255===e&&(e=this.byteStream.getUI16());const s=[];for(let a=0;a<e;++a)s[s.length]=this.lineStyles(t);return s}lineStyles(t){const e={fillStyleType:0};switch(t){case 46:e.StartWidth=this.byteStream.getUI16()/20,e.EndWidth=this.byteStream.getUI16()/20,e.StartColor=this.rgba(),e.EndColor=this.rgba();break;case 84:e.StartWidth=this.byteStream.getUI16()/20,e.EndWidth=this.byteStream.getUI16()/20,e.StartCapStyle=this.byteStream.getUIBits(2),e.JoinStyle=this.byteStream.getUIBits(2),e.HasFillFlag=this.byteStream.getUIBit(),e.NoHScaleFlag=this.byteStream.getUIBit(),e.NoVScaleFlag=this.byteStream.getUIBit(),e.PixelHintingFlag=this.byteStream.getUIBit(),this.byteStream.getUIBits(5),e.NoClose=this.byteStream.getUIBit(),e.EndCapStyle=this.byteStream.getUIBits(2),2===e.JoinStyle&&(e.MiterLimitFactor=this.byteStream.getUI16()/20),e.HasFillFlag?e.FillType=this.fillStyle(t):(e.StartColor=this.rgba(),e.EndColor=this.rgba());break;case 83:e.Width=this.byteStream.getUI16()/20,e.StartCapStyle=this.byteStream.getUIBits(2),e.JoinStyle=this.byteStream.getUIBits(2),e.HasFillFlag=this.byteStream.getUIBit(),e.NoHScaleFlag=this.byteStream.getUIBit(),e.NoVScaleFlag=this.byteStream.getUIBit(),e.PixelHintingFlag=this.byteStream.getUIBit(),this.byteStream.getUIBits(5),e.NoClose=this.byteStream.getUIBit(),e.EndCapStyle=this.byteStream.getUIBits(2),2===e.JoinStyle&&(e.MiterLimitFactor=this.byteStream.getUI16()),e.HasFillFlag?e.FillType=this.fillStyle(t):e.Color=this.rgba();break;case 32:e.Width=this.byteStream.getUI16()/20,e.Color=this.rgba(),e.JoinStyle=0,e.StartCapStyle=0,e.EndCapStyle=0;break;default:e.Width=this.byteStream.getUI16()/20,e.Color=this.rgb(),e.JoinStyle=0,e.StartCapStyle=0,e.EndCapStyle=0}return e}shapeRecords(t,e){this.currentPosition.x=0,this.currentPosition.y=0;const s=[],a=[];for(;;){const i=this.byteStream.getUIBits(6);if(32&i){const e=15&i;if(16&i){this.straightEdgeRecord(t,e,s);continue}this.curvedEdgeRecord(t,e,s);continue}if(!i){s.push(-1),this.byteStream.byteAlign();break}this.styleChangeRecord(t,i,e,s,a)}const i={records:new Int32Array(s)};return a.length&&(i.styles=a),i}straightEdgeRecord(t,e,s){let a=0,i=0;this.byteStream.getUIBit()?(a=this.byteStream.getSIBits(e+2),i=this.byteStream.getSIBits(e+2)):this.byteStream.getUIBit()?i=this.byteStream.getSIBits(e+2):a=this.byteStream.getSIBits(e+2);let r=a,h=i;switch(t){case 46:case 84:break;default:r=this.currentPosition.x+a,h=this.currentPosition.y+i,this.currentPosition.x=r,this.currentPosition.y=h}s.push(0,0,r,h)}curvedEdgeRecord(t,e,s){const a=this.byteStream.getSIBits(e+2),i=this.byteStream.getSIBits(e+2),r=this.byteStream.getSIBits(e+2),h=this.byteStream.getSIBits(e+2);let o=a,n=i,l=r,c=h;switch(t){case 46:case 84:break;default:o=this.currentPosition.x+a,n=this.currentPosition.y+i,l=o+r,c=n+h,this.currentPosition.x=l,this.currentPosition.y=c}s.push(0,1,o,n,l,c)}styleChangeRecord(t,e,s,a,i){const r=e>>4&1,h=e>>3&1,o=e>>2&1,n=e>>1&1,l=1&e;let c=0,b=0;if(l){const t=this.byteStream.getUIBits(5);c=this.byteStream.getSIBits(t),b=this.byteStream.getSIBits(t),this.currentPosition.x=c,this.currentPosition.y=b}const g=n?this.byteStream.getUIBits(s.FillBits):0,y=o?this.byteStream.getUIBits(s.FillBits):0,S=h?this.byteStream.getUIBits(s.LineBits):0;let m=null,f=null,d=0,Y=0;if(r){m=this.fillStyleArray(t),f=this.lineStyleArray(t);const e=this.byteStream.getUI8();s.FillBits=d=e>>4,s.LineBits=Y=15&e}a.push(1,r),r&&(a.push(d,Y),i.push({FillStyles:m,LineStyles:f})),a.push(l),l&&a.push(c,b),a.push(n),n&&a.push(g),a.push(o),o&&a.push(y),a.push(h),h&&a.push(S)}parseDefineBitsLossLess(t,e){const s=this.byteStream.byte_offset,a=this.byteStream.getUI16(),i=this.byteStream.getUI8(),r=this.byteStream.getUI16(),h=this.byteStream.getUI16(),o=36===t,n=3===i?this.byteStream.getUI8()+1:0;let l=r*h*4;if(3===i){l=(r+((r+3&-4)-r|0))*h+n*(o?4:3)}const c=e-(this.byteStream.byte_offset-s),b=this.byteStream.byte_offset;this.byteStream.byte_offset+=c;const g=this.byteStream.data.slice(b,this.byteStream.byte_offset),y={width:r,height:h,format:i,fileSize:l,tableSize:n,isAlpha:o,color:o?4278190080:0,_$name:\"lossless\",_$characterId:a,buffer:g};this.setCharacter(a,y,[g.buffer])}parseJPEGTables(t){const e=this.byteStream.byte_offset;return this.byteStream.byte_offset+=t,{offset:e,length:this.byteStream.byte_offset}}parseDefineBits(t,e,s=null){const a=this.byteStream.byte_offset,i=this.byteStream.getUI16(),r=this.byteStream.byte_offset-a,h=35===t||90===t?this.byteStream.getUI32():e-r;if(90===t){const t=this.byteStream.getUI16();console.log(\"TODO DeblockParam\",t)}const o=this.byteStream.byte_offset;this.byteStream.byte_offset+=h;let n=this.byteStream.data.slice(o,this.byteStream.byte_offset);if(s){const t=this.byteStream.data.subarray(s.offset,s.length);if(t.length>4&&255===n[0]&&216===n[1]){const e=t.length-2,s=n.length,a=new Uint8Array(e+s);a.set(t.subarray(0,e),0),a.set(n.subarray(2,s),e),n=a}}const l={infoKey:\"character\",_$name:\"imageData\",_$characterId:i,jpegData:n,alphaData:null},c=[];c.push(n.buffer);let b=!1;const g=a+e-this.byteStream.byte_offset;if(g){b=!0;const t=this.byteStream.byte_offset;this.byteStream.byte_offset+=g;const e=this.byteStream.data.slice(t,this.byteStream.byte_offset);l.alphaData=e,c.push(e.buffer)}l.isAlpha=b,l.color=b?4278190080:0,this.setCharacter(i,l,c)}parseDefineFont(t,e){const s=this.byteStream.byte_offset+e|0,a=this.byteStream.getUI16(),i=this.getFont(a)||{};let r=0,h=0,o=0;if(48===t||75===t){const t=this.byteStream.getUI8();i._$hasLayout=t>>>7&1,i._$shiftJIS=t>>>6&1,i._$smallText=t>>>5&1,i._$ANSI=t>>>4&1,h=t>>>3&1,o=t>>>2&1,i._$italic=t>>>1&1,i._$bold=1&t,this.byteStream.byteAlign(),i._$languageCode=this.byteStream.getUI8();const e=this.byteStream.getUI8();if(e){const t=0|this.byteStream.byte_offset;i._$fontName=this.getFontName(this.byteStream.getDataUntil()),this.byteStream.byte_offset=t+e|0}r=this.byteStream.getUI16(),i._$numGlyphs=r}const n=0|this.byteStream.byte_offset;if(10===t&&(r=this.byteStream.getUI16()),r){const e=[];10===t&&(e[0]=r,r/=2,r-=1);let s=0;if(1===h){for(let t=0;t<r;++t)e[e.length]=this.byteStream.getUI32();10!==t&&(s=this.byteStream.getUI32())}else{for(let t=0;t<r;++t)e[e.length]=this.byteStream.getUI16();10!==t&&(s=this.byteStream.getUI16())}const a=[];10===t&&(r+=1);for(let s=0;s<r;++s){this.byteStream.setOffset(e[s]+n,0);const i=this.byteStream.getUI8(),r={FillBits:i>>4,LineBits:15&i};a[a.length]=this.shapeRecords(t,r)}switch(i._$glyphShapeTable=a,t){case 48:case 75:if(this.byteStream.setOffset(s+n,0),1===o){const t=new Uint16Array(r);for(let e=0;e<r;++e)t[e]=this.byteStream.getUI16();i._$codeTable=t}else{const t=new Uint8Array(r);for(let e=0;e<r;++e)t[e]=this.byteStream.getUI8();i._$codeTable=t}if(i._$hasLayout){i._$ascent=this.byteStream.getUI16(),i._$descent=this.byteStream.getUI16(),i._$leading=this.byteStream.getUI16();const e=new Uint16Array(r);for(let t=0;t<r;++t)e[t]=this.byteStream.getUI16();i._$advanceTable=e;const s=[];for(let t=0;t<r;++t)s[s.length]=this.rect();if(75===t){const t=this.byteStream.getUI16(),e=[];for(let s=0;s<t;++s){const t=o?this.byteStream.getUI16():this.byteStream.getUI8(),s=o?this.byteStream.getUI16():this.byteStream.getUI8(),a=this.byteStream.getSIBits(16);e[e.length]={FontKerningCode1:t,FontKerningCode2:s,FontKerningAdjustment:a}}i._$kerningRecords=e}}}}this.byteStream.byte_offset=0|s,this.setFont(a,i)}parseDefineFontInfo(t,e){const s=this.byteStream.byte_offset+e|0,a=this.byteStream.getUI16();let i=this.getFont(a);i||(i={});const r=this.byteStream.getUI8(),h=this.byteStream.getData(r);let o=\"\";for(let t=0;t<r;++t)h[t]>127||(o+=String.fromCharCode(h[t]));this.byteStream.getUIBits(2),i._$smallText=this.byteStream.getUIBits(1),i._$shiftJIS=this.byteStream.getUIBits(1),i._$ANSI=this.byteStream.getUIBits(1),i._$italic=this.byteStream.getUIBits(1),i._$bold=this.byteStream.getUIBits(1);const n=this.byteStream.getUIBits(1);62===t&&(i._$languageCode=this.byteStream.getUI8());const l=i._$shiftJIS||2===i._$languageCode?Util.$decodeToShiftJis(o):decodeURIComponent(o);i._$fontName=this.getFontName(l),this.byteStream.byteAlign();const c=[];let b=null;if(!0==(1===n||62===t)){for(;this.byteStream.byte_offset<s;)c[c.length]=this.byteStream.getUI16();b=new Uint16Array(c)}else{for(;this.byteStream.byte_offset<s;)c[c.length]=this.byteStream.getUI8();b=new Uint8Array(c)}i._$codeTable=b,this.setFont(a,i)}getFontName(t){const e=0|t.length;switch(0===t.substr(e-1).charCodeAt(0)&&(t=t.slice(0,-1)),t){case\"_sans\":return\"_sans\";case\"_serif\":return\"_serif\";case\"_typewriter\":return\"_typewriter\";case\"_等幅\":return\"Osaka\";default:return\"_\"===t.substr(0,1)?\"sans-serif\":t}}parseDefineFontName(){this.byteStream.getUI16(),this.byteStream.getDataUntil(),this.byteStream.getDataUntil()}parseDefineText(t){const e={_$name:\"StaticText\"};e._$characterId=0|this.byteStream.getUI16(),e._$bounds=this.rect(),e._$baseMatrix=this.matrix(),e._$shapeRecords=null;const s=this.byteStream.getUI8(),a=this.byteStream.getUI8();e._$textRecords=this.getTextRecords(t,s,a),this.setCharacter(e._$characterId,e)}getTextRecords(t,e,s){const a=[];for(;0!==this.byteStream.getUI8();){this.byteStream.incrementOffset(-1,0);const i={};i.TextRecordType=this.byteStream.getUIBits(1),i.StyleFlagsReserved=this.byteStream.getUIBits(3),i.StyleFlagsHasFont=this.byteStream.getUIBits(1),i.StyleFlagsHasColor=this.byteStream.getUIBits(1),i.StyleFlagsHasYOffset=this.byteStream.getUIBits(1),i.StyleFlagsHasXOffset=this.byteStream.getUIBits(1),i.StyleFlagsHasFont&&(i.FontId=this.byteStream.getUI16()),i.StyleFlagsHasColor&&(i.TextColor=11===t?this.rgb():this.rgba()),i.StyleFlagsHasXOffset&&(i.XOffset=this.byteStream.getUI16()/20),i.StyleFlagsHasYOffset&&(i.YOffset=this.byteStream.getUI16()/20),i.StyleFlagsHasFont&&(i.TextHeight=this.byteStream.getUI16()),i.GlyphCount=this.byteStream.getUI8(),i.GlyphEntries=this.getGlyphEntries(i.GlyphCount,e,s),a[a.length]=i}return a}getGlyphEntries(t,e,s){const a=[];for(let i=0;i<t;++i)a[a.length]={GlyphIndex:this.byteStream.getUIBits(e),GlyphAdvance:this.byteStream.getSIBits(s)/20};return a}parseDefineEditText(){const t={_$ns:[\"flash\",\"text\"],_$name:\"TextField\"},e={},s=this.byteStream.getUI16();t._$characterId=s,t._$bounds=this.rect();const a=this.byteStream.getUI8(),i=a>>>7&1;t._$wordWrap=a>>>6&1,t._$multiline=a>>>5&1,t._$displayAsPassword=a>>>4&1;const r=a>>>3&1;t._$type=\"dynamic\",r||(t._$type=\"input\");const h=a>>>2&1,o=a>>>1&1,n=1&a,l=this.byteStream.getUI8(),c=l>>>7&1,b=l>>>5&1;t._$selectable=l>>>4&1,t._$border=l>>>3&1;const g=l>>>1&1,y=1&l;t._$border&&(t._$background=!0);let S=0;if(n){const s=this.byteStream.getUI16(),a=this.getFont(s);if(a){if(S=a._$shiftJIS,c){const t=this.byteStream.getDataUntil();console.log(\"TODO HasFontClass: \",t)}e._$font=a._$fontName,e._$size=this.byteStream.getUI16()/20,t._$fontId=0|s,t._$embedFonts=!(!y&&\"embedded\"!==a.fontType||t.displayAsPassword)}}if(h){const e=this.rgba();t._$textColor=(e.R<<16)+(e.G<<8)+e.B+255*e.A*16777216}if(o&&(t._$maxChars=this.byteStream.getUI16()),b){switch(this.byteStream.getUI8()){case 0:e._$align=\"left\";break;case 1:e._$align=\"right\";break;case 2:e._$align=\"center\";break;case 3:e._$align=\"justify\"}e._$leftMargin=this.byteStream.getUI16()/20,e._$rightMargin=this.byteStream.getUI16()/20,e._$indent=this.byteStream.getUI16(),e._$indent>=32768&&(e._$indent-=65536),e._$leading=this.byteStream.getUI16(),e._$leading>=32768&&(e._$leading-=65536),e._$indent/=20,e._$leading/=20}const m=this.byteStream.getDataUntil(S)+\"\";if(t._$text=\"\",i){const e=this.byteStream.getDataUntil(S);if(!0==(1===g))t._$htmlText=e,t._$initText=!0;else t._$text=e}\"\"!==m&&console.log(\"VariableName: \",m),t._$defaultTextFormat=[null,e._$font,e._$size,e._$color,e._$bold,e._$italic,e._$underline,e._$url,e._$target,e._$align,e._$leftMargin,e._$rightMargin,0,e._$leading,e._$indent],this.setCharacter(s,t)}parseDefineMorphShape(t){const e={};e.CharacterId=this.byteStream.getUI16(),e.StartBounds=this.rect(),e.EndBounds=this.rect(),84===t&&(e.StartEdgeBounds=this.rect(),e.EndEdgeBounds=this.rect(),this.byteStream.getUIBits(6),e.UsesNonScalingStrokes=this.byteStream.getUIBits(1),e.UsesScalingStrokes=this.byteStream.getUIBits(1));const s=this.byteStream.getUI32(),a=this.byteStream.byte_offset+s;e.MorphFillStyles=this.fillStyleArray(t),e.MorphLineStyles=this.lineStyleArray(t),e.StartEdges=this.shapeWithStyle(t),this.byteStream.byte_offset!==a&&(this.byteStream.byte_offset=a),e.EndEdges=this.shapeWithStyle(t);const i={x:0,y:0},r={x:0,y:0},h=e.StartEdges.ShapeData.records,o=e.EndEdges.ShapeData.records,n=h.length,l=o.length;let c=Math.max(n,l);const b=[],g=[];let y=0,S=0;for(;c>y||c>S;){const t=h[y++],e=o[S++];if(-1===t&&-1===e)break;switch(!0){case-1===t:case void 0===t:if(e){const t=o[S++];if(g.push(1,t),b.push(1,t),t){const t=o[S++],e=o[S++];g.push(t,e),b.push(t,e),console.log(\"TODO Parse Morph NewStyles\")}const e=o[S++];if(g.push(e),b.push(e),e){const t=o[S++],e=o[S++];r.x=t,r.y=e,g.push(t,e),b.push(t,e)}const s=o[S++];if(g.push(s),b.push(s),s){const t=o[S++];g.push(t),b.push(t)}const a=o[S++];if(g.push(a),b.push(a),a){const t=o[S++];g.push(t),b.push(t)}const i=o[S++];if(g.push(i),b.push(i),i){const t=o[S++];g.push(t),b.push(t)}break}if(o[S++]){const t=o[S++],e=o[S++],s=o[S++],a=o[S++];r.x+=t+s,r.y+=e+a,g.push(0,1,t,e,s,a),b.push(0,1,t,e,s,a)}else{const t=o[S++],e=o[S++];r.x+=t,r.y+=e,g.push(0,0,t,e),b.push(0,0,t,e)}break;case-1===e:case void 0===e:if(t){const t=h[y++];if(g.push(1,t),b.push(1,t),t){const t=h[y++],e=h[y++];g.push(t,e),b.push(t,e),console.log(\"TODO Parse Morph NewStyles\")}const e=h[y++];if(g.push(e),b.push(e),e){const t=h[y++],e=h[y++];i.x=t,i.y=e,g.push(t,e),b.push(t,e)}const s=h[y++];if(g.push(s),b.push(s),s){const t=h[y++];g.push(t),b.push(t)}const a=h[y++];if(g.push(a),b.push(a),a){const t=h[y++];g.push(t),b.push(t)}const r=h[y++];if(g.push(r),b.push(r),r){const t=h[y++];g.push(t),b.push(t)}break}if(h[y++]){const t=h[y++],e=h[y++],s=h[y++],a=h[y++];i.x+=t+s,i.y+=e+a,g.push(0,1,t,e,s,a),b.push(0,1,t,e,s,a)}else{const t=h[S++],e=h[S++];i.x+=t,i.y+=e,g.push(0,0,t,e),b.push(0,0,t,e)}break;case 1===t&&1===e:const s=h[y++];if(b.push(1,s),s){const t=h[y++],e=h[y++];b.push(t,e),console.log(\"TODO Parse Morph NewStyles\")}const a=h[y++];if(b.push(a),a){const t=h[y++],e=h[y++];i.x=t,i.y=e,b.push(t,e)}const n=h[y++];if(b.push(n),n){const t=h[y++];b.push(t)}const l=h[y++];if(b.push(l),l){const t=h[y++];b.push(t)}const c=h[y++];if(b.push(c),c){const t=h[y++];b.push(t)}const m=o[S++];if(g.push(1,m),m){const t=o[S++],e=o[S++];g.push(t,e),console.log(\"TODO Parse Morph NewStyles\")}const f=o[S++];if(g.push(f),f){const t=o[S++],e=o[S++];i.x=t,i.y=e,g.push(t,e)}const d=o[S++];if(g.push(d),d){const t=o[S++];g.push(t)}const Y=o[S++];if(g.push(Y),Y){const t=o[S++];g.push(t)}const I=o[S++];if(g.push(I),I){const t=o[S++];g.push(t)}break;case 0===t&&0===e:if(h[y++]){const t=h[y++],e=h[y++],s=h[y++],a=h[y++];i.x=s,i.y=a,b.push(0,1,t,e,s,a)}else{const t=h[y++],e=h[y++];i.x=t,i.y=e,b.push(0,0,t,e)}if(o[S++]){const t=o[S++],e=o[S++],s=o[S++],a=o[S++];r.x=s,r.y=a,g.push(0,1,t,e,s,a)}else{const t=o[S++],e=o[S++];r.x=t,r.y=e,g.push(0,0,t,e)}break;case 1===t&&0===e:{const t=h[y++];if(g.push(1,t),b.push(1,t),t){const t=h[y++],e=h[y++];g.push(t,e),b.push(t,e),console.log(\"TODO Parse Morph NewStyles\")}const e=h[y++];if(g.push(e),b.push(e),e){const t=h[y++],e=h[y++];i.x=t,i.y=e,g.push(t,e),b.push(t,e)}const s=h[y++];if(g.push(s),b.push(s),s){const t=h[y++];g.push(t),b.push(t)}const a=h[y++];if(g.push(a),b.push(a),a){const t=h[y++];g.push(t),b.push(t)}const r=h[y++];if(g.push(r),b.push(r),r){const t=h[y++];g.push(t),b.push(t)}--S}break;case 0===t&&1===e:{const t=o[S++];if(g.push(1,t),b.push(1,t),t){const t=o[S++],e=o[S++];g.push(t,e),b.push(t,e),console.log(\"TODO Parse Morph NewStyles\")}const e=o[S++];if(g.push(e),b.push(e),e){const t=o[S++],e=o[S++];r.x=t,r.y=e,g.push(t,e),b.push(t,e)}const s=o[S++];if(g.push(s),b.push(s),s){const t=o[S++];g.push(t),b.push(t)}const a=o[S++];if(g.push(a),b.push(a),a){const t=o[S++];g.push(t),b.push(t)}const i=o[S++];if(g.push(i),b.push(i),i){const t=o[S++];g.push(t),b.push(t)}--y}}}b.push(-1),g.push(-1),e.StartEdges.ShapeData.records=new Int32Array(b),e.EndEdges.ShapeData.records=new Int32Array(g),this.setCharacter(e.CharacterId,{_$ns:[\"flash\",\"display\"],_$name:\"MorphShape\",_$characterId:e.CharacterId,_$endBounds:e.EndBounds,_$endEdges:e.EndEdges,_$fillStyles:e.MorphFillStyles,_$lineStyles:e.MorphLineStyles,_$startBounds:e.StartBounds,_$startEdges:e.StartEdges,_$shapes:null,_$frameData:[],_$frameCreated:!1},[e.StartEdges.ShapeData.records.buffer,e.EndEdges.ShapeData.records.buffer])}parseFrameLabel(){return{name:this.byteStream.getDataUntil(),frame:0}}parseDefineButton(t,e){const s=this.byteStream.byte_offset+e|0,a={_$ns:[\"flash\",\"display\"],_$name:\"SimpleButton\"};a._$characterId=0|this.byteStream.getUI16();let i=0;7!==t&&(this.byteStream.getUIBits(7),a._$trackAsMenu=!!this.byteStream.getUIBits(1),i=0|this.byteStream.getUI16()),a._$characters=this.buttonCharacters(s),7===t?(i=s-this.byteStream.byte_offset|0,this.byteStream.byte_offset+=i):i>0&&(a._$actions=this.buttonActions(s)),this.setCharacter(a._$characterId,a),this.byteStream.byte_offset!==s&&(this.byteStream.byte_offset=0|s)}buttonCharacters(t){const e=[];for(;0!==this.byteStream.getUI8();){this.byteStream.incrementOffset(-1,0);const s=0|this.byteStream.byte_offset,a=this.buttonRecord();if(this.byteStream.byte_offset>t){this.byteStream.byte_offset=0|s;break}e[e.length]=a}return e}buttonRecord(){this.byteStream.getUIBits(2);const t={};return t.PlaceFlagHasBlendMode=this.byteStream.getUIBits(1),t.PlaceFlagHasFilterList=this.byteStream.getUIBits(1),t.ButtonStateHitTest=this.byteStream.getUIBits(1),t.ButtonStateDown=this.byteStream.getUIBits(1),t.ButtonStateOver=this.byteStream.getUIBits(1),t.ButtonStateUp=this.byteStream.getUIBits(1),t.CharacterId=this.byteStream.getUI16(),t.Depth=this.byteStream.getUI16(),t.PlaceFlagHasMatrix=1,t.Matrix=this.matrix(),t.ColorTransform=this.colorTransform(),t.PlaceFlagHasColorTransform=void 0===t.ColorTransform?0:1,t.PlaceFlagHasBlendMode&&(t.BlendMode=this.byteStream.getUI8()),t.PlaceFlagHasFilterList&&(t.SurfaceFilterList=this.getFilterList()),t.PlaceFlagHasRatio=0,t.PlaceFlagHasClipDepth=0,t.Sound=null,t}buttonActions(t){for(;;){const e={},s=0|this.byteStream.byte_offset,a=this.byteStream.getUI16();e.CondIdleToOverDown=this.byteStream.getUIBits(1),e.CondOutDownToIdle=this.byteStream.getUIBits(1),e.CondOutDownToOverDown=this.byteStream.getUIBits(1),e.CondOverDownToOutDown=this.byteStream.getUIBits(1),e.CondOverDownToOverUp=this.byteStream.getUIBits(1),e.CondOverUpToOverDown=this.byteStream.getUIBits(1),e.CondOverUpToIdle=this.byteStream.getUIBits(1),e.CondIdleToOverUp=this.byteStream.getUIBits(1),e.CondKeyPress=this.byteStream.getUIBits(7),e.CondOverDownToIdle=this.byteStream.getUIBits(1);const i=t-this.byteStream.byte_offset+1|0;if(this.byteStream.byte_offset+=i,!a)break;this.byteStream.byte_offset=s+a|0}return[]}parsePlaceObject(t,e){const s=this.byteStream.byte_offset,a={};if(a.tagType=t,4===t)return a.CharacterId=this.byteStream.getUI16(),a.Depth=this.byteStream.getUI16(),a.Matrix=this.matrix(),a.PlaceFlagHasMatrix=1,this.byteStream.byteAlign(),this.byteStream.byte_offset-s<e&&(a.ColorTransform=this.colorTransform(),a.PlaceFlagHasColorTransform=1),this.byteStream.byteAlign(),this.byteStream.byte_offset=s+e,a;const i=this.swfVersion;if(a.PlaceFlagHasClipActions=this.byteStream.getUIBits(1),a.PlaceFlagHasClipDepth=this.byteStream.getUIBits(1),a.PlaceFlagHasName=this.byteStream.getUIBits(1),a.PlaceFlagHasRatio=this.byteStream.getUIBits(1),a.PlaceFlagHasColorTransform=this.byteStream.getUIBits(1),a.PlaceFlagHasMatrix=this.byteStream.getUIBits(1),a.PlaceFlagHasCharacter=this.byteStream.getUIBits(1),a.PlaceFlagMove=this.byteStream.getUIBits(1),70===t&&(this.byteStream.getUIBits(1),a.PlaceFlagOpaqueBackground=this.byteStream.getUIBits(1),a.PlaceFlagHasVisible=this.byteStream.getUIBits(1),a.PlaceFlagHasImage=this.byteStream.getUIBits(1),a.PlaceFlagHasClassName=this.byteStream.getUIBits(1),a.PlaceFlagHasCacheAsBitmap=this.byteStream.getUIBits(1),a.PlaceFlagHasBlendMode=this.byteStream.getUIBits(1),a.PlaceFlagHasFilterList=this.byteStream.getUIBits(1)),a.Depth=this.byteStream.getUI16(),a.PlaceFlagHasClassName&&(a.ClassName=this.byteStream.getDataUntil(),console.log(\"TODO \",a.ClassName)),a.PlaceFlagHasCharacter&&(a.CharacterId=this.byteStream.getUI16()),a.PlaceFlagHasMatrix&&(a.Matrix=this.matrix()),a.PlaceFlagHasColorTransform&&(a.ColorTransform=this.colorTransform()),a.PlaceFlagHasRatio&&(a.Ratio=this.byteStream.getUI16()),a.PlaceFlagHasName&&(a.Name=this.byteStream.getDataUntil()),a.PlaceFlagHasClipDepth&&(a.ClipDepth=this.byteStream.getUI16()),70===t&&(a.PlaceFlagHasFilterList&&(a.SurfaceFilterList=this.getFilterList()),a.PlaceFlagHasBlendMode&&(a.BlendMode=this.byteStream.getUI8()),a.PlaceFlagHasCacheAsBitmap&&(a.BitmapCache=this.byteStream.getUI8()),a.PlaceFlagHasVisible&&(a.Visible=this.byteStream.getUI8()),a.PlaceFlagOpaqueBackground&&(a.BackgroundColor=this.rgba())),a.PlaceFlagHasClipActions){this.byteStream.getUI16(),a.AllEventFlags=this.parseClipEventFlags();const t=s+e;for(;this.byteStream.byte_offset<t;){const e=this.parseClipActionRecord(t);if(t<=this.byteStream.byte_offset)break;if(!(i<=5?this.byteStream.getUI16():this.byteStream.getUI32()))break;this.byteStream.byte_offset-=i<=5?2:4,e.KeyCode&&(this.byteStream.byte_offset-=1)}}return this.byteStream.byteAlign(),this.byteStream.byte_offset=s+e,a}parseClipActionRecord(t){const e={},s=this.parseClipEventFlags();if(t>this.byteStream.byte_offset){const t=this.byteStream.getUI32();s.keyPress&&(e.KeyCode=this.byteStream.getUI8()),this.byteStream.byte_offset+=t}return e}parseClipEventFlags(){const t=this.swfVersion,e={};return e.keyUp=this.byteStream.getUIBits(1),e.keyDown=this.byteStream.getUIBits(1),e.mouseUp=this.byteStream.getUIBits(1),e.mouseDown=this.byteStream.getUIBits(1),e.mouseMove=this.byteStream.getUIBits(1),e.unload=this.byteStream.getUIBits(1),e.enterFrame=this.byteStream.getUIBits(1),e.load=this.byteStream.getUIBits(1),t>=6&&(e.dragOver=this.byteStream.getUIBits(1),e.rollOut=this.byteStream.getUIBits(1),e.rollOver=this.byteStream.getUIBits(1),e.releaseOutside=this.byteStream.getUIBits(1),e.release=this.byteStream.getUIBits(1),e.press=this.byteStream.getUIBits(1),e.initialize=this.byteStream.getUIBits(1)),e.data=this.byteStream.getUIBits(1),t>=6&&(this.byteStream.getUIBits(5),e.construct=this.byteStream.getUIBits(1),e.keyPress=this.byteStream.getUIBits(1),e.dragOut=this.byteStream.getUIBits(1),this.byteStream.getUIBits(8)),this.byteStream.byteAlign(),e}getFilterList(){const t=0|this.byteStream.getUI8(),e=[];for(let s=0;s<t;++s){const t=this.getFilter();t&&(e[e.length]=t)}return e.length?e:null}getFilter(){switch(0|this.byteStream.getUI8()){case 0:return this.dropShadowFilter();case 1:return this.blurFilter();case 2:return this.glowFilter();case 3:return this.bevelFilter();case 4:return this.gradientGlowFilter();case 5:return this.convolutionFilter();case 6:return this.colorMatrixFilter();case 7:return this.gradientBevelFilter()}}dropShadowFilter(){const t={},e=this.rgba(),s=e.A,a=e.R<<16|e.G<<8|e.B,i=this.byteStream.getUI32()/65536,r=this.byteStream.getUI32()/65536,h=this.byteStream.getUI32()/65536*Util.$Rad2Deg,o=this.byteStream.getUI32()/65536,n=this.byteStream.getFloat16()/256,l=!!this.byteStream.getUIBits(1),c=!!this.byteStream.getUIBits(1),b=!this.byteStream.getUIBits(1),g=this.byteStream.getUIBits(5);return t._$ns=[\"flash\",\"filters\"],t._$name=\"DropShadowFilter\",t.params=[null,o,h,a,s,i,r,n,g,l,c,b],t}blurFilter(){const t={},e=this.byteStream.getUI32()/65536,s=this.byteStream.getUI32()/65536,a=this.byteStream.getUIBits(5);return this.byteStream.getUIBits(3),t._$ns=[\"flash\",\"filters\"],t._$name=\"BlurFilter\",t.params=[null,e,s,a],t}glowFilter(){const t={},e=this.rgba(),s=e.A,a=e.R<<16|e.G<<8|e.B,i=this.byteStream.getUI32()/65536,r=this.byteStream.getUI32()/65536,h=this.byteStream.getFloat16()/256,o=!!this.byteStream.getUIBits(1),n=!!this.byteStream.getUIBits(1);this.byteStream.getUIBits(1);const l=this.byteStream.getUIBits(5);return t._$ns=[\"flash\",\"filters\"],t._$name=\"GlowFilter\",t.params=[null,a,s,i,r,h,l,o,n],t}bevelFilter(){const t={};let e=this.rgba();const s=e.A,a=e.R<<16|e.G<<8|e.B;e=this.rgba();const i=e.A,r=e.R<<16|e.G<<8|e.B,h=this.byteStream.getUI32()/65536,o=this.byteStream.getUI32()/65536,n=this.byteStream.getUI32()/65536*Util.$Rad2Deg,l=this.byteStream.getUI32()/65536,c=this.byteStream.getFloat16()/256,b=!!this.byteStream.getUIBits(1),g=!!this.byteStream.getUIBits(1);this.byteStream.getUIBits(1);const y=this.byteStream.getUIBits(1),S=this.byteStream.getUIBits(4);let m=\"inner\";return b||(m=y?\"full\":\"outer\"),t._$ns=[\"flash\",\"filters\"],t._$name=\"BevelFilter\",t.params=[null,l,n,a,s,r,i,h,o,c,S,m,g],t}gradientGlowFilter(){const t={},e=0|this.byteStream.getUI8(),s=[],a=[];for(let t=0;t<e;++t){const t=this.rgba();a[a.length]=t.A,s[s.length]=t.R<<16|t.G<<8|t.B}const i=[];for(let t=0;t<e;++t)i[i.length]=+this.byteStream.getUI8()/255;const r=this.byteStream.getUI32()/65536,h=this.byteStream.getUI32()/65536,o=this.byteStream.getUI32()/65536*Util.$Rad2Deg,n=this.byteStream.getUI32()/65536,l=this.byteStream.getFloat16()/256,c=!!this.byteStream.getUIBits(1),b=!!this.byteStream.getUIBits(1);this.byteStream.getUIBits(1);const g=this.byteStream.getUIBits(1),y=this.byteStream.getUIBits(4);let S=\"inner\";return c||(S=g?\"full\":\"outer\"),t._$ns=[\"flash\",\"filters\"],t._$name=\"GradientGlowFilter\",t.params=[null,n,o,s,a,i,r,h,l,y,S,b],t}convolutionFilter(){const t={},e=this.byteStream.getUI8(),s=this.byteStream.getUI8(),a=this.byteStream.getFloat32,i=this.byteStream.getFloat32,r=e*s,h=[];for(let t=0;t<r;++t)h[h.length]=this.byteStream.getFloat32();const o=this.rgba();this.byteStream.getUIBits(6);const n=!!this.byteStream.getUIBits(1),l=!!this.byteStream.getUIBits(1);return t._$ns=[\"flash\",\"filters\"],t._$name=\"ConvolutionFilter\",t.params=[null,e,s,h,a,i,l,n,o],t}gradientBevelFilter(){const t={},e=0|this.byteStream.getUI8(),s=[],a=[];for(let t=0;t<e;++t){const t=this.rgba();a[a.length]=t.A,s[s.length]=t.R<<16|t.G<<8|t.B}const i=[];for(let t=0;t<e;++t)i[i.length]=+this.byteStream.getUI8()/255;const r=this.byteStream.getUI32()/65536,h=this.byteStream.getUI32()/65536,o=this.byteStream.getUI32()/65536*Util.$Rad2Deg,n=this.byteStream.getUI32()/65536,l=this.byteStream.getFloat16()/256,c=!!this.byteStream.getUIBits(1),b=!!this.byteStream.getUIBits(1);this.byteStream.getUIBits(1);const g=this.byteStream.getUIBits(1),y=this.byteStream.getUIBits(4);let S=\"inner\";return c||(S=g?\"full\":\"outer\"),t._$ns=[\"flash\",\"filters\"],t._$name=\"GradientBevelFilter\",t.params=[null,n,o,s,a,i,r,h,l,y,S,b],t}colorMatrixFilter(){const t={},e=[];for(let t=0;t<20;t++)e[e.length]=this.byteStream.getFloat32();return t._$ns=[\"flash\",\"filters\"],t._$name=\"ColorMatrixFilter\",t.params=[null,e],t}colorTransform(){this.byteStream.byteAlign();const t=[1,1,1,1,0,0,0,0],e=this.byteStream.getUIBits(6),s=e>>5,a=15&e;return e>>4&1&&(t[0]=this.byteStream.getSIBits(a)/256,t[1]=this.byteStream.getSIBits(a)/256,t[2]=this.byteStream.getSIBits(a)/256,t[3]=this.byteStream.getSIBits(a)/256),s&&(t[4]=this.byteStream.getSIBits(a),t[5]=this.byteStream.getSIBits(a),t[6]=this.byteStream.getSIBits(a),t[7]=this.byteStream.getSIBits(a)),t}parseSoundStreamHead(t){const e={};e.tagType=t,this.byteStream.getUIBits(4),e.PlaybackSoundRate=this.byteStream.getUIBits(2),e.PlaybackSoundSize=this.byteStream.getUIBits(1),e.PlaybackSoundType=this.byteStream.getUIBits(1),e.StreamSoundCompression=this.byteStream.getUIBits(4),e.StreamSoundRate=this.byteStream.getUIBits(2),e.StreamSoundSize=this.byteStream.getUIBits(1),e.StreamSoundType=this.byteStream.getUIBits(1),e.StreamSoundSampleCount=this.byteStream.getUI16(),2===e.StreamSoundCompression&&(e.LatencySeek=this.byteStream.getSIBits(2))}parseDefineSound(t){const e=this.byteStream.byte_offset,s=this.byteStream.getUI16();this.byteStream.getUIBits(4),this.byteStream.getUIBits(2),this.byteStream.getUIBit(),this.byteStream.getUIBit(),this.byteStream.getUI32();const a=t-(this.byteStream.byte_offset-e),i=this.byteStream.byte_offset,r=this.byteStream.data.slice(i,i+a),h={_$characterId:s,_$name:\"Sound\",_$data:null,_$buffer:r};this.byteStream.byte_offset=e+t,this.setCharacter(s,h,[r.buffer])}parseStartSound(t){const e={};return e.SoundId=this.byteStream.getUI16(),89===t&&(e.SoundClassName=this.byteStream.getDataUntil()),e.SoundInfo=this.parseSoundInfo(),e}parseDefineButtonSound(){const t=this.byteStream.getUI16(),e=this.getCharacter(t);for(let t=0;t<4;t++){const s=this.byteStream.getUI16();if(s){const a=this.parseSoundInfo();switch(t){case 0:e.ButtonStateUpSoundInfo=a,e.ButtonStateUpSoundId=s;break;case 1:e.ButtonStateOverSoundInfo=a,e.ButtonStateOverSoundId=s;break;case 2:e.ButtonStateDownSoundInfo=a,e.ButtonStateDownSoundId=s;break;case 3:e.ButtonStateHitTestSoundInfo=a,e.ButtonStateHitTestSoundId=s}}}this.setCharacter(t,e)}parseSoundInfo(){this.byteStream.getUIBits(2);const t={};if(t.SyncStop=this.byteStream.getUIBit(),t.SyncNoMultiple=this.byteStream.getUIBit(),t.HasEnvelope=this.byteStream.getUIBit(),t.HasLoops=this.byteStream.getUIBit(),t.HasOutPoint=this.byteStream.getUIBit(),t.HasInPoint=this.byteStream.getUIBit(),t.HasInPoint&&(t.InPoint=this.byteStream.getUI32()),t.HasOutPoint&&(t.OutPoint=this.byteStream.getUI32()),t.HasLoops&&(t.LoopCount=this.byteStream.getUI16()),t.HasEnvelope){const e=this.byteStream.getUI8(),s=[];for(let t=0;t<e;++t)s[t]={Pos44:this.byteStream.getUI32(),LeftLevel:this.byteStream.getUI16(),RightLevel:this.byteStream.getUI16()};t.EnvPoints=e,t.EnvelopeRecords=s}return t}parseDefineFontAlignZones(){const t=this.byteStream.getUI16(),e=this.getFont(t)||{};e._$CSMTableHint=this.byteStream.getUIBits(2),this.byteStream.getUIBits(6);const s=0|e._$numGlyphs,a=[];for(let t=0;t<s;++t){const e=this.byteStream.getUI8(),s=[];for(let t=0;t<e;++t)s.push(this.byteStream.getFloat16()),s.push(this.byteStream.getFloat16());this.byteStream.getUIBits(6),this.byteStream.getUIBits(1),this.byteStream.getUIBits(1),a[t]=s}this.byteStream.byteAlign(),e._$zoneTable=a,this.setFont(t,e)}parseCSMTextSettings(t){const e=this.byteStream.getUI16(),s={};s.tagType=t,s.UseFlashType=this.byteStream.getUIBits(2),s.GridFit=this.byteStream.getUIBits(3),this.byteStream.getUIBits(3),s.Thickness=this.byteStream.getUI32(),s.Sharpness=this.byteStream.getUI32(),this.byteStream.getUI8(),this.setTextSetting(e,s)}parseSoundStreamBlock(t,e){const s={};s.tagType=t,s.compressed=this.byteStream.getData(e)}parseDefineScalingGrid(){const t=this.byteStream.getUI16(),e=this.rect();this.setGrid(t,e)}postCharacter(t,e){globalThis.postMessage({infoKey:\"_$characters\",characters:t},e),t.length=0,e&&(e.length=0)}}Util.$swfParser=new SwfParser,this.addEventListener(\"message\",function(t){const e=Util.$swfParser;e.version=t.data.version,e.byteStream.setData(t.data.buffer),e.byteStream.byte_offset=t.data.offset;const s=Util.$createMovieClip();e.parseTags(t.data.buffer.length,s),e.postData(s),e.clear()});"], { "type": "text/javascript" })
);
Util.$parserWorker     = null;
Util.$parserQueues     = [];
Util.$parserWorkerWait = false;

/**
 * @param  {object} event
 * @return void
 * @static
 */
Util.$unlzmaHandler = function (event)
{
    // event end
    event.target.onmessage = null;

    // next
    if (Util.$unlzmaQueues.length) {

        const object = Util.$unlzmaQueues.shift();

        const worker = new Worker(Util.$unlzmaWorkerURL);

        worker.onmessage = Util.$unlzmaHandler.bind(object);

        const data = object._$byteStream._$buffer;
        worker.postMessage({
            "fileSize": object.fileSize,
            "mode":     object.mode,
            "buffer":   data
        }, [data.buffer]);

    } else {

        Util.$unlzmaWorkerActive = false;

    }

    // setup
    this._$byteStream._$buffer = event.data;
    this.parseAndBuild();
};

/**
 * @description 全てのエリアのコピーを初期化
 * @return {void}
 * @static
 */
Util.$allClearCopy = () =>
{
    Util.$timelineMenu.clearCopy();
    Util.$screenMenu.clearCopy();
    Util.$libraryMenu.clearCopy();
};

/**
 * @param  {Uint8Array} data
 * @return {string|null}
 * @static
 */
Util.$getImageType = (data) =>
{
    switch (true) {

        // JPEG
        case data[0] === 0xff && data[1] === 0xd8:
            return "jpeg";

        // GIF
        case data[0] === 0x47 && data[1] === 0x49 && data[2] === 0x46:
            return "gif";

        // PNG
        case data[0] === 0x89 && data[1] === 0x50 &&
            data[2] === 0x4E && data[3] === 0x47 &&
            data[4] === 0x0D && data[5] === 0x0A &&
            data[6] === 0x1A && data[7] === 0x0A:
            return "png";

        // BMP
        case data[0] === 0x42 && data[1] === 0x4d:
            return "bmp";

        default:
            return null;

    }
};

/**
 * @return {void}
 * @static
 */
Util.$jpegDecodeHandler = () =>
{
    const image  = this.image;
    const width  = image.width;
    const height = image.height;

    const canvas  = document.createElement("canvas");
    canvas.width  = width;
    canvas.height = height;
    const context = canvas.getContext("2d");

    context.drawImage(image, 0, 0, width, height);
    const buffer = new Uint8Array(context
        .getImageData(0, 0, width, height)
        .data);

    // clear
    this.jpegData = null;
    this.image    = null;

    const workSpace = Util.$currentWorkSpace();
    const instance  = workSpace.getLibrary(this.libraryId);
    instance.width  = width;
    instance.height = height;

    if (this.isAlpha) {

        // set
        this.buffer = buffer;
        this.width  = width;
        this.height = height;

        if (Util.$unzipWorkerActive) {
            Util.$unzipQueues.push(this);
            return ;
        }

        Util.$unzipWorkerActive = true;

        if (!Util.$unzipWorker) {
            Util.$unzipWorker = new Worker(Util.$unzipURL);
        }

        const worker = Util.$unzipWorker;
        worker.onmessage = Util.$unzipHandler.bind(this);
        worker.postMessage(this, [
            this.buffer.buffer,
            this.alphaData.buffer
        ]);

    } else {

        instance._$buffer = buffer;

    }
};

/**
 * @type {Map}
 */
Util.$characters = new Map();
Util.$symbols    = new Map();
Util.$fonts      = new Map();
Util.$texts      = new Map();

/**
 * @param  {object} event
 * @return void
 * @static
 */
Util.$parserHandler = function (event)
{
    const worker = event.target;
    switch (event.data.infoKey) {

        case "character":
            {
                const character = event.data.piece;

                const workSpace = Util.$currentWorkSpace();
                const id = workSpace.nextLibraryId;
                character.libraryId = id;

                switch (character._$name) {

                    case "Shape":
                        {
                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.SHAPE, `Shape_${id}`, id);

                            object.recodes  = Util.$vtc.convert(character._$records);
                            object.inBitmap = object.recodes.pop();
                            object.bounds   = {
                                "xMin": character._$bounds.xMin,
                                "xMax": character._$bounds.xMax,
                                "yMin": character._$bounds.yMin,
                                "yMax": character._$bounds.yMax
                            };

                            const shape = workSpace.addLibrary(object);
                            console.log(shape, object.recodes);
                            if (this._$folderId) {
                                shape.folderId = this._$folderId;
                            }

                            Util.$characters.set(character._$characterId, id);
                        }
                        break;

                    case "MovieClip":
                        {
                            for (let idx = 0; idx < character._$dictionary.length; ++idx) {
                                const object = character._$dictionary[idx];
                                object.LibraryId = Util.$characters.get(object.CharacterId);
                            }

                            const name = character._$characterId
                                ? `MovieClip_${id}`
                                : this._$fileName;

                            let libraryId = !character._$characterId && this._$libraryId
                                ? this._$libraryId
                                : id;

                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.MOVIE_CLIP, name, libraryId);

                            // create MovieClip
                            const movieClip = workSpace.addLibrary(object);
                            if (this._$folderId) {
                                movieClip.folderId = this._$folderId;
                            }

                            // create layer
                            let clipMap = new Map();
                            let layerArray = [];
                            for (let idx = 0; idx < character._$dictionary.length; ++idx) {
                                const tag = character._$dictionary[idx];

                                if (layerArray.indexOf(tag.Depth) !== -1) {
                                    continue;
                                }
                                layerArray.push(tag.Depth);

                                if (tag.ClipDepth) {
                                    clipMap.set(tag.Depth, idx);
                                }

                            }

                            layerArray.sort((a, b) =>
                            {
                                switch (true) {

                                    case a > b:
                                        return 1;

                                    case a < b:
                                        return -1;

                                    default:
                                        return 0;

                                }
                            });

                            // adj clips
                            if (clipMap.size) {

                                for (const [depth, index] of clipMap) {

                                    const moveArray = [];

                                    const tag = character._$dictionary[index];
                                    for (let idx = 0; character._$dictionary.length > idx; ++idx) {

                                        const target = character._$dictionary[idx];
                                        if (target.Depth > tag.ClipDepth) {
                                            break;
                                        }

                                        if (target.Depth > depth) {
                                            moveArray.push(target);
                                        }
                                    }

                                    for (let idx = 0; idx < moveArray.length; ++idx) {

                                        const target = moveArray[idx];

                                        const index = layerArray.indexOf(target.Depth);
                                        const depth = layerArray.splice(index, 1)[0];
                                        const insertIndex = layerArray.indexOf(tag.Depth);

                                        layerArray.splice(insertIndex, 0, depth);
                                    }

                                }
                            }

                            let maskId     = -1;
                            let clipDepth  = -1;
                            const index    = layerArray.length - 1;
                            const layerMap = new Map();
                            const layers   = [];
                            for (let idx = index; idx > -1; --idx) {

                                const layer = new Layer();
                                layer.name  = `Layer_${index - idx}`;

                                const depth = layerArray[idx];
                                if (clipMap.size) {

                                    if (clipDepth > -1) {
                                        if (depth > clipDepth) {
                                            layer.mode   = LayerMode.MASK_IN;
                                            layer.maskId = maskId;
                                        } else {
                                            maskId    = -1;
                                            clipDepth = -1;
                                        }
                                    }

                                    if (clipMap.has(depth)) {
                                        clipDepth  = depth;
                                        maskId     = index - idx;
                                        layer.mode = LayerMode.MASK;
                                        layer.lock = true;
                                    }
                                }

                                layers.push(layer);
                                layerMap.set(depth, layer);
                            }

                            for (let idx = 0; idx < layerArray.length; ++idx) {
                                movieClip.setLayer(idx, layers[idx]);
                            }

                            // setup
                            const characters = [];
                            const totalFrame = character._$controller.length - 1;
                            for (let idx = 0; idx < character._$dictionary.length; ++idx) {

                                const tag = character._$dictionary[idx];

                                const instance = new Character();
                                instance.libraryId  = tag.LibraryId;
                                instance.startFrame = tag.StartFrame;
                                instance.endFrame   = tag.EndFrame || totalFrame + 1;
                                instance.name       = tag.Name || "";

                                characters.push(instance);
                            }

                            const dup = new Map();
                            for (let frame = 1; frame < character._$controller.length; ++frame) {

                                const controller = character._$controller[frame];
                                for (let idx = 0; idx < controller.length; ++idx) {

                                    const id  = controller[idx];
                                    const tag = character._$dictionary[id];

                                    const layer = layerMap.get(tag.Depth);

                                    const instance = characters[id];
                                    if (!dup.has(id)) {
                                        dup.set(id, -1);
                                        layer.addCharacter(instance);
                                    }

                                    const nextId    = character._$placeMap[frame][tag.Depth];
                                    const currentId = dup.get(id);
                                    if (currentId !== nextId) {
                                        const placeObject = character._$placeObjects[nextId];

                                        instance.setPlace(frame, {
                                            "frame": frame,
                                            "depth": 0,
                                            "matrix": placeObject.matrix,
                                            "colorTransform": placeObject.colorTransform,
                                            "blendMode": placeObject.blendMode,
                                            "filter": placeObject.filters ? placeObject.filters : [],
                                            "loop": Util.$getDefaultLoopConfig()
                                        });

                                        dup.set(id, nextId);
                                    }
                                }
                            }

                            for (let idx = 0; idx < layers.length; ++idx) {

                                const empty = {
                                    "startFrame": -1
                                };

                                const layer = layers[idx];
                                for (let frame = 1; frame <= totalFrame; ++frame) {

                                    const characters = layer.getActiveCharacter(frame);

                                    // 空白のフレーム処理
                                    if (!characters.length) {

                                        if (empty.startFrame === -1) {
                                            empty.startFrame = frame;
                                        }

                                    } else {

                                        // 空白のフレームがあれば登録して初期化
                                        if (empty.startFrame > 0) {
                                            layer.addEmptyCharacter(new EmptyCharacter({
                                                "startFrame": empty.startFrame,
                                                "endFrame": frame
                                            }));

                                            // 初期化
                                            empty.startFrame = -1;
                                        }

                                    }
                                }
                            }

                            // 連続するplace objectをtweenに変換する
                            for (let idx = 0; idx < layers.length; ++idx) {

                                const layer = layers[idx];

                                const totalFrame = layer.totalFrame;
                                for (let frame = 1; totalFrame > frame; ) {

                                    const characters = layer.getActiveCharacter(frame);
                                    if (!characters.length || characters.length > 2) {
                                        frame++;
                                        continue;
                                    }

                                    const character = characters[0];
                                    const range = character.getRange(frame);

                                    // 幅が1フレーム以上なら次のレンジに移動
                                    if (range.endFrame - range.startFrame !== 1) {
                                        frame = range.endFrame;
                                        continue;
                                    }

                                    // キーフレームが終了していれば次のレイヤーへ
                                    if (frame + 1 >= totalFrame) {
                                        break;
                                    }

                                    if (!character.hasPlace(frame + 1)) {
                                        frame++;
                                        continue;
                                    }

                                    const startFrame = frame;
                                    for (;;) {

                                        // 次のフレームにキーフレームがなければ終了
                                        if (!character.hasPlace(frame + 1)) {
                                            if (frame - startFrame > 2) {
                                                character.setTween(startFrame, {
                                                    "method": "linear",
                                                    "curve": [],
                                                    "custom": Util.$tweenController.createEasingObject(),
                                                    "startFrame": startFrame,
                                                    "endFrame": frame
                                                });

                                                // キーフレームにtweenの設定を追加
                                                for (let tweenFrame = startFrame; frame > tweenFrame; ++tweenFrame) {
                                                    character.getPlace(tweenFrame).tweenFrame = startFrame;
                                                }
                                            }
                                            break;
                                        }

                                        frame++;

                                        // フレームが終了したら次のレイヤーに
                                        if (frame >= totalFrame) {
                                            break;
                                        }
                                    }

                                }

                            }

                            // ラベルの取り込み
                            for (let idx = 0; idx < character._$labels.length; ++idx) {

                                const object = character._$labels[idx];

                                movieClip._$labels.set(object.frame, object.label);

                            }

                            // 音声の取り込み
                            for (let idx = 0; idx < character._$sounds.length; ++idx) {

                                const soundInfo = character._$sounds[idx];

                                const sounds = [];
                                for (let idx = 0; idx < soundInfo.data.length; ++idx) {

                                    const object = soundInfo.data[idx];

                                    sounds.push({
                                        "characterId": Util.$characters.get(object.SoundId),
                                        "volume":      100,
                                        "loopCount":   object.SoundInfo.LoopCount | 0,
                                        "autoPlay":    !!object.SoundInfo.HasLoops
                                    });
                                }

                                movieClip._$sounds.set(soundInfo.frame, sounds);
                            }

                            Util.$characters.set(character._$characterId, id);
                        }
                        break;

                    case "lossless": // PNG
                        {

                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.BITMAP, `Bitmap_${id}`, id);

                            character.mode   = "lossless";
                            object.imageType = "image/png";
                            object.buffer    = null;
                            object.width     = character.width;
                            object.height    = character.height;

                            const bitmap = workSpace.addLibrary(object);
                            if (this._$folderId) {
                                bitmap.folderId = this._$folderId;
                            }

                            Util.$characters.set(character._$characterId, id);

                            if (Util.$unzipWorkerActive) {
                                Util.$unzipQueues.push(character);
                                return ;
                            }

                            Util.$unzipWorkerActive = true;

                            if (!Util.$unzipWorker) {
                                Util.$unzipWorker = new Worker(Util.$unzipURL);
                            }

                            const worker = Util.$unzipWorker;
                            worker.onmessage = Util.$unzipHandler.bind(character);
                            worker.postMessage(character, [character.buffer.buffer]);
                        }
                        break;

                    case "imageData": // JPEG,GIF,PNG,etc...
                        {
                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.BITMAP, `Bitmap_${id}`, id);

                            const imageType     = `image/${Util.$getImageType(character.jpegData)}`;
                            character.mode      = "jpegAlpha";
                            character.imageType = imageType;
                            object.imageType    = imageType;
                            object.buffer       = null;
                            object.width        = 0;
                            object.height       = 0;

                            const bitmap = workSpace.addLibrary(object);
                            if (this._$folderId) {
                                bitmap.folderId = this._$folderId;
                            }

                            Util.$characters.set(character._$characterId, id);

                            character.image = new Image();
                            character.image.decoding = "async";
                            character.image.src = URL.createObjectURL(
                                new Blob([character.jpegData], {
                                    "type": character.imageType
                                })
                            );

                            character.image.decode()
                                .then(Util.$jpegDecodeHandler.bind(character));

                        }
                        break;

                    case "StaticText":
                        {
                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.SHAPE, `ShapeText_${id}`, id);

                            object.bounds  = {
                                "xMin": character._$bounds.xMin,
                                "xMax": character._$bounds.xMax,
                                "yMin": character._$bounds.yMin,
                                "yMax": character._$bounds.yMax
                            };

                            const text = workSpace.addLibrary(object);
                            if (this._$folderId) {
                                text.folderId = this._$folderId;
                            }

                            Util.$characters.set(character._$characterId, id);

                            Util.$texts.set(Util.$texts.size, character);
                        }
                        break;

                    case "SimpleButton":
                        console.log("TODO SimpleButton: ", character);

                        // const object = Util
                        //     .$libraryController
                        //     .createInstance(InstanceType.BUTTON, `Button_${id}`, id);
                        //
                        // object.bounds  = {
                        //     "xMin": character._$bounds.xMin,
                        //     "xMax": character._$bounds.xMax,
                        //     "yMin": character._$bounds.yMin,
                        //     "yMax": character._$bounds.yMax
                        // };

                        // workSpace.addLibrary(object);

                        Util.$characters.set(character._$characterId, id);
                        break;

                    case "TextField":
                        {
                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.TEXT, `Text_${id}`, id);

                            object.bounds  = {
                                "xMin": character._$bounds.xMin,
                                "xMax": character._$bounds.xMax,
                                "yMin": character._$bounds.yMin,
                                "yMax": character._$bounds.yMax
                            };

                            // attach
                            object.text          = character._$text;
                            object.inputType     = character._$type;
                            object.color         = character._$textColor;
                            object.font          = character._$defaultTextFormat[1];
                            object.size          = character._$defaultTextFormat[2];
                            object.align         = character._$defaultTextFormat[7];
                            object.leftMargin    = character._$defaultTextFormat[8];
                            object.rightMargin   = character._$defaultTextFormat[9];
                            object.leading       = character._$defaultTextFormat[10];
                            object.multiline     = character._$multiline === 1;
                            object.wordWrap      = character._$wordWrap === 1;
                            object.border        = character._$border === 1;

                            if (character._$defaultTextFormat[4]
                            && character._$defaultTextFormat[5]
                            ) {
                                object.fontType = 3;
                            } else if (character._$defaultTextFormat[4]) {
                                object.fontType = 2;
                            } else if (character._$defaultTextFormat[5]) {
                                object.fontType = 1;
                            }

                            // Preserve HTML flag for roundtrip
                            object.html = !!character._$html;
                            object.htmlText = character._$htmlText;

                            const text = workSpace.addLibrary(object);
                            if (this._$folderId) {
                                text.folderId = this._$folderId;
                            }

                            Util.$characters.set(character._$characterId, id);
                        }
                        break;

                    case "Sound":
                        {
                            const object = Util
                                .$libraryController
                                .createInstance(InstanceType.SOUND, `Sound_${id}`, id);

                            object.buffer = character._$buffer;

                            const sound = workSpace.addLibrary(object);
                            if (this._$folderId) {
                                sound.folderId = this._$folderId;
                            }

                            Util.$characters.set(character._$characterId, id);
                        }
                        break;

                    default:
                        console.log("TODO: ", character);
                        break;

                }

                if (character._$characterId) {
                    return ;
                }

                if (this._$libraryId) {

                    Util.$changeLibraryId = this._$libraryId;

                    workSpace
                        .scene
                        .changeFrame(
                            Util.$timelineFrame.currentFrame
                        );

                    Util.$changeLibraryId = 0;
                }
            }
            break;

        case "_$symbols":
            for (let idx = 0; idx < event.data.pieces.length; ++idx) {
                const piece = event.data.pieces[idx];
                Util.$symbols.set(piece.tagId, piece.ns);
            }
            return;

        case "font":
            Util.$fonts.set(event.data.index, event.data.piece);
            return;

        case "font_shape":
            {
                const font = Util.$fonts.get(event.data.index);
                font._$glyphShapeTable.push.apply(font._$glyphShapeTable, event.data.pieces);
                Util.$fonts.set(event.data.index, font);
            }
            return;

        case "font_zone":
            {
                const font = Util.$fonts.get(event.data.index);
                font._$zoneTable.push.apply(font._$zoneTable, event.data.pieces);
                Util.$fonts.set(event.data.index, font);
            }
            return;

        default:
            break;

    }

    // if (Util.$texts.size) {
    //
    //     const { Graphics } = window.next2d.display;
    //
    //     const workSpace = Util.$currentWorkSpace();
    //
    //     for (const character of Util.$texts.values()) {
    //
    //         const shape = workSpace.getLibrary(character.libraryId);
    //
    //         // build shape data
    //         let offsetX     = 0;
    //         let offsetY     = 0;
    //         let color       = null;
    //         let codeTables  = null;
    //         let shapeTables = null;
    //         let textHeight  = 0;
    //         let isZoneTable = false;
    //
    //         const baseMatrix = character._$baseMatrix;
    //
    //         // build shape data
    //         const records = character._$textRecords;
    //         for (let idx = 0; idx < records.length; ++idx) {
    //
    //             const record = records[idx];
    //
    //             if ("FontId" in record) {
    //                 const font  = Util.$fonts.get(record.FontId);
    //                 codeTables  = font._$codeTable;
    //                 shapeTables = font._$glyphShapeTable;
    //                 isZoneTable = font._$zoneTable !== null;
    //             }
    //
    //             if ("XOffset" in record) {
    //                 offsetX = record.XOffset;
    //             }
    //
    //             if ("YOffset" in record) {
    //                 offsetY = record.YOffset;
    //             }
    //
    //             if ("TextColor" in record) {
    //                 color = record.TextColor;
    //             }
    //
    //             if ("TextHeight" in record) {
    //                 textHeight = record.TextHeight;
    //                 if (isZoneTable) {
    //                     textHeight /= 20;
    //                 }
    //             }
    //
    //             const entries = record.GlyphEntries;
    //             const count   = record.GlyphCount;
    //             const scale   = textHeight / 1024;
    //             for (let idx = 0; idx < count; ++idx) {
    //
    //                 const entry = entries[idx];
    //                 const index = entry.GlyphIndex | 0;
    //
    //                 // add records
    //                 const shapeRecodes = Util.$vtc.convert({
    //                     "ShapeData": shapeTables[index],
    //                     "lineStyles": [],
    //                     "fillStyles": [{
    //                         "Color": color,
    //                         "fillStyleType": 0
    //                     }]
    //                 });
    //
    //                 const matrix = [
    //                     scale, baseMatrix[1], baseMatrix[2], scale,
    //                     baseMatrix[4] + offsetX,
    //                     baseMatrix[5] + offsetY
    //                 ];
    //
    //                 for (let idx = 0; idx < shapeRecodes.length;) {
    //
    //                     const code = shapeRecodes[idx++];
    //                     shape._$recodes.push(code);
    //                     switch (code) {
    //
    //                         case Graphics.MOVE_TO:
    //                         case Graphics.LINE_TO:
    //                             {
    //                                 const x  = shapeRecodes[idx++];
    //                                 const y  = shapeRecodes[idx++];
    //                                 const tx = x * matrix[0] + y * matrix[2] + matrix[4];
    //                                 const ty = x * matrix[1] + y * matrix[3] + matrix[5];
    //                                 shape._$recodes.push(tx, ty);
    //                             }
    //                             break;
    //
    //                         case Graphics.CURVE_TO:
    //                             {
    //                                 const cx  = shapeRecodes[idx++];
    //                                 const cy  = shapeRecodes[idx++];
    //                                 const ctx = cx * matrix[0] + cy * matrix[2] + matrix[4];
    //                                 const cty = cx * matrix[1] + cy * matrix[3] + matrix[5];
    //                                 shape._$recodes.push(ctx, cty);
    //
    //                                 const x  = shapeRecodes[idx++];
    //                                 const y  = shapeRecodes[idx++];
    //                                 const tx = x * matrix[0] + y * matrix[2] + matrix[4];
    //                                 const ty = x * matrix[1] + y * matrix[3] + matrix[5];
    //                                 shape._$recodes.push(tx, ty);
    //                             }
    //                             break;
    //
    //                         case Graphics.FILL_STYLE:
    //                             shape._$recodes.push(
    //                                 shapeRecodes[idx++], shapeRecodes[idx++],
    //                                 shapeRecodes[idx++], shapeRecodes[idx++]
    //                             );
    //                             break;
    //
    //                         case Graphics.BEGIN_PATH:
    //                         case Graphics.END_FILL:
    //                             break;
    //
    //                     }
    //                 }
    //
    //                 offsetX += entry.GlyphAdvance;
    //             }
    //         }
    //     }
    // }

    const workSpace = Util.$currentWorkSpace();
    for (const [id, name] of Util.$symbols) {
        const instance = workSpace.getLibrary(id);
        instance._$symbol = `${name}`;
    }

    // map clear
    Util.$characters.clear();
    Util.$symbols.clear();
    Util.$fonts.clear();
    Util.$texts.clear();

    Util.$libraryController.reload(
        Array.from(workSpace._$libraries.values())
    );

    // parser end
    worker.onmessage = null;

    if (this._$resolve) {
        this._$resolve();
    }

    // next
    if (Util.$parserQueues.length) {

        const object = Util.$parserQueues.shift();

        worker.onmessage = Util.$parserHandler.bind(object);

        const buffer = object._$byteStream._$buffer;
        worker.postMessage({
            "version": object._$swfVersion,
            "offset":  object._$offset,
            "buffer":  buffer
        }, [buffer.buffer]);

    } else {

        Util.$parserWorkerWait = false;

    }

};

/**
 * @param  {object} bounds
 * @param  {Float32Array} matrix
 * @return {object}
 * @method
 * @static
 */
Util.$boundsMatrix = (bounds, matrix) =>
{
    const x0 = bounds.xMax * matrix[0] + bounds.yMax * matrix[2] + matrix[4];
    const x1 = bounds.xMax * matrix[0] + bounds.yMin * matrix[2] + matrix[4];
    const x2 = bounds.xMin * matrix[0] + bounds.yMax * matrix[2] + matrix[4];
    const x3 = bounds.xMin * matrix[0] + bounds.yMin * matrix[2] + matrix[4];
    const y0 = bounds.xMax * matrix[1] + bounds.yMax * matrix[3] + matrix[5];
    const y1 = bounds.xMax * matrix[1] + bounds.yMin * matrix[3] + matrix[5];
    const y2 = bounds.xMin * matrix[1] + bounds.yMax * matrix[3] + matrix[5];
    const y3 = bounds.xMin * matrix[1] + bounds.yMin * matrix[3] + matrix[5];

    return {
        "xMin": Math.min( Number.MAX_VALUE, x0, x1, x2, x3),
        "xMax": Math.max(-Number.MAX_VALUE, x0, x1, x2, x3),
        "yMin": Math.min( Number.MAX_VALUE, y0, y1, y2, y3),
        "yMax": Math.max(-Number.MAX_VALUE, y0, y1, y2, y3)
    };
};

/**
 * @param   {number} color
 * @returns {object}
 * @method
 * @static
 */
Util.$intToRGB = (color) =>
{
    return {
        "R": (color & 0xff0000) >> 16,
        "G": (color & 0x00ff00) >> 8,
        "B": color & 0x0000ff
    };
};

/**
 * @param  {object} object
 * @param  {Map}    dup
 * @method
 * @static
 */
Util.$copyContainer = (object, dup) =>
{
    const workSpace       = Util.$currentWorkSpace();
    const targetWorkSpace = Util.$workSpaces[Util.$copyWorkSpaceId];

    if (!dup.has(object.id)) {
        dup.set(object.id, workSpace.nextLibraryId);
    }

    object.id = dup.get(object.id);
    workSpace.addLibrary(object);

    for (let idx = 0; idx < object.layers.length; ++idx) {

        const layer = object.layers[idx];
        for (let idx = 0; idx < layer.characters.length; ++idx) {

            const character = layer.characters[idx];
            if (!dup.has(character.libraryId)) {

                dup.set(character.libraryId, workSpace.nextLibraryId);

                const instance = targetWorkSpace
                    .getLibrary(character.libraryId);

                const object = instance.toObject();
                if (object.type === InstanceType.MOVIE_CLIP) {

                    Util.$copyContainer(object, dup);

                } else {

                    object.id = dup.get(character.libraryId);
                    workSpace.addLibrary(object);

                }
            }

            character.libraryId = dup.get(character.libraryId);
        }
    }

    workSpace.addLibrary(object);
};

/**
 * @return {void}
 * @static
 */
Util.$clearShapePointer = () =>
{
    const element  = document.getElementById("stage-area");
    if (!element) {
        return ;
    }

    const children = element.children;
    for (let idx = 0; children.length > idx; ++idx) {

        const node = children[idx];
        if (!node.dataset.shapePointer) {
            continue;
        }

        node.remove();
        --idx;
    }
};

/**
 * @return {object}
 * @static
 */
Util.$getDefaultLoopConfig = () =>
{
    return {
        "type": LoopController.DEFAULT,
        "start": 1,
        "end": 0
    };
};

/**
 * @param  {object} place
 * @param  {object} range
 * @param  {number} parent_frame
 * @param  {number} total_frame
 * @param  {number} static_frame
 * @return {number}
 * @static
 */
Util.$getFrame = (place, range, parent_frame, total_frame, static_frame = 0) =>
{
    const length = parent_frame - range.startFrame;

    let frame = 1;
    switch (place.loop.type) {

        case LoopController.REPEAT:
            {
                const totalFrame = place.loop.end
                    ? place.loop.end
                    : total_frame;

                frame = place.loop.start;
                for (let idx = 0; idx < length; ++idx) {

                    ++frame;

                    if (frame > totalFrame) {
                        frame = place.loop.start;
                    }

                }
            }
            break;

        case LoopController.NO_REPEAT:
            {
                const totalFrame = place.loop.end
                    ? place.loop.end
                    : total_frame;

                frame = place.loop.start;
                for (let idx = 0; idx < length; ++idx) {

                    ++frame;

                    // ループは一回だけなので最後のフレームで終了
                    if (frame > totalFrame) {
                        frame = totalFrame;
                        break;
                    }

                }
            }
            break;

        case LoopController.FIXED_ONE:
            frame = place.loop.start;
            break;

        case LoopController.NO_REPEAT_REVERSAL:
            frame = place.loop.end
                ? place.loop.end
                : total_frame;

            for (let idx = 0; idx < length; ++idx) {

                --frame;

                // ループは一回だけなので最初のフレームにセットして終了
                if (place.loop.start > frame) {
                    frame = place.loop.start;
                    break;
                }
            }
            break;

        case LoopController.REPEAT_REVERSAL:
            {
                const totalFrame = place.loop.end
                    ? place.loop.end
                    : total_frame;

                frame = totalFrame;
                for (let idx = 0; idx < length; ++idx) {

                    --frame;

                    if (place.loop.start > frame) {
                        frame = totalFrame;
                    }
                }
            }
            break;

        case LoopController.DEFAULT:

            if (static_frame === 0) {
                frame = 1;
                for (let idx = 0; idx < length; ++idx) {

                    ++frame;

                    if (frame > total_frame) {
                        frame = 1;
                    }

                }
            } else {
                frame = static_frame;
            }

            if (frame > total_frame) {
                frame = 1;
            }
            break;

    }

    return frame;
};

/**
 * @param {File} file
 * @param {Instance} instance
 * @param {function} callback
 * @method
 * @static
 */
Util.$loadFils = (file, instance, callback) =>
{
    file
        .arrayBuffer()
        .then((buffer) =>
        {
            const image = new Image();
            image.src = URL.createObjectURL(new Blob([buffer], {
                "type": file.type
            }));

            image
                .decode()
                .then(() =>
                {
                    const width   = image.width;
                    const height  = image.height;

                    const canvas  = Util.$getCanvas();
                    canvas.width  = width;
                    canvas.height = height;
                    const context = canvas.getContext("2d", {
                        "willReadFrequently": true
                    });

                    context.drawImage(image, 0, 0, width, height);
                    instance._$buffer = new Uint8Array(
                        context.getImageData(0, 0, width, height).data
                    );
                    Util.$poolCanvas(canvas);

                    // 上書き
                    instance.width     = width;
                    instance.height    = height;
                    instance.imageType = file.type;

                    callback();

                    if (Util.$waitFiles.length) {
                        requestAnimationFrame(() =>
                        {
                            const object = Util.$waitFiles.shift();
                            Util.$loadFils(
                                object.file,
                                object.instance,
                                object.callback
                            );
                        });
                    } else {
                        Util.$loadingFile = false;
                    }
                });
        });
};