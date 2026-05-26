/**
 * @class
 * @extends {BaseTimeline}
 * @memberOf view.timeline
 */
class TimelinePlayer extends BaseTimeline
{
    /**
     * @constructor
     * @public
     */
    constructor ()
    {
        super();

        /**
         * @type {boolean}
         * @default true
         * @private
         */
        this._$stopFlag = true;

        /**
         * @type {boolean}
         * @default false
         * @private
         */
        this._$repeat = false;

        /**
         * @type {number}
         * @default 0
         * @private
         */
        this._$totalFrame = 0;

        /**
         * @type {number}
         * @default 0
         * @private
         */
        this._$startTime = 0;

        /**
         * @type {number}
         * @default 0
         * @private
         */
        this._$fps = 0;

        /**
         * @type {number}
         * @default -1
         * @private
         */
        this._$timerId = -1;

        /**
         * @type {number}
         * @default 0
         * @private
         */
        this._$baseOffsetHalfWidth = 0;

        /**
         * @type {array}
         * @private
         */
        this._$sounds = [];

        /**
         * @type {number}
         * @default 0
         * @private
         */
        this._$clientWidth = 0;

        /**
         * @type {function}
         * @description null
         * @private
         */
        this._$run = null;

        /**
         * @type {boolean}
         * @default false
         * @private
         */
        this._$rendering = false;
    }

    /**
     * @description リピート設定を返す
     *
     * @return {boolean}
     * @readonly
     * @public
     */
    get repeat ()
    {
        return this._$repeat;
    }

    /**
     * @description 再生フラグを返す
     *
     * @return {boolean}
     * @readonly
     * @public
     */
    get stopFlag ()
    {
        return this._$stopFlag;
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
        super.initialize();

        const elementIds = [
            "timeline-play",
            "timeline-stop",
            "timeline-repeat",
            "timeline-no-repeat"
        ];

        for (let idx = 0; idx < elementIds.length; ++idx) {

            const id = elementIds[idx];

            const element = document.getElementById(id);
            if (!element) {
                continue;
            }

            // ストップとリピートアイコンは初期は非表示
            switch (id) {

                case "timeline-stop":
                case "timeline-repeat":
                    element.style.display = "none";
                    break;

                default:
                    break;

            }

            // eslint-disable-next-line no-loop-func
            element.addEventListener("mousedown", (event) =>
            {
                console.log('[PlayDbg] Button mousedown:', id,
                    'display:', element.style.display,
                    'target:', event.target.id,
                    'stopFlag:', this._$stopFlag,
                    'rendering:', this._$rendering);

                // 親のイベント中止
                event.stopPropagation();

                // id名で関数を実行
                this.executeFunction(event);

                // 全てのメニューを終了する
                Util.$endMenu();
            });
        }

        // 毎フレームの再生関数を変数にセット
        this._$run = this.run.bind(this);
    }

