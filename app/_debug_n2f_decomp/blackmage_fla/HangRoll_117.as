package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class HangRoll_117 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function HangRoll_117() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(8, frame_9);
            addFrameScript(18, frame_19);
            addFrameScript(19, frame_20);
            addFrameScript(24, frame_25);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            if (SSF2API.isReady())
                        {
                            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        };
                        if (parent && SSF2API.isReady())
                        {
                            this.self.setIntangibility(true);
                        };
        }
        internal function frame_3():* {
            this.self.playSound("bm_doublejump");
        }
        internal function frame_9():* {
            this.self.playSound("run_start");
        }
        internal function frame_19():* {
            this.self.setIntangibility(false);
        }
        internal function frame_20():* {
            this.self.playSound("blackmage_landLight");
        }
        internal function frame_25():* {
            this.self.endAttack();
        }
    }
}
