package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Walk_14 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Walk_14() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(4, frame_5);
            addFrameScript(13, frame_14);
            addFrameScript(17, frame_18);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }
        internal function frame_5():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s1");
                        }
                        else
                        {
                            this.self.playSound("bm_footstep");
                        };
        }
        internal function frame_14():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s2");
                        }
                        else
                        {
                            this.self.playSound("bm_footstep");
                        };
        }
        internal function frame_18():* {
            this.self.stancePlayFrame("loop");
        }
    }
}
