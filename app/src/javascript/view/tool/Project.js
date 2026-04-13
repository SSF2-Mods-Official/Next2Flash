/**
 * @class
 * @memberOf view.tool
 */
class Project
{
    /**
     * @description 初期起動関数
     *
     * @return {void}
     * @method
     * @public
     */
    initialize ()
    {
        // 新規プロジェクト
        const newElement = document
            .getElementById("tools-new-project");

        if (newElement) {
            newElement
                .addEventListener("click", (event) =>
                {
                    event.preventDefault();
                    this.newProject();
                });
        }

        // ファイル読み込み
        const loadElement = document
            .getElementById("tools-load");

        if (loadElement) {
            loadElement
                .addEventListener("click", (event) =>
                {
                    event.preventDefault();
                    this.open();
                });
        }

        const fileInput = document
            .getElementById("tools-load-file-input");

        if (fileInput) {
            fileInput
                .addEventListener("change", (event) =>
                {
                    const files = event.target.files;
                    for (let idx = 0; idx < files.length; ++idx) {
                        this.load(files[idx]);
                    }

                    // reset
                    event.target.value = "";
                });
        }

        const saveElement = document
            .getElementById("tools-save");

        if (saveElement) {
            saveElement
                .addEventListener("click", (event) =>
                {
                    event.preventDefault();
                    this.save();
                });
        }

        const exportElement = document
            .getElementById("tools-export");

        if (exportElement) {
            exportElement
                .addEventListener("click", (event) =>
                {
                    event.preventDefault();
                    this.publish();
                });
        }

        const languageElement = document
            .getElementById("language-setting");

        if (languageElement) {

            const language = localStorage
                .getItem(`${Util.PREFIX}@language-setting`);

            if (language) {
                const children = languageElement.children;
                for (let idx = 0; idx < children.length; ++idx) {
                    const node = children[idx];
                    if (node.value === language) {
                        node.selected = true;
                        break;
                    }
                }
            }

            languageElement
                .addEventListener("change", (event) =>
                {
                    const language = event.target.value;

                    const LanguageClass = Util.$languages.get(language);
                    Util.$currentLanguage = new LanguageClass();

                    localStorage
                        .setItem(`${Util.PREFIX}@language-setting`, language);

                    Util.$addModalEvent(document);
                });
        }
    }

