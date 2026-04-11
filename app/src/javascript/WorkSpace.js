/**
 * @class
 * @memberOf global
 */
class WorkSpace
{
    /**
     * @param {string} [json=""]
     *
     * @constructor
     * @public
     */
    constructor (json = "")
    {
        // Phase 2.1: Composition over inheritance - split God object
        this._$project      = new ProjectData();
        this._$timeline     = new TimelineState();
        this._$uiState      = new UIState();

        // Snapshot-based undo (legacy - use command mode if possible)
        this._$revision     = [];
        this._$currentData  = null;
        this._$position     = 0;

        // Command Pattern Undo/Redo (M6 refactoring)
        // Use this for efficient command-based undo instead of snapshot-based
        this._$undoManager  = new UndoManager(100);
        this._$commandMode  = false;  // Enable with enableCommandMode()

        if (json) {
            this.load(json);
        }
    }

    /**
     * @description Backward compatibility: Access repository as _$libraries
     * @return {LibraryRepository}
     * @deprecated Use _$project.repository instead
     * @public
     */
    get _$libraries ()
    {
        return this._$project.repository;
    }

    /**
     * @description Backward compatibility: Access ruler properties
     * @return {Array}
     * @deprecated Use _$uiState.rulerX instead
     * @public
     */
    get _$rulerX ()
    {
        return this._$uiState.rulerX;
    }

    /**
     * @description Backward compatibility: Set ruler X positions
     * @param {Array} value
     * @deprecated Use _$uiState.rulerX instead
     * @public
     */
    set _$rulerX (value)
    {
        this._$uiState.rulerX = value;
    }

    /**
     * @description Backward compatibility: Access ruler properties
     * @return {Array}
     * @deprecated Use _$uiState.rulerY instead
     * @public
     */
    get _$rulerY ()
    {
        return this._$uiState.rulerY;
    }

    /**
     * @description Backward compatibility: Set ruler Y positions
     * @param {Array} value
     * @deprecated Use _$uiState.rulerY instead
     * @public
     */
    set _$rulerY (value)
    {
        this._$uiState.rulerY = value;
    }

    /**
     * @description Backward compatibility: Access ruler visibility
     * @return {boolean}
     * @deprecated Use _$uiState.ruler instead
     * @public
     */
    get _$ruler ()
    {
        return this._$uiState.ruler;
    }

    /**
     * @description Backward compatibility: Set ruler visibility
     * @param {boolean} value
     * @deprecated Use _$uiState.ruler instead
     * @public
     */
    set _$ruler (value)
    {
        this._$uiState.ruler = value;
    }

    /**
     * @description Backward compatibility: Access controller width
     * @return {number}
     * @deprecated Use _$uiState.controllerWidth instead
     * @public
     */
    get _$controllerWidth ()
    {
        return this._$uiState.controllerWidth;
    }

    /**
     * @description Backward compatibility: Set controller width
     * @param {number} value
     * @deprecated Use _$uiState.controllerWidth instead
     * @public
     */
    set _$controllerWidth (value)
    {
        this._$uiState.controllerWidth = value;
    }

    /**
     * @description Backward compatibility: Access timeline height
     * @return {number}
     * @deprecated Use _$uiState.timelineHeight instead
     * @public
     */
    get _$timelineHeight ()
    {
        return this._$uiState.timelineHeight;
    }

    /**
     * @description Backward compatibility: Set timeline height
     * @param {number} value
     * @deprecated Use _$uiState.timelineHeight instead
     * @public
     */
    set _$timelineHeight (value)
    {
        this._$uiState.timelineHeight = value;
    }

    /**
     * @description Backward compatibility: Access name→id index
     * @return {Map}
     * @deprecated LibraryRepository manages its own name index now
     * @public
     */
    get _$nameMap ()
    {
        // Return a proxy Map that delegates to repository's name index
        // Since repository's nameIndex is private, we create a wrapper
        return {
            clear: () => {
                // Name index is part of repository state
                // Clearing it would require clearing the whole repository
                // For now, just log a warning
                console.warn('WorkSpace._$nameMap.clear() is deprecated. Use repository methods instead.');
            },
            get: (name) => this._$project.repository.findByName(name),
            has: (name) => this._$project.repository.findByName(name) !== undefined,
            set: (name, instance) => {
                // This is handled automatically by repository.add()
                console.warn('WorkSpace._$nameMap.set() is deprecated. Repository manages name index automatically.');
            },
            delete: (name) => {
                const library = this._$project.repository.findByName(name);
                if (library) {
                    this._$project.repository.delete(library.id);
                }
            }
        };
    }

    /**
     * @description Backward compatibility: Get current scene
     * @return {MovieClip}
     * @deprecated Direct access - consider using a proper scene manager
     * @public
     */
    get _$scene ()
    {
        return this._$timeline.scene;
    }

