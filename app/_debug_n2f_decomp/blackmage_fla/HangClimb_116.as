package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class HangClimb_116 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function HangClimb_116() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(15, frame_16);
            addFrameScript(16, frame_17);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady())
                        {
                            this.self.setIntangibility(true);
                        };
        }
        internal function frame_3():* {
            this.self.playSound("bm_doublejump");
        }
        internal function frame_9():* {
            this.self.setXSpeed(4.5, false);
        }
        internal function frame_11():* {
            this.self.playSound("blackmage_landLight");
        }
        internal function frame_16():* {
            this.self.setIntangibility(false);
        }
        internal function frame_17():* {
            this.self.endAttack();
        }
    }
}
