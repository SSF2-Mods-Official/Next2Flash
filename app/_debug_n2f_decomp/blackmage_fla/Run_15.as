package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Run_15 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Run_15() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(6, frame_7);
            addFrameScript(7, frame_8);
            addFrameScript(11, frame_12);
            addFrameScript(15, frame_16);
            addFrameScript(19, frame_20);
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
                            this.self.playSound("run_start");
                        };
        }
        internal function frame_4():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s2");
                        }
                        else
                        {
                            this.self.playSound("bm_footstep");
                        };
        }
        internal function frame_7():* {
            this.self.stancePlayFrame("run");
        }
        internal function frame_8():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s1");
                        }
                        else
                        {
                            this.self.playSound("bm_footstep");
                        };
        }
        internal function frame_12():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_step_s2");
                        }
                        else
                        {
                            this.self.playSound("bm_footstep");
                        };
        }
        internal function frame_16():* {
            this.self.stancePlayFrame("run");
        }
        internal function frame_20():* {
            if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_s");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landLight");
                        };
        }
    }
}
