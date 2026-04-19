package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Taunts_130 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Taunts_130() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(40, frame_41);
            addFrameScript(44, frame_45);
            addFrameScript(90, frame_91);
            addFrameScript(101, frame_102);
            addFrameScript(166, frame_167);
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
        }
        internal function frame_5():* {
            if (!this.self.getMetalStatus())
                        {
                            this.self.playSound("bmtaunt3", true);
                        };
        }
        internal function frame_41():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_s");
                        };
        }
        internal function frame_45():* {
            this.self.endAttack();
        }
        internal function frame_91():* {
            this.self.endAttack();
        }
        internal function frame_102():* {
            if (!this.self.getMetalStatus())
                        {
                            this.self.playSound("bm_taunt3", true);
                        };
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("bm_taunt3_metal");
                        };
        }
        internal function frame_167():* {
            this.self.endAttack();
        }
    }
}
