package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class Sleep_124 extends MovieClip {
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function Sleep_124() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(19, frame_20);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (parent && SSF2API.isReady())
                        {
                            this.self.attachEffect("BM_Zz", {
                                "x":this.self.flipX(10),
                                "y":-26
                            });
                            this.self.setGlobalVariable("jab", false);
                            this.self.clearEffectsOnStateChange();
                        };
                        if (parent && SSF2API.isReady() && this.self)
                        {
                            this.self.playSound("fall_asleep");
                        };
        }
        internal function frame_20():* {
            this.self.stancePlayFrame("again");
        }
    }
}
