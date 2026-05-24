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
        this._$wsDbgId      = (WorkSpace._$wsDbgCounter = (WorkSpace._$wsDbgCounter || 0) + 1);
        console.log(`[UNDO-DBG] new WorkSpace instance id=${this._$wsDbgId}`);

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
        // Suppress snapshots while reloadData() is restoring state — otherwise
        // tool side-effects (e.g. TransformTool.resetPointer) push the just-
        // restored state back onto the stack, clobbering redo and turning
        // every subsequent undo into a no-op.
        if (this._$reloadInProgress) {
            console.log(`[UNDO-DBG] temporarilySaved SUPPRESSED (reload in progress)`);
            return;
        }

        Util.$updated = true;

        if (this._$currentData) {
            this._$currentData = null;
        }

        if (this._$position !== this._$revision.length) {
            console.log(`[UNDO-DBG] temporarilySaved TRUNCATE revision from ${this._$revision.length} to ${this._$position}`);
            this._$revision.length = this._$position;
        }

        const stack = (new Error()).stack.split('\n').slice(2, 5).map(s => s.trim()).join(' | ');
        const json = this.toJSON(true);

        // De-duplicate: if the top snapshot is identical to the new one, skip.
        // (Happens when both a pre-edit and a post-edit save fire for the
        // same logical action without any actual state change in between.)
        if (this._$revision.length && this._$revision[this._$revision.length - 1] === json) {
            console.log(`[UNDO-DBG] temporarilySaved DEDUPE (same as top) caller=${stack}`);
            return;
        }

        this._$revision.push(json);
        this._$position++;
        console.log(`[UNDO-DBG] temporarilySaved PUSH wsId=${this._$wsDbgId} pos=${this._$position} revLen=${this._$revision.length} jsonLen=${json.length} caller=${stack}`);

        // remove old data
        if (this._$revision.length > Util.REVISION_LIMIT) {
            this._$revision.shift();
            this._$position = this._$revision.length;
            console.log(`[UNDO-DBG] temporarilySaved LIMIT_HIT pos=${this._$position}`);
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
        console.log(`[UNDO-DBG] undo() ENTER wsId=${this._$wsDbgId} pos=${this._$position} revLen=${this._$revision.length} hasCurrentData=${!!this._$currentData}`);
        if (!this._$position) {
            console.log(`[UNDO-DBG] undo() ABORT pos=0`);
            return ;
        }

        const currentJson = this.toJSON(true);
        if (!this._$currentData) {
            this._$currentData = currentJson;
            console.log(`[UNDO-DBG] undo() captured currentData len=${this._$currentData.length}`);
        }

        // Skip snapshots that match the current state — these are post-edit
        // "save" calls (e.g. TransformTool.resetPointer fires AFTER a draw
        // completes, snapshotting the already-mutated state). Without this,
        // the first undo restores the SAME state and appears to do nothing.
        let data = null;
        while (this._$position > 0) {
            const candidate = this._$revision[--this._$position];
            if (candidate !== currentJson) {
                data = candidate;
                break;
            }
            console.log(`[UNDO-DBG] undo() SKIP same-as-current at pos=${this._$position}`);
        }

        if (!data) {
            console.log(`[UNDO-DBG] undo() ABORT - no distinct prior state found`);
            return ;
        }

        console.log(`[UNDO-DBG] undo() RESTORING pos=${this._$position} dataLen=${data.length}`);
        this.reloadData(data);
        Util.$timelineFrame.currentFrame = 0;
        console.log(`[UNDO-DBG] undo() DONE pos=${this._$position}`);
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
        console.log(`[UNDO-DBG] redo() ENTER wsId=${this._$wsDbgId} pos=${this._$position} revLen=${this._$revision.length} hasCurrentData=${!!this._$currentData}`);
        if (!this._$revision.length
            || this._$position === this._$revision.length
        ) {
            console.log(`[UNDO-DBG] redo() ABORT - at top of stack`);
            return ;
        }

        const currentJson = this.toJSON(true);
        let data = null;

        // Skip snapshots that match current state (mirror of undo() logic)
        while (this._$position < this._$revision.length) {
            const candidate = this._$revision[this._$position++];
            if (candidate !== currentJson) {
                data = candidate;
                break;
            }
            console.log(`[UNDO-DBG] redo() SKIP same-as-current at pos=${this._$position - 1}`);
        }

        // Fall through to stashed currentData if at top
        if (!data && this._$currentData && this._$currentData !== currentJson) {
            data = this._$currentData;
            this._$currentData = null;
            console.log(`[UNDO-DBG] redo() using stashed currentData`);
        }

        if (!data) {
            console.log(`[UNDO-DBG] redo() ABORT - no distinct forward state`);
            return ;
        }

        console.log(`[UNDO-DBG] redo() RESTORING pos=${this._$position} dataLen=${data.length}`);
        this.reloadData(data);
        Util.$timelineFrame.currentFrame = 0;
        console.log(`[UNDO-DBG] redo() DONE pos=${this._$position}`);
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
        console.log(`[UNDO-DBG] reloadData() ENTER dataType=${typeof data} dataLen=${typeof data === 'string' ? data.length : 'N/A'} sceneId=${this._$scene && this._$scene.id} curFrame=${Util.$timelineFrame && Util.$timelineFrame.currentFrame}`);
        this._$reloadInProgress = true;
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

        // Force screen redraw after undo/redo. Manual changeFrame+pointer
        // reset wasn't reliably triggering a visual repaint. The user has
        // confirmed that zooming in/out fixes the display, so invoke the
        // exact same code path: ScreenZoom.execute(0) (delta=0 keeps zoom
        // level identical but runs the full dispose → changeFrame → DOM
        // pointer reset → ruler rebuild pipeline).
        try {
            const self = this;
            if (Util.$screenZoom && typeof Util.$screenZoom.execute === "function") {
                console.log(`[UNDO-DBG] reloadData() invoking ScreenZoom.execute(0)`);
                Util.$screenZoom.execute(0);
                // ScreenZoom.execute fires changeFrame asynchronously without
                // returning the promise. Clear the reload guard on the next
                // microtask tick — by then the dispose loop has already run
                // and only the async DOM reset remains, which doesn't call
                // temporarilySaved.
                Promise.resolve().then(() => {
                    self._$reloadInProgress = false;
                    console.log(`[UNDO-DBG] reloadData() ASYNC DONE`);
                });
            } else {
                // Fallback: direct changeFrame
                const frame = Util.$timelineFrame
                    ? Util.$timelineFrame.currentFrame
                    : this._$scene.currentFrame;
                for (const layer of this._$scene._$layers.values()) {
                    for (let i = 0; i < layer._$characters.length; ++i) {
                        layer._$characters[i].dispose();
                    }
                }
                this._$scene.changeFrame(frame).then(() => {
                    self._$reloadInProgress = false;
                }).catch(() => {
                    self._$reloadInProgress = false;
                });
            }
        } catch (e) {
            this._$reloadInProgress = false;
            console.warn("[UNDO-DBG] reloadData: redraw failed", e);
        }
        console.log(`[UNDO-DBG] reloadData() EXIT (async pending)`);
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