    /**
     * @description タイムラインのプレイヤーを再生する
     *
     * @return {void}
     * @method
     * @public
     */
    executeTimelinePlay ()
    {
        console.log('[PlayDbg] executeTimelinePlay called — stopFlag:', this._$stopFlag,
            'rendering:', this._$rendering, 'timerId:', this._$timerId,
            'frame:', Util.$timelineFrame.currentFrame);

        if (this._$stopFlag) {

            if ("next2d" in window) {
                Util.$root.stage._$player._$loadWebAudio();
            }

            const scene = Util.$currentWorkSpace().scene;

            // アクティブな再生範囲を取得(空のフレームは含めない)
            this._$totalFrame = scene.totalFrame;

            // 1フレーム以上あるタイムラインが再生対象
            if (this._$totalFrame > 1) {

                // サウンド設定を初期化
                Util.$soundController.clear();

                // Reset rendering flag from any prior stuck state
                this._$rendering = false;

                this._$stopFlag = false;

                // 先に起動しているタイマーがあれば停止する
                if (this._$timerId > -1) {
                    window.cancelAnimationFrame(this._$timerId);
                }

                /**
                 * @type {ArrowTool}
                 */
                const tool = Util.$tools.getDefaultTool("arrow");
                tool.clear();

                // 再生位置の補正
                let frame = Util.$timelineFrame.currentFrame;
                if (frame >= this._$totalFrame) {

                    Util.$timelineFrame.currentFrame = 1;

                    // スクロールしていれば左端にセット
                    Util.$timelineHeader.scrollX = 0;

                    // タイムラインを再構成
                    Util.$timelineHeader.rebuild();
                    Util.$timelineLayer.moveTimeLine();

                    // マーカーを移動
                    Util.$timelineMarker.move();
                }

                scene.startSound(Util.$timelineFrame.currentFrame);

                // 再生ボタンを非表示
                document
                    .getElementById("timeline-play")
                    .style.display = "none";

                // 停止ボタンを表示
                document
                    .getElementById("timeline-stop")
                    .style.display = "";

                // 現在のタイムラインの幅をキャッシュ
                const element = document
                    .getElementById("timeline-controller-base");

                this._$baseOffsetHalfWidth = element.offsetWidth / 2;
                this._$clientWidth = element.clientWidth;

                const _rawFps = document.getElementById("stage-fps").value | 0;
                this._$fps = 1000 / (_rawFps || 24);

                // Extended pre-warm: render first N frames to populate
                // shape buffers and container caches so the initial heavy
                // frames don't freeze the screen during real playback.
                this._$rendering = true;
                var self = this;
                var _warmStart = Util.$timelineFrame.currentFrame;
                var _warmEnd = Math.min(self._$totalFrame, 120);
                var _warmT0 = performance.now();
                var _scene = Util.$currentWorkSpace().scene;

                function _prewarmNext(f) {
                    if (f > _warmEnd || self._$stopFlag) {
                        // Done — clear any sounds triggered during pre-warm,
                        // reset to start frame, and do a final proper render.
                        Util.$soundController.clear();
                        Util.$timelineFrame.currentFrame = _warmStart;
                        _scene.startSound(_warmStart);
                        return Promise.resolve(self.reloadScreen());
                    }
                    Util.$timelineFrame.currentFrame = f;
                    return Promise.resolve(_scene.changeFrame(f)).then(function() {
                        return _prewarmNext(f + 1);
                    });
                }

                _prewarmNext(_warmStart).then(function () {
                    self._$rendering = false;
                    if (self._$stopFlag) return;
                    self._$startTime = window.performance.now();
                    self._$timerId   = window.requestAnimationFrame(self._$run);

                    console.log('[PlayDbg] PLAY started (pre-warmed frames ' +
                        _warmStart + '-' + _warmEnd + ' in ' +
                        (performance.now() - _warmT0).toFixed(0) +
                        'ms) — totalFrame:', self._$totalFrame,
                        'fps interval:', self._$fps.toFixed(1) + 'ms',
                        'startFrame:', Util.$timelineFrame.currentFrame,
                        'timerId:', self._$timerId);
                }, function (err) {
                    console.error('[PlayDbg] Pre-warm failed:', err);
                    self._$rendering = false;
                    if (self._$stopFlag) return;
                    self._$startTime = window.performance.now();
                    self._$timerId   = window.requestAnimationFrame(self._$run);
                });

            } else {
                console.log('[PlayDbg] PLAY skipped — totalFrame <= 1:', this._$totalFrame);
            }

        } else {

            console.log('[PlayDbg] PLAY toggled to STOP (was playing)');
            this.executeTimelineStop();

        }
    }

    /**
     * @description 再生中のサウンドを全て停止する
     *
     * @return {void}
     * @method
     * @public
     */
    stopAllSound ()
    {
        const sounds = [];
        for (let idx = 0; idx < this._$sounds.length; ++idx) {

            const sound = this._$sounds[idx];
            if (sound._$stopFlag) {
                sounds.push(sound);
                continue;
            }

            sound.stop();
        }

        this._$sounds = sounds;

        // 読み込み途中の音声があれば待機して再実行
        if (this._$sounds.length) {
            requestAnimationFrame(() =>
            {
                this.stopAllSound();
            });
        }
    }

    /**
     * @description タイムラインのプレイヤーを停止する
     *
     * @param  {boolean} [reload=true]
     * @return {void}
     * @method
     * @public
     */
    executeTimelineStop (reload = true)
    {
        console.log('[PlayDbg] executeTimelineStop called — stopFlag:', this._$stopFlag,
            'rendering:', this._$rendering, 'timerId:', this._$timerId,
            'frame:', Util.$timelineFrame.currentFrame, 'reload:', reload);

        // タイマーを終了
        window.cancelAnimationFrame(this._$timerId);



        // 再生中のサウンドを全て停止する
        this.stopAllSound();

        // Clear playback DOM cache
        Util.$screen.clearPlaybackCache();

        // 変数を初期化
        this._$stopFlag  = true;
        this._$timerId   = -1;
        this._$rendering = false;

        // 再生ボタンを表示
        const playBtn = document.getElementById("timeline-play");
        const stopBtn = document.getElementById("timeline-stop");
        playBtn.style.display = "";
        stopBtn.style.display = "none";

        console.log('[PlayDbg] STOP done — play btn display:', JSON.stringify(playBtn.style.display),
            'stop btn display:', JSON.stringify(stopBtn.style.display),
            'play btn offsetParent:', !!playBtn.offsetParent,
            'stop btn offsetParent:', !!stopBtn.offsetParent);

        // 再生位置で再描画
        if (reload) {
            this.reloadScreen();
        }
    }

    /**
     * @description タイムラインのプレイヤーの再生が最終フレームにいくと自動的に終了する
     *
     * @return {void}
     * @method
     * @public
     */
    executeTimelineRepeat ()
    {
        document
            .getElementById("timeline-repeat")
            .style.display = "none";

        document
            .getElementById("timeline-no-repeat")
            .style.display = "";

        this._$repeat = false;
    }

