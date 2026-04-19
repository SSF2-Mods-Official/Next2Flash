package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class HangAttack_118 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function HangAttack_118() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(11, frame_12);
            addFrameScript(12, frame_13);
            addFrameScript(24, frame_25);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
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
        internal function frame_10():* {
            this.self.playSound("run_start");
        }
        internal function frame_11():* {
            this.self.setXSpeed(8, false);
        }
        internal function frame_12():* {
            this.self.playAttackSound(1);
                        this.self.attachEffect("global_dust_light");
        }
        internal function frame_13():* {
            this.self.setIntangibility(false);
        }
        internal function frame_25():* {
            this.self.endAttack();
        }
    }
}
