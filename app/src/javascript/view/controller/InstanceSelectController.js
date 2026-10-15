/**
 * @class
 * @memberOf view.controller
 */
class InstanceSelectController extends BaseController
{
    /**
     * @description ライブラリの選択インスタンスのプルダウン制御
     *
     * @return {void}
     * @method
     * @public
     */
    initialize ()
    {
        super.initialize();

        // インスタンス設定は初期は非表示
        const element = document.getElementById("instance-setting");
        if (element) {
            element.style.display = "none";
        }
    }

    /**
     * @description ライブラリの選択可能なインスタンスをプルダウンにセット
     *
     * @param  {object} instance
     * @return {void}
     * @method
     * @public
     */
    createInstanceSelect (instance)
    {
        const workSpace = Util.$currentWorkSpace();

        const element = document
            .getElementById("instance-type-name");

        while (element.children.length) {
            element.children[0].remove();
        }

        // アイコンを登録
        const i = document.createElement("i");
        i.setAttribute("class", `library-type-${instance.type}`);
        element.appendChild(i);

        const select = document.createElement("select");
        select.classList.add("instance-select");

        select.addEventListener("change", (event) =>
        {
            const activeTool = Util.$tools.activeTool;
            if (activeTool) {
                event.displayObject = true;
                activeTool.dispatchEvent(
                    EventType.CHANGE,
                    event
                );
            }
        });

        // Show only the selected option initially (lazy-load rest on interaction)
        const selectedOption = document.createElement("option");
        selectedOption.value = instance.id;
        let selectedPath = instance.name;
        if (instance._$folderId) {
            let parent = instance;
            while (parent._$folderId) {
                parent = workSpace.getLibrary(parent._$folderId);
                selectedPath = `${parent.name}/${selectedPath}`;
            }
        }
        selectedOption.textContent = selectedPath;
        selectedOption.defaultSelected = true;
        select.appendChild(selectedOption);

        // Populate all options lazily on first interaction
        let populated = false;
        const populateOptions = () => {
            if (populated) return;
            populated = true;

            // Remove placeholder
            select.textContent = "";

            for (const value of workSpace._$libraries.values()) {
                if (!value.id) continue;
                switch (value.type) {
                    case InstanceType.FOLDER:
                    case InstanceType.SOUND:
                        continue;
                    default:
                        break;
                }

                const option = document.createElement("option");
                option.value = value.id;
                let path = value.name;
                if (value._$folderId) {
                    let parent = value;
                    while (parent._$folderId) {
                        parent = workSpace.getLibrary(parent._$folderId);
                        path = `${parent.name}/${path}`;
                    }
                }
                option.textContent = path;
                if (value.id === instance.id) {
                    option.defaultSelected = true;
                }
                select.appendChild(option);
            }
        };
        select.addEventListener("mousedown", populateOptions, { once: true });
        select.addEventListener("focus", populateOptions, { once: true });

        // DOMに登録
        element.appendChild(select);
    }
}

Util.$instanceSelectController = new InstanceSelectController();