    /**
     * @description タイムラインのプレイヤーの再生をリピートする
     *
     * @return {void}
     * @method
     * @public
     */
    executeTimelineNoRepeat ()
    {
        document
            .getElementById("timeline-repeat")
            .style.display = "";

        document
            .getElementById("timeline-no-repeat")
            .style.display = "none";

        this._$repeat = true;
    }



    /**
     * @description 毎フレームの再生処理
     * @param  {number} timestamp
     * @return {void}
     * @method
     * @public
     */
    run (timestamp = 0)
    {
        if (this._$stopFlag) {
            return ;
        }

        // Skip frame if previous render is still in progress
        if (this._$rendering) {
            // Track how long we've been stuck waiting
            if (!this._$renderWaitStart) {
                this._$renderWaitStart = timestamp;
            } else if (timestamp - this._$renderWaitStart > 5000) {
                console.error('[PlayDbg] _$rendering stuck TRUE for 5s! Force-resetting.',
                    'frame:', Util.$timelineFrame.currentFrame);
                this._$rendering = false;
                this._$renderWaitStart = 0;
            }
            this._$timerId = window.requestAnimationFrame(this._$run);
            return;
        }
        this._$renderWaitStart = 0;

        let delta = timestamp - this._$startTime;
        if (delta > this._$fps) {

            // ── Cache pressure relief: trim oversized cacheStore every 30 frames ──
            if (!this._$flushCounter) this._$flushCounter = 0;
            this._$flushCounter++;
            if (this._$flushCounter >= 30) {
                this._$flushCounter = 0;
                try {
                    var player = window.next2d && window.next2d.player;
                    if (player && player.cacheStore && player.cacheStore._$store) {
                        var store = player.cacheStore._$store;
                        if (store.size > 300) {
                            var count = 0;
                            var limit = store.size - 300;
                            for (var _key of store.keys()) {
                                if (count >= limit) break;
                                player.cacheStore.removeCache(_key);
                                count++;
                            }
                        }
                    }
                } catch (e) { /* non-fatal */ }
            }

            let frame = Util.$timelineFrame.currentFrame + 1;
            if (frame > this._$totalFrame) {

                if (!this._$repeat) {
                    console.log('[PlayDbg] Reached end of timeline at frame',
                        frame - 1, '/', this._$totalFrame, '— stopping');
                    return this.executeTimelineStop();
                }

                frame = 1;

                // スクロールしていれば左端にセット
                Util.$timelineHeader.scrollX = 0;
                Util.$timelineLayer.moveTimeLine();
            }

            // フレームを移動
            Util.$timelineFrame.currentFrame = frame;

            const timelineWidth = Util.$timelineTool.timelineWidth;
            const moveFrame     = Util.$timelineHeader.scrollX / timelineWidth | 0;

            // タイムラインの座標修正
            const deltaX = (frame - moveFrame) * (timelineWidth + 1);
            if (0 >= deltaX || deltaX > this._$clientWidth) {
                Util.$timelineHeader.scrollX = (frame - 1) * timelineWidth;
            }

            // Throttle timeline UI to every 5th frame — saves ~20ms/frame
            // of DOM work (rebuild + marker + moveTimeLine)
            if (frame % 5 === 0 || frame === 1) {
                Util.$timelineHeader.rebuild();
                Util.$timelineMarker.move();

                const moveX = (frame - 1) * (Util.$timelineTool.timelineWidth + 1);
                if (moveX > this._$baseOffsetHalfWidth) {
                    Util.$timelineLayer.moveTimeLine();
                }
            }

            // 描画した時間を更新
            this._$startTime = timestamp - delta % this._$fps;

            // Log slow frames and periodic status
            var renderStart = performance.now();
            if (delta > 500) {
                console.warn('[PlayDbg] SLOW delta:', delta.toFixed(0) + 'ms',
                    'at frame', frame, '/', this._$totalFrame);
            }
            if (frame % 10 === 0 || frame === 1) {
                console.log('[PlayDbg] Frame', frame, '/', this._$totalFrame,
                    'delta:', delta.toFixed(0) + 'ms',
                    'heap:', (performance.memory ? (performance.memory.usedJSHeapSize / 1048576).toFixed(0) + 'MB' : 'n/a'));
            }

            // 再描画
            this._$rendering = true;
            var self = this;
            Promise.resolve(this.reloadScreen()).then(function() {
                var renderTime = performance.now() - renderStart;
                self._$rendering = false;
                if (renderTime > 100) {
                    console.warn('[PlayDbg] Slow render:', renderTime.toFixed(0) + 'ms',
                        'frame', Util.$timelineFrame.currentFrame);
                }
            }, function(err) {
                console.error('[PlayDbg] Render FAILED at frame',
                    Util.$timelineFrame.currentFrame, err);
                self._$rendering = false;
            });

        }

        // 描画のタイマーをセット
        this._$timerId = window.requestAnimationFrame(this._$run);
    }

}

Util.$timelinePlayer = new TimelinePlayer();