    /**
     * @description Backward compatibility: Set current scene
     * @param {MovieClip} scene
     * @deprecated Direct access - consider using a proper scene manager
     * @public
     */
    set _$scene (scene)
    {
        this._$timeline.scene = scene;
    }

    /**
     * @description Backward compatibility: Get character ID counter
     * @return {number}
     * @deprecated Use _$project.characterId instead
     * @public
     */
    get _$characterId ()
    {
        return this._$project._$characterId;
    }

    /**
     * @description Backward compatibility: Set character ID counter
     * @param {number} value
     * @deprecated Use _$project.characterId instead
     * @public
     */
    set _$characterId (value)
    {
        this._$project._$characterId = value;
    }

    /**
     * @description Backward compatibility: Get project name
     * @return {string}
     * @deprecated Use _$project.name instead
     * @public
     */
    get _$name ()
    {
        return this._$project.name;
    }

    /**
     * @description Backward compatibility: Set project name
     * @param {string} value
     * @deprecated Use _$project.name instead
     * @public
     */
    set _$name (value)
    {
        this._$project._$name = value;
    }

    /**
     * @description Backward compatibility: Get stage configuration
     * @return {Stage}
     * @deprecated Use _$project.stage instead
     * @public
     */
    get _$stage ()
    {
        return this._$project._$stage;
    }

    /**
     * @description Backward compatibility: Set stage configuration
     * @param {Stage} value
     * @deprecated Use _$project.stage instead
     * @public
     */
    set _$stage (value)
    {
        this._$project._$stage = value;
    }

    /**
     * @description Backward compatibility: Get plugins map
     * @return {Map}
     * @deprecated Use _$project.plugins instead
     * @public
     */
    get _$plugins ()
    {
        return this._$project._$plugins;
    }

    /**
     * @description Backward compatibility: Get current frame
     * @return {number}
     * @deprecated Use _$timeline.currentFrame instead
     * @public
     */
    get _$currentFrame ()
    {
        return this._$timeline.currentFrame;
    }

    /**
     * @description Backward compatibility: Set current frame
     * @param {number} value
     * @deprecated Use _$timeline.currentFrame instead
     * @public
     */
    set _$currentFrame (value)
    {
        this._$timeline.currentFrame = value;
    }

    /**
     * @description rootのMovieClipを戻す
     *
     * @return {MovieClip}
     * @readonly
     * @public
     */
    get root ()
    {
        return this._$project.root;
    }

    /**
     * @description プロジェクトのStageオブジェクトを返す
     *
     * @return {Stage}
     * @readonly
     * @public
     */
    get stage ()
    {
        return this._$project.stage;
    }

    /**
     * @description プロジェクト名を返す
     *
     * @return {string}
     * @public
     */
    get name ()
    {
        return this._$project.name;
    }

    /**
     * @description プロジェクト名をセット
     *
     * @param  {string} name
     * @return {void}
     * @public
     */
    set name (name)
    {
        this._$project.name = name;
    }

    /**
     * @description 現在表示中のシーン(MovieClip)を返す
     *
     * @return {MovieClip}
     * @public
     */
    get scene ()
    {
        return this._$timeline.scene;
    }

    /**
     * @description 指定のシーン(MovieClip)を起動する
     *
     * @param  {MovieClip} scene
     * @return {void}
     * @public
     */
    set scene (scene)
    {
        this._$timeline.scene = scene;
    }

    /**
     * @description 指定のシーン(MovieClip)を起動する
     *
     * @param  {MovieClip} scene
     * @return {Promise}
     * @public
     */
    setScene (scene)
    {
        this._$timeline.scene = scene;
        return scene.initialize();
    }

    /**
     * @description ライブラリのユニークIDを生成
     *
     * @return {number}
     * @readonly
     * @public
     */
    get nextLibraryId ()
    {
        return this._$project.nextLibraryId;
    }

    /**
     * @description 初期起動関数
     *
     * @param  {MovieClip} scene
     * @return {void}
     * @public
     */
    initialize (scene)
    {
        // シーンをセット
        this.scene = scene;

        // 選択中のライブラリを非アクティブに
        Util.$libraryController.clearActive();

        // ライブラリを初期化
        Util.$libraryController.reload(
            this._$project.repository.getAll()
        );

        // 内部スクリプトを初期化
        Util.$javascriptController.reload();

        // プラグインを初期化
        Util.$pluginController.reload(
            Array.from(this._$project.plugins.values())
        );

        // スクリーンの表示をrootに変更
        Util.$sceneChange.reload();
    }

    /**
     * @description 起動関数
     *
     * @return {void}
     * @method
     * @public
     */
    run ()
    {
        // Update CSS variables from UI state
        this._$uiState.updateCSSVariables();

        // ステージをセット
        this.stage.initialize();

        // 初期化
        this.initialize(this.root);
    }