    /**
     * @description サーバー経由で新規プロジェクトを作成
     *
     * @return {void}
     * @method
     * @public
     */
    newProject ()
    {
        if (Util.$saveProgress.active) {
            return ;
        }

        // Get current stage defaults from the active workspace (if any)
        const current = Util.$currentWorkSpace();
        const stage   = current ? current.stage : null;

        const params = {
            "name":            "untitled",
            "width":           stage ? stage.width  : 550,
            "height":          stage ? stage.height : 400,
            "frameRate":       stage ? stage.fps    : 24,
            "backgroundColor": stage ? stage.bgColor : 0xFFFFFF,
            "saveFolder":      true
        };

        // Try the server endpoint first (creates project folder for export).
        // Fall back to local-only blank workspace if server is unavailable.
        fetch("/api/new-project", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(params)
        })
            .then(async (response) =>
            {
                if (!response.ok) {
                    throw new Error(`Server returned ${response.status}`);
                }

                const buffer = await response.arrayBuffer();
                const uint8  = new Uint8Array(buffer);
                const name   = response.headers.get("X-N2D-Name") || params.name;

                // Same loading path as load() for ZIP-msgpack
                if (uint8.length >= 4 && uint8[0] === 0x50 && uint8[1] === 0x4B) {
                    const zip     = await JSZip.loadAsync(buffer);
                    let jsonData;

                    if (zip.file("project.msgpack")) {
                        const msgpackData = await zip.file("project.msgpack").async("uint8array");
                        jsonData = window.MessagePack.decode(msgpackData);
                    } else if (zip.file("project.json")) {
                        jsonData = JSON.parse(await zip.file("project.json").async("string"));
                    } else {
                        throw new Error("Invalid N2D response");
                    }

                    const workSpace = new WorkSpace();
                    workSpace.name = name;
                    workSpace.loadFromObject(jsonData);

                    Util.$workSpaces.push(workSpace);
                    Util.$screenTab.createElement(workSpace, Util.$workSpaces.length - 1);
                    Util.$screenTab.activeTab({
                        "currentTarget": {
                            "dataset": {
                                "tabId": Util.$workSpaces.length - 1
                            }
                        }
                    });
                } else {
                    throw new Error("Unexpected response format");
                }
            })
            .catch(() =>
            {
                // Fallback: create a local-only blank workspace (no project folder)
                const workSpace = new WorkSpace();
                workSpace.name = params.name;

                Util.$workSpaces.push(workSpace);
                Util.$screenTab.createElement(workSpace, Util.$workSpaces.length - 1);
                Util.$screenTab.activeTab({
                    "currentTarget": {
                        "dataset": {
                            "tabId": Util.$workSpaces.length - 1
                        }
                    }
                });
            });
    }

    /**
     * @description 指定したフォーマットで書き出し
     *
     * @return {void}
     * @method
     * @public
     */
    publish ()
    {
        if (Util.$saveProgress.active) {
            return ;
        }

        Util.$saveProgress.start();

        // ダウンロードリンクを生成
        const anchor = document.getElementById("save-anchor");

        if (anchor.href) {
            URL.revokeObjectURL(anchor.href);
        }

        const type = document
            .getElementById("publish-type-setting")
            .value;

        switch (type) {

            case "json":
                Util.$saveProgress.createJson();
                setTimeout(() =>
                {
                    anchor.download = `${Util.$currentWorkSpace().name}.json`;
                    anchor.href     = URL.createObjectURL(new Blob(
                        [Publish.toJSON()],
                        { "type" : "application/json" }
                    ));
                    anchor.click();

                    Util.$saveProgress.end();
                }, 200);
                break;

            case "zlib":
                Publish.toZlib();
                break;

            case "webm":
                Publish.toWebM();
                break;

            case "gif-loop":
                Publish.toGIF();
                break;

            case "gif":
                Publish.toGIF(-1);
                break;

            case "png":
                Publish.toPng();
                break;

            case "apng-loop":
                Publish.toApng(true);
                break;

            case "apng":
                Publish.toApng(false);
                break;

            case "custom":
                {
                    const object = window.nt || window.fl;
                    if ("customPublish" in object) {
                        window.FLfile.clear();
                        object
                            .customPublish(Publish.toObject());
                    }
                    Util.$saveProgress.end();
                }
                break;

        }
    }

    /**
     * @description n2dファイルの読み込み処理、zipデータ解凍
     *
     * @param  {File} file
     * @return {void}
     * @public
     */
    load (file)
    {
        if (Util.$saveProgress.active) {
            return ;
        }

        Util.$saveProgress.start();

        file
            .arrayBuffer()
            .then(async (buffer) =>
            {
                const uint8Array = new Uint8Array(buffer);
                
                // Check if it's a ZIP file (new format with MessagePack)
                // ZIP files start with PK signature (0x50 0x4B)
                if (uint8Array.length >= 4 && 
                    uint8Array[0] === 0x50 && uint8Array[1] === 0x4B) {
                    
                    console.log('[N2F] Detected ZIP format, extracting MessagePack/JSON...');
                    
                    try {
                        // Load ZIP
                        const zip = await JSZip.loadAsync(buffer);
                        
                        let jsonData;
                        
                        // Check for MessagePack format first (preferred)
                        if (zip.file('project.msgpack')){
                            console.log('[N2F] Loading MessagePack format (binary)');
                            const msgpackData = await zip.file('project.msgpack').async('uint8array');
                            
                            if (!window.MessagePack || !window.MessagePack.decode) {
                                throw new Error('MessagePack library not loaded');
                            }
                            
                            jsonData = window.MessagePack.decode(msgpackData);
                            console.log('[N2F] MessagePack decoded successfully');
                            
                        } else if (zip.file('project.json')) {
                            console.log('[N2F] Loading JSON format (legacy)');
                            const jsonText = await zip.file('project.json').async('string');
                            jsonData = JSON.parse(jsonText);
                            
                        } else {
                            throw new Error('N2D file contains neither project.msgpack nor project.json');
                        }
                        
                        // Load object directly into WorkSpace (bypasses string conversion limit!)
                        console.log('[N2F] Loading object directly into WorkSpace');
                        console.time('[N2F] WorkSpace creation from object');
                        
                        Util.$saveProgress.loadN2D();
                        
                        const sizeInMB = buffer.byteLength / (1024 * 1024);
                        const librariesCount = jsonData.libraries ? jsonData.libraries.length : 0;
                        console.log(`[N2F] Data size: ${sizeInMB.toFixed(2)} MB, ${librariesCount} libraries`);
                        
                        // Use progressive loading for large files (>300MB or >1000 libraries)
                        if (sizeInMB > 300 || librariesCount > 1000) {
                            console.log('[N2F] Using progressive loading...');
                            Util.$loadWorkSpaceProgressivelyFromObject(jsonData, file.name.replace(".n2d", ""));
                        } else {
                            const workSpace = new WorkSpace();
                            workSpace.name = file.name.replace(".n2d", "");
                            workSpace.loadFromObject(jsonData);
                            console.timeEnd('[N2F] WorkSpace creation from object');
                            
                            Util.$workSpaces.push(workSpace);
                            
                            Util.$screenTab.createElement(workSpace, Util.$workSpaces.length - 1);
                            
                            Util.$screenTab.activeTab({
                                "currentTarget": {
                                    "dataset": {
                                        "tabId": Util.$workSpaces.length - 1
                                    }
                                }
                            });
                            
                            Util.$saveProgress.end();
                        }
                        
                    } catch (error) {
                        console.error('[N2F] Failed to load ZIP/MessagePack format:', error);
                        Util.$saveProgress.end();
                        alert('Failed to load N2D file: ' + error.message);
                    }
                    
                } else {
                    // Old format: zlib-compressed URL-encoded JSON
                    console.log('[N2F] Detected zlib format (legacy)');
                    Util.$saveProgress.zlibInflate();
                    
                    Util.$unZlibWorker.postMessage({
                        "buffer": uint8Array,
                        "name"  : file.name.replace(".n2d", ""),
                        "type"  : "n2d"
                    }, [uint8Array.buffer]);
                }
            });
    }

    /**
     * @description プロジェクトデータをローカルから選択する
     *
     * @return {void}
     * @method
     * @public
     */
    open ()
    {
        document
            .getElementById("tools-load-file-input")
            .click();
    }

    /**
     * @description プロジェクトデータをローカルへ保存
     *
     * @return {void}
     * @method
     * @public
     */
    save ()
    {
        if (Util.$saveProgress.active) {
            return ;
        }

        Util.$saveProgress.start();

        new Promise((resolve) =>
        {
            Util.$saveProgress.createJson();
            setTimeout(() =>
            {
                resolve({
                    "object": Util.$currentWorkSpace().toJSON(),
                    "type": "n2d"
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
    }
}

Util.$project = new Project();
