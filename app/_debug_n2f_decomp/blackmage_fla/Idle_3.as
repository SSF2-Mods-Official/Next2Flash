package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Idle_3 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var used:Boolean;
        public var rand:int;
        public var repeats:int;
        public function Idle_3() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(11, frame_12);
            addFrameScript(35, frame_36);
            addFrameScript(65, frame_66);
            addFrameScript(69, frame_70);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var used:Boolean;
            var rand:int;
            var repeats:int;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.used = false;
                        this.rand = 0;
                        if (!this.repeats)
                        {
                            this.repeats = 0;
                        };
                        if (parent && SSF2API.isReady() && this.self)
                        {
                            this.rand = (100 * SSF2API.random());
                            if (this.rand >= 95)
                            {
                                this.gotoAndStop("bored");
                            }
                            else if (this.rand >= 85)
                            {
                                this.gotoAndStop("blink");
                            };
                        };
                        if (SSF2API.isReady() && this.self)
                        {
                            this.restoreSpecials();
                        };
                        if (this.self && SSF2API.isReady() && (!this.self.hasEventListener(SSF2Event.STATE_CHANGE, this.uncrouch)))
                        {
                            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.uncrouch);
                        };
        }
        internal function frame_12():* {
            this.repeats++;
                        this.gotoAndStop("loop");
        }
        internal function frame_36():* {
            this.repeats++;
                        this.gotoAndStop("loop");
        }
        internal function frame_66():* {
            this.gotoAndStop("loop");
        }
        internal function frame_70():* {
            gotoAndStop("loop");
        }
    }
}