    /**
     * @description プロジェクトを停止
     *
     * @return {void}
     * @method
     * @public
     */
    stop ()
    {
        this._$timeline.reset();

        // 定規を初期化
        Util.$screenRuler.clear();

        // プレビューを初期化
        Util.$libraryPreview.dispose();

        // player側も停止
        Util.$root.stage._$player.stop();
    }

    /**
     * @description 指定のプロジェクトJSONを読み込む (従来方式)
     *
     * @param  {string} json
     * @return {void}
     * @method
     * @public
     */
    load (json)
    {
        const object = JSON.parse(json);
        this.loadFromObject(object);
    }

    /**
     * @description プロジェクトオブジェクトから読み込む (ストリーミング対応)
     *
     * @param  {object} object
     * @return {void}
     * @method
     * @public
     */
    loadFromObject (object)
    {
        // Load project data
        this._$project.loadFromObject(object);

        // Load UI settings
        if (object.setting) {
            this._$uiState.loadFromObject(object.setting);
        }
    }

    /**
     * @description プロジェクトのJSONを生成
     *
     * @return {string}
     * @method
     * @public
     */
    toJSON (light)
    {
        const projectData = this._$project.toObject(light);
        const uiData = this._$uiState.toObject();

        return JSON.stringify({
            ...projectData,
            "setting": uiData
        });
    }

    /**
     * @description メモリに現在のプロジェクトデータを保存
     *
     * @return {void}
     * @method
     * @public
     */
    temporarilySaved ()
    {
        Util.$updated = true;

        if (this._$currentData) {
            this._$currentData = null;
        }

        if (this._$position !== this._$revision.length) {
            this._$revision.length = this._$position;
        }

        // Deferred snapshot: push a lazy thunk that only serializes
        // when undo is actually triggered.  The old requestIdleCallback
        // eager-resolution caused 29s main-thread freezes on large files
        // because toJSON(true) is O(N) over every library item / frame.
        const self = this;
        const idx  = this._$revision.length;
        let resolved = false;
        const thunk = {
            _resolve () {
                if (resolved) return;
                resolved = true;
                const json = self.toJSON(true);
                self._$revision[idx] = json;
                return json;
            },
            toString () { return this._resolve(); }
        };
        this._$revision.push(thunk);
        this._$position++;

        // remove old data
        if (this._$revision.length > Util.REVISION_LIMIT) {

            this._$revision.shift();

            this._$position = this._$revision.length;
        }
    }

    /**
     * @description 保存した一個前のプロジェクトデータを読み込む
     *
     * @return {void}
     * @method
     * @public
     */
    undo ()
    {
        if (!this._$position) {
            return ;
        }

        if (!this._$currentData) {
            this._$currentData = this.toJSON(true);
        }

        const currentFrame = Util.$timelineFrame.currentFrame;
        // Force-resolve lazy thunks before using them
        let data = this._$revision[--this._$position];
        if (data && typeof data === 'object' && data._resolve) {
            data = data._resolve();
        }
        this.reloadData(data);
        Util.$timelineFrame.currentFrame = 0;
    }

    /**
     * @description 保存した一個先のプロジェクトデータを読み込む
     *
     * @return {void}
     * @method
     * @public
     */
    redo ()
    {
        if (!this._$revision.length
            || this._$position === this._$revision.length
        ) {
            return ;
        }

        let data = null;
        if (this._$position + 1 === this._$revision.length) {

            if (!this._$currentData) {
                return ;
            }

            data = this._$currentData;

            this._$position++;
            this._$currentData = null;

        } else {

            data = this._$revision[++this._$position];

        }

        // Force-resolve lazy thunks
        if (data && typeof data === 'object' && data._resolve) {
            data = data._resolve();
        }

        if (!data) {
            return ;
        }

        const currentFrame = Util.$timelineFrame.currentFrame;
        this.reloadData(data);
        Util.$timelineFrame.currentFrame = 0;
    }

    /**
     * @description undo/redoのデータの再読み込み
     *
     * @param  {string} data
     * @return {void}
     * @method
     * @public
     */
    reloadData (data)
    {
        // 選択中のレイヤーを保持
        const layerIds = [];
        const targetLayers = Util.$timelineLayer.targetLayers;
        for (const layerId of targetLayers.keys()) {
            layerIds.push(layerId);
        }

        // シーンの階層データを保持
        Util.$sceneChange.cache();

        /**
         * @type {ArrowTool}
         */
        const tool = Util.$tools.getDefaultTool("arrow");
        tool.clear();
        Util.$tools.reset();

        // 値をキャッシュ
        const currentFrame   = this._$scene.currentFrame;
        const currentSceneId = this._$scene.id;

        // シーンを初期化
        this._$timeline.reset();

        // 再読み込み
        this.load(data);

        // loadしたデータでレイヤーを再構築
        let scene = this.getLibrary(currentSceneId);

        // 指定したシーンがなければrootをセット
        if (!scene) {
            scene = this.getLibrary(0);
            layerIds.length = 0;
        } else {
            scene._$currentFrame = currentFrame;
        }

        Util.$sceneChange.restore();
        this.initialize(scene);

        // 再読み込み
        if (layerIds.length) {

            const ctrlKey = Util.$ctrlKey;
            Util.$ctrlKey = true;
            for (let idx = 0; idx < layerIds.length; ++idx) {

                const element = document
                    .getElementById(`${layerIds[idx]}`);

                if (!element) {
                    continue;
                }

                Util.$timelineLayer.activeLayer(element);
            }

            Util.$ctrlKey = ctrlKey;
        }
    }

