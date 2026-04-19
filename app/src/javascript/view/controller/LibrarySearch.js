/**
 * @class
 * @memberOf view.controller
 */
class LibrarySearch
{
    /**
     * @constructor
     * @public
     */
    constructor ()
    {
        /**
         * @type {function}
         * @default null
         * @private
         */
        this._$handler = null;

        /**
         * @type {Map<number, string>}
         * @private
         */
        this._$folderModes = new Map();

        /**
         * @type {boolean}
         * @private
         */
        this._$searchActive = false;

        // DOMの読込がまだであれば、イベントに登録
        Util.$readEnd++;
        if (document.readyState !== "complete") {
            this._$handler = this.initialize.bind(this);
            window.addEventListener("DOMContentLoaded", this._$handler);
        } else {
            this.initialize();
        }
    }

    /**
     * @description 初期起動関数
     *
     * @return {void}
     * @method
     * @public
     */
    initialize ()
    {
        // イベントの登録を解除して、変数を解放
        if (this._$handler) {
            window.removeEventListener("DOMContentLoaded", this._$handler);
            this._$handler = null;
        }

        const element = document
            .getElementById("library-search");

        if (element) {

            element.addEventListener("focusin", () =>
            {
                Util.$keyLock = true;
            });
            element.addEventListener("focusout", () =>
            {
                Util.$keyLock = false;
            });
            element.addEventListener("input", (event) =>
            {
                this.execute(event);
            });

        }

        // 終了コール
        Util.$initializeEnd();
    }

    /**
     * @description デバッグ情報をサーバーログへ送信
     *
     * @param  {string} message
     * @param  {object} payload
     * @return {void}
     * @method
     * @public
     */
    sendDebugLog (message, payload = {})
    {
        try {

            fetch("/api/log", {
                "method": "POST",
                "headers": {
                    "Content-Type": "application/json"
                },
                "keepalive": true,
                "body": JSON.stringify({
                    "level": "INFO",
                    "module": "LibrarySearch",
                    "message": `${message} ${JSON.stringify(payload)}`
                })
            }).catch(() => {});

        } catch (e) {
            // no-op
        }
    }

    /**
     * @description inputの値をライブラリ内で検索
     *
     * @param  {Event} event
     * @return {void}
     * @method
     * @public
     */
    execute (event)
    {
        const value = (event.target.value || "")
            .toLowerCase();

        const workSpace = Util.$currentWorkSpace();
        if (!workSpace || !workSpace._$libraries) {
            return ;
        }

        const libraries = Array.from(workSpace._$libraries.values())
            .filter((instance) => instance && instance.id);

        if (!value) {

            this.restoreFolderModes();

            Util
                .$libraryController
                .reload(libraries);

            return ;
        }

        this.saveFolderModes(libraries);

        const byId = new Map();
        for (let idx = 0; idx < libraries.length; ++idx) {
            byId.set(libraries[idx].id, libraries[idx]);
        }

        const result = new Map();
        for (let idx = 0; idx < libraries.length; ++idx) {

            const instance = libraries[idx];

            const nameText = `${instance.name || ""}`.toLowerCase();
            const symbolText = `${instance.symbol || ""}`.toLowerCase();

            if (nameText.indexOf(value) === -1
                && symbolText.indexOf(value) === -1
            ) {
                continue;
            }

            result.set(instance.id, instance);

            let parentId = instance.folderId | 0;
            while (parentId) {

                const parent = byId.get(parentId);
                if (!parent) {
                    break;
                }

                parent.mode = FolderType.OPEN;
                result.set(parent.id, parent);

                parentId = parent.folderId | 0;
            }
        }

        if (value.indexOf("blackmage_d") > -1) {

            const totalBlackmageRows = libraries
                .filter((instance) => {
                    return instance
                        && instance.name
                        && instance.name.toLowerCase().indexOf("blackmage_d") > -1;
                })
                .map((instance) => {
                    return {
                        "id": instance.id,
                        "name": instance.name,
                        "symbol": instance.symbol,
                        "folderId": instance.folderId | 0
                    };
                });

            const matchedRows = Array.from(result.values())
                .filter((instance) => {
                    return instance
                        && instance.name
                        && instance.name.toLowerCase().indexOf("blackmage_d") > -1;
                })
                .map((instance) => {
                    return {
                        "id": instance.id,
                        "name": instance.name,
                        "symbol": instance.symbol,
                        "folderId": instance.folderId | 0
                    };
                });

            console.groupCollapsed(
                `[N2F][LibrarySearchDebug] query=${value} total=${totalBlackmageRows.length} matched=${matchedRows.length}`
            );
            console.log("totalBlackmageRows", totalBlackmageRows);
            console.log("matchedRows", matchedRows);
            console.log(
                "id217",
                {
                    "inTotal": totalBlackmageRows.some((entry) => entry.id === 217),
                    "inMatched": matchedRows.some((entry) => entry.id === 217)
                }
            );
            console.groupEnd();

            const debugPayload = {
                "query": value,
                "total": totalBlackmageRows.length,
                "matched": matchedRows.length,
                "id217": {
                    "inTotal": totalBlackmageRows.some((entry) => entry.id === 217),
                    "inMatched": matchedRows.some((entry) => entry.id === 217)
                },
                "totalRows": totalBlackmageRows,
                "matchedRows": matchedRows
            };

            window.__n2fLibraryDebug = window.__n2fLibraryDebug || {};
            window.__n2fLibraryDebug.search = debugPayload;

            this.sendDebugLog("[N2F][LibrarySearchDebug]", debugPayload);
        }

        Util
            .$libraryController
            .reload(Array.from(result.values()));
    }

    /**
     * @description DOM上のライブラリ一覧が不足している時は再構築する
     *
     * @return {void}
     * @method
     * @public
     */
    saveFolderModes (libraries)
    {
        if (this._$searchActive) {
            return ;
        }

        this._$folderModes.clear();
        for (let idx = 0; idx < libraries.length; ++idx) {

            const instance = libraries[idx];
            if (instance.type !== InstanceType.FOLDER) {
                continue;
            }

            this._$folderModes.set(instance.id, instance.mode);
        }

        this._$searchActive = true;
    }

    /**
     * @description 検索中に変更したフォルダー開閉状態を復元する
     *
     * @return {void}
     * @method
     * @public
     */
    restoreFolderModes ()
    {
        if (!this._$searchActive) {
            return ;
        }

        const workSpace = Util.$currentWorkSpace();
        if (!workSpace || !workSpace._$libraries) {
            this._$folderModes.clear();
            this._$searchActive = false;
            return ;
        }

        for (const [folderId, mode] of this._$folderModes) {

            const folder = workSpace.getLibrary(folderId);
            if (!folder || folder.type !== InstanceType.FOLDER) {
                continue;
            }

            folder.mode = mode;
        }

        this._$folderModes.clear();
        this._$searchActive = false;
    }
}

Util.$librarySearch = new LibrarySearch();
