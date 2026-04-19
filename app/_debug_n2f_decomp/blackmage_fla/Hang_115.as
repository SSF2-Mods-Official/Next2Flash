package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Hang_115 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Hang_115() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(44, frame_45);
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
                            this.self.setAttackEnabled(true, "b_forward");
                            this.self.setAttackEnabled(true, "b_forward_air");
                        };
        }
        internal function frame_2():* {
            this.self.attachEffect("ledgeGrab_gfx", {
                            "x":this.self.flipX(0),
                            "y":0,
                            "scaleX":-0.4,
                            "scaleY":-0.4
                        });
        }
        internal function frame_45():* {
            this.self.stancePlayFrame("loop");
        }
    }
}