    /**
     * @description ライブラリに追加されたObjectをプロジェクト内部に格納
     *
     * @param  {object} library
     * @return {object}
     * @method
     * @public
     */
    addLibrary (library)
    {
        return this._$project.addLibrary(library);
    }

    /**
     * @description 指定のライブラリのアイテムを返す
     *
     * @param  {uint} id
     * @return {object}
     * @method
     * @public
     */
    getLibrary (id)
    {
        return this._$project.repository.get(id | 0);
    }

    /**
     * @description 指定のライブラリのアイテムを削除
     *
     * @param  {uint} id
     * @return {void}
     * @method
     * @public
     */
    removeLibrary (id)
    {
        this._$project.repository.delete(id | 0);
    }

    // ══════════════════════════════════════════════════════════════════
    //                  COMMAND PATTERN UNDO/REDO (M6)
    // ══════════════════════════════════════════════════════════════════

    /**
     * @description Enable command-based undo/redo (replaces snapshot-based).
     *
     * When enabled, mutations should use executeCommand() instead of
     * addRevision() for efficient memory usage.
     *
     * @return {void}
     * @method
     * @public
     */
    enableCommandMode ()
    {
        this._$commandMode = true;
        console.log("WorkSpace: Command-based undo/redo enabled");
    }

    /**
     * @description Disable command mode (revert to snapshot-based undo).
     *
     * @return {void}
     * @method
     * @public
     */
    disableCommandMode ()
    {
        this._$commandMode = false;
    }

    /**
     * @description Check if command mode is enabled.
     *
     * @return {boolean}
     * @method
     * @public
     */
    isCommandModeEnabled ()
    {
        return this._$commandMode;
    }

    /**
     * @description Execute a command through the undo manager.
     *
     * Use this for all mutations when command mode is enabled.
     *
     * Example:
     *   workspace.executeCommand(new UpdatePlaceCommand(obj, {x: 100, y: 50}));
     *
     * @param  {Command} command - Command to execute
     * @return {void}
     * @method
     * @public
     */
    executeCommand (command)
    {
        this._$undoManager.execute(command);
    }

    /**
     * @description Undo last command (command mode only).
     *
     * @return {boolean} - True if undo succeeded
     * @method
     * @public
     */
    undoCommand ()
    {
        return this._$undoManager.undo();
    }

    /**
     * @description Redo next command (command mode only).
     *
     * @return {boolean} - True if redo succeeded
     * @method
     * @public
     */
    redoCommand ()
    {
        return this._$undoManager.redo();
    }

    /**
     * @description Check if undo is available (command mode).
     *
     * @return {boolean}
     * @method
     * @public
     */
    canUndoCommand ()
    {
        return this._$undoManager.canUndo();
    }

    /**
     * @description Check if redo is available (command mode).
     *
     * @return {boolean}
     * @method
     * @public
     */
    canRedoCommand ()
    {
        return this._$undoManager.canRedo();
    }

    /**
     * @description Get the undo manager instance.
     *
     * @return {UndoManager}
     * @method
     * @public
     */
    getUndoManager ()
    {
        return this._$undoManager;
    }

    /**
     * @description Begin a transaction (batch multiple commands).
     *
     * Example:
     *   workspace.beginTransaction("Paste");
     *   workspace.executeCommand(new AddLibraryCommand(...));
     *   workspace.executeCommand(new AddLayerCommand(...));
     *   workspace.commitTransaction();
     *
     * @param  {string} [description] - Transaction description
     * @return {void}
     * @method
     * @public
     */
    beginTransaction (description)
    {
        this._$undoManager.beginTransaction(description);
    }

    /**
     * @description Commit the current transaction.
     *
     * @return {void}
     * @method
     * @public
     */
    commitTransaction ()
    {
        this._$undoManager.commitTransaction();
    }

    /**
     * @description Cancel the current transaction.
     *
     * @return {void}
     * @method
     * @public
     */
    cancelTransaction ()
    {
        this._$undoManager.cancelTransaction();
    }
}

